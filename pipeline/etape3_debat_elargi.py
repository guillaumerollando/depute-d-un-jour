"""Étape 3d : débat élargi pour les cartes sans arguments (METHODE §5).

Quand un camp ne s'exprime pas dans l'extrait du vote, il a souvent parlé dans une autre séance consacrée au même texte.
Séances retenues, sans interprétation : la séance du vote et toutes celles où des amendements du même dossier ont été
discutés (`seanceDiscussionRef` des amendements). Dans chacune, on ne garde que les points de l'ordre du jour dont
le titre correspond au texte (mots communs avec le titre du dossier), puis les interventions substantielles des groupes.

Sortie : data/interim/debats_elargis/<uid>.json (même format que les extraits)
"""
import glob
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

from commun import INTERIM, RAW, charger_json, ecrire_json, normaliser
from etape2_extraits import appartenances, borner, dernieres_par_groupe, fusionner, local, texte

MOTS_VIDES = set("le la les de des du d l un une et a au aux en pour par sur dans visant relatif relative "
                 "relatifs relatives portant loi proposition projet organique texte".split())
MIN_CARACTERES = 300


def mots(titre):
    """Racines (5 premières lettres) des mots significatifs : « relance » et « relancer » se rejoignent."""
    t = (titre or "").replace("’", " ").replace("'", " ")
    return {m[:5] for m in normaliser(t).split() if len(m) > 2 and m not in MOTS_VIDES}


def interventions_du_texte(chemin, cles):
    """Paragraphes des points de l'ordre du jour dont le titre partage au moins la moitié des mots-clés du dossier."""
    racine = ET.parse(chemin).getroot()
    paras, garder = [], False
    for p in racine.iter():
        if local(p) == "point" and p.get("nivpoint") == "1":
            titre = texte(next((c for c in p if local(c) == "texte"), None))
            commun = mots(titre) & cles
            garder = bool(cles) and len(commun) >= max(2, len(cles) // 2)
        if local(p) != "paragraphe" or not garder:
            continue
        orateur = next((o for o in p.iter() if local(o) == "orateur"), None)
        nom = texte(next((c for c in orateur if local(c) == "nom"), None)) if orateur is not None else ""
        qualite = texte(next((c for c in orateur if local(c) == "qualite"), None)) if orateur is not None else ""
        corps = next((c for c in p if local(c) == "texte"), None)
        paras.append({"acteur": p.get("id_acteur"), "nom": nom, "qualite": qualite,
                      "role": p.get("roledebat") or "", "texte": texte(corps)})
    return paras


def main():
    import sys
    uids = sys.argv[1:]
    cartes = {c["uid"]: c for c in charger_json(RACINE_PUBLIE)}
    seances_par_dossier = defaultdict(set)
    for f in glob.glob(str(RAW / "amendements/json/*/*/*.json")):
        dossier = Path(f).parts[-3]
        with open(f, encoding="utf-8") as fh:
            m = re.search(r'"seanceDiscussionRef":\s*"([^"]+)"', fh.read())
        if m:
            seances_par_dossier[dossier].add(m.group(1))
    comptes_rendus = {}
    for f in glob.glob(str(RAW / "debats/xml/compteRendu/*.xml")):
        with open(f, encoding="utf-8") as fh:
            m = re.search(r"<seanceRef>([^<]+)</seanceRef>", fh.read(2000))
        if m:
            comptes_rendus[m.group(1)] = f
    app = appartenances()
    for uid in uids:
        c = cartes[uid]
        if c["type"] == "amendement":
            # Le débat général sur le texte ne porte pas sur l'amendement lui-même : pas d'élargissement
            print(uid, "amendement : pas d'élargissement")
            continue
        extrait = charger_json(INTERIM / "extraits" / f"{uid}.json")
        cles = mots(c["dossier_titre"])
        seances = {extrait["seance"]} | seances_par_dossier.get(c["dossier"], set())
        paras = []
        for s in sorted(seances):
            if s in comptes_rendus:
                paras += interventions_du_texte(comptes_rendus[s], cles)
        interventions = [i for i in fusionner(paras, app, c["date"])
                         if i["groupe"] and len(i["texte"]) >= MIN_CARACTERES]
        ecrire_json(INTERIM / "debats_elargis" / f"{uid}.json",
                    {**{k: extrait[k] for k in extrait if k != "interventions"},
                     # les 3 dernières interventions substantielles de CHAQUE groupe, pour représenter tous les camps
                    "seances": sorted(seances), "interventions": borner(dernieres_par_groupe(interventions, par_groupe=3))})
        print(uid, len(seances), "séances,", len(interventions), "interventions,",
              len({i["groupe"] for i in interventions}), "groupes")


RACINE_PUBLIE = INTERIM.parent / "publie" / "cartes.json"

if __name__ == "__main__":
    main()
