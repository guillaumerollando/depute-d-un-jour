"""Étape 3c (METHODE §6, étape 3) : assembler les cartes vérifiées et choisir le paquet final.

Entrées : data/interim/apres_ambiguite.json, data/interim/ia/etape3/, data/interim/ia/etape3_verif/,
          data/interim/sources.json, data/interim/extraits/
Sorties : data/publie/cartes.json (paquet final), data/interim/selection.md (rapport)
"""
import itertools
import re
from collections import Counter

from commun import INTERIM, ORDRE, PRIORITE_TYPE, RACINE, charger_json, ecrire_json

TAILLE_MAX = 80
COUVERTURE_CIBLE = 3
MAX_PAR_THEME = 8
MAX_PAR_DOSSIER = 2
THEMES = [
    "Économie et impôts", "Travail et retraites", "Santé et protection sociale", "Sécurité et justice",
    "Immigration et nationalité", "Environnement et énergie", "Agriculture et alimentation",
    "Institutions et démocratie", "Défense et international", "Société et éthique",
    "Éducation, culture et numérique", "Territoires et outre-mer", "Logement",
]
# Contrôle mécanique : aucun nom de groupe ou de parti sur la carte
NOMS_INTERDITS = re.compile(
    r"\b(LFI|RN|UDR|EPR|MoDem|Horizons|LIOT|GDR|ECOS|insoumis\w*|Rassemblement national|socialiste\w*|"
    r"écologiste\w*|communiste\w*|Renaissance|Républicains|Droite républicaine|macronist\w*)\b", re.IGNORECASE)
# Proposition v0.6 : une carte dont l'objet même désigne un camp politique ne peut pas être neutre
CAMPS_POLITIQUES = re.compile(r"\b(droite|gauche|extr[eê]me[- ](droite|gauche))\b", re.IGNORECASE)
# Proposition v0.6 : un amendement qui ne modifie que l'intitulé d'un texte ne change aucune règle
AMENDEMENT_DE_TITRE = re.compile(r"amendements? .* au titre (du projet|de la proposition)", re.IGNORECASE)
# Une demande de rapport ne change aucune règle : rien à voter pour l'utilisateur
DEMANDE_RAPPORT = re.compile(r"^(Demander|Remettre|Prévoir)\b.*\brapport\b", re.IGNORECASE)
AN = "https://www.assemblee-nationale.fr/dyn/17"
PAIRES = list(itertools.combinations(ORDRE, 2))


def controles_mecaniques(carte):
    pb = []
    if carte["theme"] not in THEMES:
        pb.append(f"thème hors liste : {carte['theme']}")
    if len(carte["titre"]) > 90:
        pb.append(f"titre trop long ({len(carte['titre'])})")
    if len(carte["ce_que_ca_change"]) > 450:
        pb.append(f"résumé trop long ({len(carte['ce_que_ca_change'])})")
    for champ in ("titre", "ce_que_ca_change", "contexte"):
        m = NOMS_INTERDITS.search(carte[champ] or "") or CAMPS_POLITIQUES.search(carte[champ] or "")
        if m:
            pb.append(f"nom de groupe ou de camp politique dans {champ} : « {m.group(0)} »")
    return pb


def cle_egalite(c):
    return (PRIORITE_TYPE[c["type"]], -c["votants"], tuple(-int(x) for x in c["date"].split("-")), c["numero"])


def main():
    candidates = charger_json(INTERIM / "apres_ambiguite.json")
    sources = charger_json(INTERIM / "sources.json")
    cartes, ecartees = [], []
    for c in candidates:
        uid = c["uid"]
        if AMENDEMENT_DE_TITRE.search(c["titre"]):
            ecartees.append((uid, "amendement portant seulement sur l'intitulé du texte"))
            continue
        f_res, f_ver = INTERIM / "ia/etape3" / f"{uid}.json", INTERIM / "ia/etape3_verif" / f"{uid}.json"
        if not f_res.exists() or not f_ver.exists():
            ecartees.append((uid, "résumé ou vérification manquant"))
            continue
        res, ver = charger_json(f_res), charger_json(f_ver)
        lisibilite = (ver.get("corrections") or {}).get("lisibilite") or res.get("lisibilite")
        if lisibilite != "ok":
            ecartees.append((uid, f"lisibilité : {lisibilite} — {res.get('remarque')}"))
            continue
        if ver.get("verdict") not in ("valide", "corrige"):
            ecartees.append((uid, f"vérification : {ver.get('verdict')} — {'; '.join(ver.get('problemes', []))}"))
            continue
        texte = {k: res.get(k) for k in ("theme", "titre", "ce_que_ca_change", "contexte")}
        texte.update({k: v for k, v in (ver.get("corrections") or {}).items() if k in texte})
        # Passe « français clair » : retenue seulement si le contrôle d'équivalence la valide
        f_cla, f_eq = INTERIM / "ia/etape3_clarte" / f"{uid}.json", INTERIM / "ia/etape3_equivalence" / f"{uid}.json"
        if f_cla.exists() and f_eq.exists() and charger_json(f_eq).get("verdict") == "equivalent":
            cla = charger_json(f_cla)
            texte.update({k: cla[k] for k in ("titre", "ce_que_ca_change", "contexte") if cla.get(k)})
        pb = controles_mecaniques(texte)
        if DEMANDE_RAPPORT.search(texte["titre"]):
            pb.append("demande de rapport, sans effet sur les règles")
        if pb:
            ecartees.append((uid, "contrôle mécanique : " + "; ".join(pb)))
            continue
        extrait = charger_json(INTERIM / "extraits" / f"{uid}.json")
        citations = {g: {k: v.get(k) for k in ("orateur", "citation", "categorie")}
                     for g, v in c["ambiguite"].items() if v.get("categorie") in ("A", "B") and v.get("citation")}
        src = sources.get(uid, {})
        cartes.append({
            "uid": uid, "numero": c["numero"], "date": c["date"], "type": c["type"], "votants": c["votants"],
            "socle": c.get("socle", False),
            **texte,
            "resultat": c["sort"],
            "positions": c["positions"],
            "neutralises": c["neutralises"],
            "voix": c["voix"],
            "citations": citations,
            "verification": ver.get("verdict"),
            "dossier": c["dossier"],
            "dossier_titre": c["dossier_titre"],
            "liens": {
                "scrutin": f"{AN}/scrutins/{c['numero']}",
                "dossier": f"{AN}/dossiers/{c['dossier']}",
                "texte": src.get("url"),
                "compte_rendu": f"{AN}/comptes-rendus/seance/{extrait['compte_rendu']}" if extrait.get("compte_rendu") else None,
            },
        })

    # Entrée de la consigne « sujets » : les cartes publiables
    ecrire_json(INTERIM / "sujets_entree.json",
                [{k: c[k] for k in ("uid", "titre", "ce_que_ca_change", "dossier")} for c in cartes])
    f_sujets = INTERIM / "ia/sujets.json"
    sujets = charger_json(f_sujets)["sujets"] if f_sujets.exists() else {}
    if not sujets:
        print("Attention : pas de regroupement par sujet (data/interim/ia/sujets.json absent)")

    couverture, par_theme, par_dossier, sujets_pris, choisis = Counter(), Counter(), Counter(), set(), []
    paires = {c["uid"]: {(a, b) for a, b in PAIRES if a in c["positions"] and b in c["positions"]
                         and c["positions"][a] != c["positions"][b]} for c in cartes}

    def prendre(c):
        choisis.append(c)
        par_theme[c["theme"]] += 1
        par_dossier[c["dossier"]] += 1
        sujets_pris.add(sujets.get(c["uid"], c["uid"]))
        for p in paires[c["uid"]]:
            couverture[p] += 1

    # 1. Socle : les votes solennels, désignés comme majeurs par l'Assemblée elle-même
    for c in sorted((c for c in cartes if c["socle"]), key=cle_egalite):
        if sujets.get(c["uid"], c["uid"]) not in sujets_pris:
            prendre(c)

    # 2. Complément glouton déterministe : départager les paires encore peu couvertes
    restants = sorted((c for c in cartes if c not in choisis), key=cle_egalite)
    cible = COUVERTURE_CIBLE
    while len(choisis) < TAILLE_MAX:
        meilleur, gain_max = None, 0
        for c in restants:
            if (par_theme[c["theme"]] >= MAX_PAR_THEME or par_dossier[c["dossier"]] >= MAX_PAR_DOSSIER
                    or sujets.get(c["uid"], c["uid"]) in sujets_pris):
                continue
            gain = sum(1 for p in paires[c["uid"]] if couverture[p] < cible)
            if gain > gain_max:
                meilleur, gain_max = c, gain
        if not meilleur:
            if cible >= 10 * COUVERTURE_CIBLE:
                break
            cible += COUVERTURE_CIBLE  # toutes les paires atteignent la cible : palier suivant
            continue
        restants.remove(meilleur)
        prendre(meilleur)

    ecrire_json(RACINE / "data/publie/cartes.json", choisis)
    lignes = ["# Paquet final — étape 3", "",
              f"- Cartes candidates : {len(candidates)} ; publiables : {len(cartes)} ; retenues : {len(choisis)} (dont socle : {sum(c['socle'] for c in choisis)})",
              f"- Thèmes : {dict(Counter(c['theme'] for c in choisis))}",
              f"- Types : {dict(Counter(c['type'] for c in choisis))}",
              f"- Paire la moins départagée : {min(couverture[p] for p in PAIRES)} fois", "",
              "## Cartes retenues", ""]
    for i, c in enumerate(choisis, 1):
        pour = " ".join(g for g in ORDRE if c["positions"].get(g) == "pour")
        contre = " ".join(g for g in ORDRE if c["positions"].get(g) == "contre")
        lignes += [f"{i}. **{c['titre']}** — {c['theme']} · {c['type']} · {c['date']}",
                   f"   - {c['ce_que_ca_change']}",
                   f"   - Pour : {pour} · Contre : {contre}" + (f" · Neutralisés : {', '.join(c['neutralises'])}" if c['neutralises'] else "")]
    lignes += ["", "## Cartes écartées", ""] + [f"- {u} : {r}" for u, r in ecartees]
    (INTERIM / "selection.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"Publiables : {len(cartes)} · retenues : {len(choisis)} · écartées : {len(ecartees)}")
    print("Thèmes :", dict(Counter(c["theme"] for c in choisis)))
    print("Paires les moins couvertes :", sorted((couverture[p], p) for p in PAIRES)[:5])


if __name__ == "__main__":
    main()
