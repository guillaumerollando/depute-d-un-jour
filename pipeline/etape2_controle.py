"""Étape 2b (METHODE §4) : contrôler les classements IA puis neutraliser les groupes ambigus.

Contrôles automatiques, sans IA :
- chaque groupe de `positions` a une entrée, et seulement eux ;
- toute catégorie A ou B s'appuie sur une citation présente mot pour mot dans l'extrait,
  et prononcée par un membre du groupe ; sinon la catégorie retombe à C.

Entrées : data/interim/extraits/<uid>.json, data/interim/ia/etape2/<uid>.json
Sorties : data/interim/apres_ambiguite.json, data/interim/ambiguite.md
"""
import itertools
import re
import unicodedata
from collections import Counter

from commun import INTERIM, ORDRE, charger_json, ecrire_json


def canon(t):
    t = unicodedata.normalize("NFKC", t or "")
    t = t.replace("’", "'").replace("‘", "'").replace("«", '"').replace("»", '"').replace("…", "...")
    t = t.replace(" ", " ").replace(" ", " ")
    return " ".join(t.split()).lower()


def main():
    preselection = charger_json(INTERIM / "preselection.json")
    cartes, anomalies, stats = [], [], Counter()
    for carte in preselection:
        uid = carte["uid"]
        extrait = charger_json(INTERIM / "extraits" / f"{uid}.json")
        chemin = INTERIM / "ia" / "etape2" / f"{uid}.json"
        if not chemin.exists():
            anomalies.append(f"{uid} : classement manquant")
            classement = {"groupes": {}}
        else:
            classement = charger_json(chemin)
            if classement.get("uid") != uid:
                anomalies.append(f"{uid} : identifiant interne {classement.get('uid')} différent → tout en C")
                classement = {"groupes": {}}
        groupes = classement.get("groupes", {})
        en_trop = set(groupes) - set(carte["positions"])
        if en_trop:
            anomalies.append(f"{uid} : groupes en trop {sorted(en_trop)}")

        verdicts = {}
        for g, pos in carte["positions"].items():
            c = groupes.get(g)
            if not c:
                anomalies.append(f"{uid} : {g} sans classement → C")
                verdicts[g] = {"categorie": "C", "citation": None, "orateur": None, "justification": None}
                continue
            cat = c.get("categorie")
            textes_du_groupe = [canon(i["texte"]) for i in extrait["interventions"] if i.get("groupe") == g]
            def trouvee(champ):
                cit = canon(c.get(champ))
                return bool(cit) and any(cit in t for t in textes_du_groupe)
            if cat in ("A", "B") and not trouvee("citation"):
                anomalies.append(f"{uid} : {g} citation introuvable chez le groupe → C")
                cat = "C"
            if cat == "B" and not trouvee("citation_raison"):
                anomalies.append(f"{uid} : {g} raison du vote non citée chez le groupe → A")
                cat = "A"
            verdicts[g] = {**{k: c.get(k) for k in ("orateur", "citation", "citation_raison", "justification")},
                           "categorie": cat}
            stats[cat] += 1

        neutralises = sorted(g for g, v in verdicts.items() if v["categorie"] == "B")
        positions = {g: p for g, p in carte["positions"].items() if g not in neutralises}
        paires = [(a, b) for a, b in itertools.combinations(ORDRE, 2)
                  if a in positions and b in positions and positions[a] != positions[b]]
        cartes.append({**carte, "positions_brutes": carte["positions"], "positions": positions,
                       "neutralises": neutralises, "ambiguite": verdicts, "paires": len(paires)})

    retenues = [c for c in cartes if c["paires"] > 0]
    ecrire_json(INTERIM / "apres_ambiguite.json", retenues)

    lignes = ["# Étape 2 — votes ambigus", "",
              f"- Cartes contrôlées : {len(cartes)} ; encore utiles après neutralisation : {len(retenues)}",
              f"- Catégories : {dict(stats)}",
              f"- Anomalies corrigées automatiquement : {len(anomalies)}", "", "## Groupes neutralisés", ""]
    for c in cartes:
        for g in c["neutralises"]:
            v = c["ambiguite"][g]
            lignes.append(f"- **{g}** ({c['positions_brutes'][g]}) — {c['titre'][:140]}")
            lignes.append(f"  - {v['justification']}")
            lignes.append(f"  - Principe : « {v['citation']} » — {v['orateur']}")
            lignes.append(f"  - Raison : « {v['citation_raison']} »")
    lignes += ["", "## Anomalies", ""] + [f"- {a}" for a in anomalies]
    (INTERIM / "ambiguite.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"Contrôlées : {len(cartes)} · utiles : {len(retenues)} · catégories : {dict(stats)} · anomalies : {len(anomalies)}")
    print("Neutralisations :", sum(len(c["neutralises"]) for c in cartes),
          dict(Counter(g for c in cartes for g in c["neutralises"])))


if __name__ == "__main__":
    main()
