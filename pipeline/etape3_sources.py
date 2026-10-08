"""Étape 3a (METHODE §7) : récupérer le texte officiel débattu pour chaque carte.

Choix du document, sans interprétation :
- amendement : le texte amendé (`texteLegislatifRef` de l'amendement) ;
- article : le texte amendé lors de la même séance, sinon comme pour un texte entier ;
- texte entier, partie, résolution : le dernier texte de l'Assemblée déposé avant le vote,
  de préférence le texte de la commission, sinon le texte initial.

Sorties : data/interim/textes/<document>.txt, data/interim/sources.json
"""
import glob
import re
import subprocess
import tempfile
import time
import urllib.request
from collections import defaultdict
from html import unescape

from commun import INTERIM, RAW, charger_json, ecrire_json

BASE = "https://www.assemblee-nationale.fr/dyn/17/textes/"


def url_document(uid):
    m = re.match(r"(PION|PRJL|PNRE)ANR5L17(BTC|BTA|B)(\d+)$", uid)
    if not m:
        return None
    nature, forme, num = m.groups()
    num = f"{int(num):04d}"
    if forme == "BTC":
        return f"{BASE}l17b{num}_texte-adopte-commission"
    if forme == "BTA":
        return f"{BASE}l17t{num}_texte-adopte-seance"
    suffixe = {"PRJL": "projet-loi", "PION": "proposition-loi", "PNRE": "proposition-resolution"}[nature]
    return f"{BASE}l17b{num}_{suffixe}"


def telecharger(adresse, format_):
    for essai in range(3):
        try:
            req = urllib.request.Request(adresse, headers={"User-Agent": "depute-d-un-jour (pipeline open source)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                brut = r.read()
            if format_ == "html":
                return texte_html(brut.decode("utf-8", "replace"))
            with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
                f.write(brut)
                f.flush()
                return subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True).stdout
        except Exception as e:
            if "404" in str(e):
                return None
            time.sleep(5 * (essai + 1))  # serveur saturé : on patiente
    return None


def texte_valide(texte):
    """Une page d'erreur du serveur n'est pas un texte de loi."""
    return len(texte) > 600 and "ASSEMBLÉE NATIONALE" in texte.upper() and "<?php" not in texte


def texte_html(html):
    corps = re.sub(r"(?s)<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", html)
    corps = re.sub(r"<br\s*/?>|</p>|</h\d>|</li>", "\n", corps)
    corps = unescape(re.sub(r"<[^>]+>", " ", corps))
    lignes = [" ".join(l.split()) for l in corps.splitlines()]
    return "\n".join(l for l in lignes if l)


def main():
    preselection = charger_json(INTERIM / "apres_ambiguite.json")
    docs_par_dossier = defaultdict(list)
    for f in glob.glob(str(RAW / "dossiers/json/document/*.json")):
        d = charger_json(f)["document"]
        if d.get("dossierRef") and re.match(r"(PION|PRJL|PNRE)ANR5L17", d["uid"]):
            chrono = (d.get("cycleDeVie") or {}).get("chrono") or {}
            # Les textes adoptés n'ont pas de date de dépôt : leur date de création est celle du vote
            date = chrono.get("dateDepot") or chrono.get("dateCreation") or ""
            docs_par_dossier[d["dossierRef"]].append((date[:10], d["uid"]))
    scrutins = {s["uid"]: s for s in charger_json(INTERIM / "scrutins.json")}
    texte_par_seance = defaultdict(set)
    for s in scrutins.values():
        if s.get("amendement") and s["amendement"].get("texte"):
            texte_par_seance[(s["seance"], s["dossier"])].add(s["amendement"]["texte"])

    sources, telecharges = {}, 0
    dossier_txt = INTERIM / "textes"
    dossier_txt.mkdir(parents=True, exist_ok=True)
    for c in preselection:
        doc = None
        if c["type"] == "amendement" and c.get("amendement"):
            doc = c["amendement"].get("texte")
        if not doc and c["type"] == "article":
            candidats = texte_par_seance.get((c["seance"], c["dossier"]))
            if candidats and len(candidats) == 1:
                doc = next(iter(candidats))
        vote_de_texte = c["type"] in ("ensemble", "partie", "resolution") or "article unique" in c["titre"]
        if not doc and vote_de_texte and c["sort"] == "adopté":
            # Texte adopté par l'Assemblée le jour du vote : c'est exactement la version votée
            adoptes = sorted(u for d, u in docs_par_dossier.get(c["dossier"], []) if "BTA" in u and d == c["date"])
            doc = adoptes[0] if len(adoptes) == 1 else None
        if not doc:
            avant = sorted(x for x in docs_par_dossier.get(c["dossier"], []) if x[0] <= c["date"] and "BTA" not in x[1])
            commission = [u for _, u in avant if "BTC" in u]
            doc = commission[-1] if commission else (avant[-1][1] if avant else None)
        lecture = url_document(doc) if doc else None
        url = f"https://www.assemblee-nationale.fr/dyn/opendata/{doc}.html" if doc else None
        sources[c["uid"]] = {"document": doc, "url": lecture, "url_source": url}
        if not url:
            continue
        chemin = dossier_txt / f"{doc}.txt"
        if chemin.exists() and texte_valide(chemin.read_text(encoding="utf-8")):
            continue
        # Trois formats officiels, dans l'ordre : page open data, version brute, PDF converti en texte
        essais = [(url, "html"), (f"https://www.assemblee-nationale.fr/dyn/docs/{doc}.raw", "html")]
        if lecture:
            essais.append((lecture + ".pdf", "pdf"))
        for adresse, format_ in essais:
            contenu = telecharger(adresse, format_)
            time.sleep(2)  # politesse envers le serveur
            if contenu and texte_valide(contenu):
                chemin.write_text(contenu, encoding="utf-8")
                telecharges += 1
                sources[c["uid"]].pop("erreur", None)
                break
        else:
            sources[c["uid"]]["erreur"] = "texte introuvable dans les trois formats"
    ecrire_json(INTERIM / "sources.json", sources)
    sans = [u for u, s in sources.items() if not s["url_source"] or s.get("erreur")]
    print(f"Cartes : {len(sources)} · documents téléchargés : {telecharges} · sans texte : {len(sans)}")
    for u in sans[:10]:
        print("  ", u, sources[u])


if __name__ == "__main__":
    main()
