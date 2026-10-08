"""Étape 1 (METHODE §6) : présélection gloutonne sur les votes seuls, sans IA.

Entrée : data/interim/scrutins.json
Sorties : data/interim/preselection.json, data/interim/preselection.md
"""
import itertools
import re
from collections import Counter, defaultdict

from commun import (INTERIM, MIN_GROUPES_POSITIONNES, MIN_VOTANTS, MIN_VOTANTS_DETAIL, ORDRE, PRIORITE_TYPE,
                    TYPES_ELIGIBLES, charger_json, ecrire_json)

TAILLE_MAX = 150
COUVERTURE_CIBLE = 8
MAX_PAR_DOSSIER = 2
MAX_ENSEMBLE_PAR_DOSSIER = 1

PAIRES = list(itertools.combinations(ORDRE, 2))


def paires_departagees(positions):
    return {(a, b) for a, b in PAIRES if a in positions and b in positions and positions[a] != positions[b]}


def eligible(s):
    pos = s["positions"]
    return (
        s["type"] in TYPES_ELIGIBLES
        and s["dossier"]
        and s["votants"] >= MIN_VOTANTS
        and len(pos) >= MIN_GROUPES_POSITIONNES
        and "pour" in pos.values() and "contre" in pos.values()
        and (s["type"] != "amendement" or s["amendement"])
        and not re.match(r"(le|les) sous-amendements?", s["titre"].lower())
        and (s["type"] not in ("amendement", "article") or s["votants"] >= MIN_VOTANTS_DETAIL)
    )


def cle_egalite(s):
    """Ordre de départage fixe : type, votants (desc), date (desc), identifiant."""
    return (PRIORITE_TYPE[s["type"]], -s["votants"], tuple(-int(x) for x in s["date"].split("-")), s["numero"])


def regrouper_lectures(candidats):
    """METHODE §3 : un seul vote « ensemble » par dossier, celui de la dernière lecture."""
    par_dossier = defaultdict(list)
    autres = []
    for s in candidats:
        (par_dossier[s["dossier"]] if s["type"] == "ensemble" else autres).append(s)
    garde = []
    for lectures in par_dossier.values():
        lectures.sort(key=lambda s: (s["date"], s["numero"]))
        derniere = dict(lectures[-1])
        changements = {
            g: [l["positions"].get(g) for l in lectures]
            for g in ORDRE
            if len({l["positions"].get(g) for l in lectures if l["positions"].get(g)}) > 1
        }
        derniere["lectures"] = [l["uid"] for l in lectures]
        derniere["changements_position"] = changements
        garde.append(derniere)
    return garde + autres


def selection_gloutonne(candidats, cible, taille_max):
    couverture = Counter()
    par_dossier, ensemble_dossier = Counter(), Counter()
    choisis = []
    restants = sorted(candidats, key=cle_egalite)
    gain_paires = {s["uid"]: paires_departagees(s["positions"]) for s in restants}
    while len(choisis) < taille_max:
        meilleur, meilleur_gain = None, 0
        for s in restants:
            if par_dossier[s["dossier"]] >= MAX_PAR_DOSSIER:
                continue
            if s["type"] == "ensemble" and ensemble_dossier[s["dossier"]] >= MAX_ENSEMBLE_PAR_DOSSIER:
                continue
            gain = sum(1 for p in gain_paires[s["uid"]] if couverture[p] < cible)
            if gain > meilleur_gain:  # strict : à gain égal, le premier dans l'ordre fixe gagne
                meilleur, meilleur_gain = s, gain
        if not meilleur:
            # Toutes les paires ont atteint la cible : on relève la cible d'un palier
            if cible >= 10 * COUVERTURE_CIBLE:
                break
            cible += COUVERTURE_CIBLE
            continue
        choisis.append(meilleur)
        restants.remove(meilleur)
        par_dossier[meilleur["dossier"]] += 1
        if meilleur["type"] == "ensemble":
            ensemble_dossier[meilleur["dossier"]] += 1
        for p in gain_paires[meilleur["uid"]]:
            couverture[p] += 1
    return choisis, couverture


def socle_solennel(scrutins):
    """METHODE §6 : les votes solennels sur un texte, désignés comme majeurs par l'Assemblée elle-même.
    Un par dossier (dernière lecture), s'il départage au moins une paire de groupes."""
    par_dossier = defaultdict(list)
    for s in scrutins:
        if s["solennel"] and s["type"] in ("ensemble", "partie", "article", "resolution") and s["dossier"]:
            par_dossier[s["dossier"]].append(s)
    socle = []
    for lectures in par_dossier.values():
        derniere = sorted(lectures, key=lambda s: (s["date"], s["numero"]))[-1]
        if paires_departagees(derniere["positions"]):
            socle.append({**derniere, "socle": True})
    return socle


def main():
    scrutins = charger_json(INTERIM / "scrutins.json")
    eligibles = [s for s in scrutins if eligible(s)]
    candidats = regrouper_lectures(eligibles)
    choisis, couverture = selection_gloutonne(candidats, COUVERTURE_CIBLE, TAILLE_MAX)
    deja = {s["uid"] for s in choisis}
    for s in choisis:
        s["socle"] = False
    socle = socle_solennel(scrutins)
    for s in socle:
        if s["uid"] in deja:
            next(c for c in choisis if c["uid"] == s["uid"])["socle"] = True
        else:
            choisis.append(s)
    ecrire_json(INTERIM / "preselection.json", choisis)

    lignes = [
        "# Présélection — étape 1 (votes seuls)", "",
        f"- Scrutins : {len(scrutins)} ; éligibles : {len(eligibles)} ; après regroupement des lectures : {len(candidats)}",
        f"- Cartes présélectionnées : {len(choisis)} (cible relevée par paliers de {COUVERTURE_CIBLE})",
        f"- Types : {dict(Counter(s['type'] for s in choisis))}", "",
        "## Couverture des paires", "",
        "| | " + " | ".join(ORDRE) + " |", "|---" * (len(ORDRE) + 1) + "|",
    ]
    for a in ORDRE:
        cases = []
        for b in ORDRE:
            if a == b:
                cases.append("—")
            else:
                k = (a, b) if ORDRE.index(a) < ORDRE.index(b) else (b, a)
                cases.append(str(couverture[k]))
        lignes.append(f"| **{a}** | " + " | ".join(cases) + " |")
    lignes += ["", "## Cartes", ""]
    for i, s in enumerate(choisis, 1):
        pour = " ".join(g for g in ORDRE if s["positions"].get(g) == "pour")
        contre = " ".join(g for g in ORDRE if s["positions"].get(g) == "contre")
        lignes.append(f"{i}. **[{s['type']}]** {s['date']} — {s['titre']}")
        lignes.append(f"   - Dossier : {s['dossier_titre']} · {s['votants']} votants · {s['sort']}")
        lignes.append(f"   - Pour : {pour or '—'} · Contre : {contre or '—'}")
        if s.get("changements_position"):
            lignes.append(f"   - Changement de position entre lectures : {', '.join(s['changements_position'])}")
    (INTERIM / "preselection.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")

    print(f"Éligibles : {len(eligibles)} · candidats : {len(candidats)} · présélection : {len(choisis)}")
    print("Types :", dict(Counter(s["type"] for s in choisis)))
    faibles = sorted((couverture[p], p) for p in PAIRES)[:8]
    print("Paires les moins couvertes :", ", ".join(f"{a}-{b}:{n}" for n, (a, b) in faibles))


if __name__ == "__main__":
    main()
