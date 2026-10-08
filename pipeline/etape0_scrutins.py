"""Étape 0 : normaliser les scrutins, calculer les positions de groupe, rattacher au dossier.

Sortie : data/interim/scrutins.json
"""
import difflib
import glob
import re
from html import unescape
from pathlib import Path
from collections import Counter

from commun import (ALIAS, COHESION, GROUPES, INTERIM, MIN_EXPRIMES, RAW, categorie,
                    charger_json, ecrire_json, normaliser)


def positions(scrutin):
    """METHODE §2 : abstentions ignorées dans le calcul, position si >= 80 % des voix pour+contre,
    et seulement si les voix pour+contre dépassent les abstentions."""
    pos, voix = {}, {}
    for g in scrutin["ventilationVotes"]["organe"]["groupes"]["groupe"]:
        nom = GROUPES.get(ALIAS.get(g["organeRef"], g["organeRef"]))
        if not nom:
            continue
        d = g["vote"]["decompteVoix"]
        p, c, a = int(d["pour"]), int(d["contre"]), int(d["abstentions"])
        voix[nom] = {"pour": p, "contre": c, "abstention": a}
        if p + c < MIN_EXPRIMES or p + c <= a:
            continue  # trop peu de voix exprimées, ou groupe majoritairement abstentionniste
        if p / (p + c) >= COHESION:
            pos[nom] = "pour"
        elif c / (p + c) >= COHESION:
            pos[nom] = "contre"
    return pos, voix


def titre_loi(titre):
    m = re.search(r"((?:projet|proposition) de (?:loi|résolution)[^()]*)", titre)
    return normaliser(m.group(1)) if m else None


def index_titres():
    """Titre normalisé -> dossier, et document -> titre normalisé (sans « proposition de loi »)."""
    idx, titres_textes = {}, {}
    for f in glob.glob(str(RAW / "dossiers/json/document/*.json")):
        d = charger_json(f)["document"]
        titre = (d.get("titres") or {}).get("titrePrincipal")
        if titre:
            titres_textes[d["uid"]] = re.sub(r"^(proposition|projet) de (loi|resolution)( organique)? ", "", normaliser(titre))
        if titre and d.get("dossierRef"):
            idx.setdefault(normaliser(titre), d["dossierRef"])
    return idx, titres_textes


def texte_brut(html):
    if not html:
        return None
    t = re.sub(r"<[^>]+>", " ", html)
    return " ".join(unescape(t).split())


def index_amendements():
    """(séance, numéro) -> amendement : lien exact entre un scrutin et l'amendement voté."""
    idx = {}
    for f in glob.glob(str(RAW / "amendements/json/*/*/*.json")):
        a = charger_json(f)["amendement"]
        seance = a.get("seanceDiscussionRef")
        chiffres = re.sub(r"\D", "", str(a["identification"]["numeroLong"]))
        if not chiffres:
            continue
        num = int(chiffres)
        auteur = a["signataires"]["auteur"]
        corps = a["corps"].get("contenuAuteur") or {}
        div = (a.get("pointeurFragmentTexte") or {}).get("division") or {}
        fiche = {
            "uid": a["uid"],
            "dossier": Path(f).parts[-3],
            "texte": a.get("texteLegislatifRef"),
            "division": div.get("titre") if isinstance(div.get("titre"), str) else None,
            "auteur": unescape(a["signataires"]["libelle"]) if isinstance(a["signataires"].get("libelle"), str)
            else ("Gouvernement" if auteur.get("typeAuteur") == "Gouvernement" else None),
            "auteur_groupe": GROUPES.get(ALIAS.get(auteur.get("groupePolitiqueRef"), auteur.get("groupePolitiqueRef")))
            if isinstance(auteur.get("groupePolitiqueRef"), str) else None,
            "auteur_type": auteur.get("typeAuteur"),
            "dispositif": texte_brut(corps.get("dispositif") if isinstance(corps.get("dispositif"), str) else None),
            "expose": texte_brut(corps.get("exposeSommaire") if isinstance(corps.get("exposeSommaire"), str) else None),
        }
        if isinstance(seance, str):
            idx.setdefault((seance, num), []).append(fiche)
        idx.setdefault((fiche["dossier"], num), []).append(fiche)
    return idx


def choisir_amendement(candidats, titre, titres_textes):
    """Plusieurs textes peuvent avoir un amendement de même numéro dans une même séance :
    on départage par l'auteur cité dans l'intitulé, puis par le titre du texte. Sinon, aucun."""
    if not candidats:
        return None
    if len(candidats) == 1:
        return candidats[0]
    t = normaliser(titre)
    def auteur_cite(f):
        premier = re.split(r",| et ", f["auteur"] or "")[0]
        nom = re.sub(r"^(m|mme|mm|le|la)\s+", "", normaliser(premier))
        return nom and (f" {nom} " in f" {t} ")
    def texte_cite(f):
        tt = titres_textes.get(f["texte"])
        return tt and tt[:60] in t
    for critere in (auteur_cite, texte_cite):
        restants = [f for f in candidats if critere(f)]
        if len(restants) == 1:
            return restants[0]
        if restants:
            candidats = restants
    return None


def main():
    dossiers, vote_refs = {}, {}
    for f in glob.glob(str(RAW / "dossiers/json/dossierParlementaire/*.json")):
        brut = open(f, encoding="utf-8").read()
        d = charger_json(f)["dossierParlementaire"]
        dossiers[d["uid"]] = d["titreDossier"]["titre"]
        for v in set(re.findall(r"VTANR5L17V\d+", brut)):
            vote_refs.setdefault(v, d["uid"])

    amdts = index_amendements()
    idx, titres_textes = index_titres()
    cles = sorted(idx)
    cache = {}

    def par_titre(loi):
        if loi in cache:
            return cache[loi]
        trouve = None
        for k in cles:
            if len(k) >= 30 and (loi.startswith(k) or k.startswith(loi)):
                trouve = idx[k]
                break
        if not trouve:
            proches = difflib.get_close_matches(loi, cles, n=1, cutoff=0.85)
            trouve = idx[proches[0]] if proches else None
        cache[loi] = trouve
        return trouve

    bruts = [charger_json(f)["scrutin"] for f in sorted(glob.glob(str(RAW / "scrutins/json/*.json")))]
    # Titre de loi cité -> dossier, appris des scrutins rattachés officiellement
    appris = {}
    for s in bruts:
        loi = titre_loi(s["titre"])
        ref = (s["objet"].get("dossierLegislatif") or {}).get("dossierRef") or vote_refs.get(s["uid"])
        if loi and ref:
            appris.setdefault(loi, Counter())[ref] += 1

    sortie, methodes = [], Counter()
    for s in bruts:
        pos, voix = positions(s)
        loi = titre_loi(s["titre"])
        num = re.search(r"amendements? (?:de suppression |identiques? )?n[°o]\s*(\d+)", s["titre"])
        amdt = None
        if num:
            amdt = choisir_amendement(amdts.get((s["seanceRef"], int(num.group(1)))), s["titre"], titres_textes)
            ref = (s["objet"].get("dossierLegislatif") or {}).get("dossierRef")
            if not amdt and ref:
                amdt = choisir_amendement(amdts.get((ref, int(num.group(1)))), s["titre"], titres_textes)
        dossier, methode = None, None
        if s["objet"].get("dossierLegislatif"):
            dossier, methode = s["objet"]["dossierLegislatif"]["dossierRef"], "officiel"
        elif amdt and amdt["dossier"].startswith("DLR"):
            dossier, methode = amdt["dossier"], "amendement"
        elif s["uid"] in vote_refs:
            dossier, methode = vote_refs[s["uid"]], "voteRefs"
        elif loi and loi in appris:
            dossier, methode = appris[loi].most_common(1)[0][0], "titre_scrutin"
        elif loi:
            dossier = par_titre(loi)
            methode = "titre" if dossier else None
        methodes[methode] += 1
        art = re.search(r"(?:à |de )?l.article ([^ ]+(?: (?:bis|ter|quater|quinquies|sexies|septies|octies|nonies|decies)\b)?)", s["titre"])
        sortie.append({
            "uid": s["uid"],
            "numero": int(s["numero"]),
            "date": s["dateScrutin"],
            "titre": s["titre"],
            "type": categorie(s["titre"]),
            "votants": int(s["syntheseVote"]["nombreVotants"]),
            "sort": s["sort"]["code"],
            "solennel": s["typeVote"]["codeTypeVote"] == "SPS",
            "positions": pos,
            "voix": voix,
            "dossier": dossier,
            "dossier_titre": dossiers.get(dossier),
            "rattachement": methode,
            "titre_loi": loi,
            "seance": s["seanceRef"],
            "amendement_numero": int(num.group(1)) if num else None,
            "amendement": amdt,
            "article": art.group(1) if art else None,
        })

    ecrire_json(INTERIM / "scrutins.json", sortie)
    print(f"{len(sortie)} scrutins écrits")
    print("Rattachement :", dict(methodes))
    print("Types :", dict(Counter(x["type"] for x in sortie)))
    sans = Counter(x["titre_loi"][:90] for x in sortie if not x["dossier"] and x["titre_loi"])
    print("Non rattachés (titres les plus fréquents) :")
    for t, n in sans.most_common(6):
        print(f"  {n:4} {t}")


if __name__ == "__main__":
    main()
