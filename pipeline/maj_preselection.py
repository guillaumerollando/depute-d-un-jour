"""Mise à jour (METHODE §9) : présélection des scrutins votés depuis la date du paquet publié.

Le paquet publié est conservé tel quel. Les nouveaux scrutins passent par les mêmes règles que l'étape 1
(éligibilité, dernière lecture, socle, complément glouton), appliquées à eux seuls, puis s'ajoutent à
data/interim/preselection.json. Les étapes suivantes (débats, IA, sources) ne traitent que ces ajouts.

Entrées : data/interim/scrutins.json, data/interim/preselection.json, app/public/data/meta.json
Sorties : data/interim/preselection.json (complétée), data/interim/preselection_maj.md
"""
import sys
from collections import Counter

from commun import INTERIM, ORDRE, RACINE, charger_json, ecrire_json
from etape1_preselection import (COUVERTURE_CIBLE, eligible, regrouper_lectures, selection_gloutonne,
                                 socle_participation, socle_solennel)

# Assez de candidats pour que la sélection finale ait le choix après les contrôles et le regroupement par sujet
TAILLE_MAX_MAJ = 40


def main():
    depuis = sys.argv[1] if len(sys.argv) > 1 else charger_json(RACINE / "app/public/data/meta.json")["date_donnees"]
    scrutins = charger_json(INTERIM / "scrutins.json")
    preselection = charger_json(INTERIM / "preselection.json")
    deja = {s["uid"] for s in preselection}

    eligibles = [s for s in scrutins if eligible(s)]
    # Dernière lecture calculée sur toute la législature, puis on ne garde que ce qui est postérieur au paquet
    candidats = [s for s in regrouper_lectures(eligibles) if s["date"] > depuis and s["uid"] not in deja]
    choisis, _ = selection_gloutonne(candidats, COUVERTURE_CIBLE, TAILLE_MAX_MAJ)
    for s in choisis:
        s["socle"] = False
    pris = {s["uid"] for s in choisis}
    nouveaux = [s for s in scrutins if s["date"] > depuis]
    for s in socle_solennel(nouveaux) + socle_participation([s for s in eligibles if s["date"] > depuis]):
        if s["uid"] in deja:
            continue
        if s["uid"] in pris:
            next(c for c in choisis if c["uid"] == s["uid"])["socle"] = True
        else:
            choisis.append(s)
            pris.add(s["uid"])
    for s in choisis:
        s["maj"] = depuis

    ecrire_json(INTERIM / "preselection.json", preselection + choisis)
    lignes = [f"# Mise à jour — scrutins postérieurs au {depuis}", "",
              f"- Nouveaux scrutins : {len(nouveaux)} ; éligibles après regroupement des lectures : {len(candidats)}",
              f"- Ajoutés à la présélection : {len(choisis)} (dont socle : {sum(s['socle'] for s in choisis)})",
              f"- Types : {dict(Counter(s['type'] for s in choisis))}", "", "## Cartes", ""]
    for i, s in enumerate(sorted(choisis, key=lambda s: s["date"], reverse=True), 1):
        pour = " ".join(g for g in ORDRE if s["positions"].get(g) == "pour")
        contre = " ".join(g for g in ORDRE if s["positions"].get(g) == "contre")
        lignes += [f"{i}. **[{s['type']}]** {s['date']} — {s['titre']}" + (" — socle" if s["socle"] else ""),
                   f"   - Dossier : {s['dossier_titre']} · {s['votants']} votants · {s['sort']}",
                   f"   - Pour : {pour or '—'} · Contre : {contre or '—'}"]
    (INTERIM / "preselection_maj.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print(f"Postérieurs au {depuis} : {len(nouveaux)} scrutins · candidats : {len(candidats)} · ajoutés : {len(choisis)}")
    for s in sorted(choisis, key=lambda s: s["date"], reverse=True):
        print(f"  {s['uid']} {s['date']} {s['type']:10} {s['votants']:3} {'S' if s['socle'] else ' '} {s['titre'][:90]}")


if __name__ == "__main__":
    main()
