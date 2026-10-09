"""Étape 4 : exporter le paquet final pour l'application (app/public/data/).

- groupes.json : groupes dans l'ordre usuel de l'hémicycle, avec nom, sigle et couleur officiels
- cartes.json  : cartes du paquet final, avec le vote nominatif de chaque député
- deputes.json : nom, groupe et département des députés ayant voté sur ces cartes
- meta.json    : date des données, volumes, adresse du dépôt
"""
import glob
import json
import os

from commun import ALIAS, GROUPES, INTERIM, ORDRE, RACINE, RAW, charger_json, ecrire_json
from etape2_controle import canon
from etape2_extraits import appartenances, groupe_a_la_date
from etape3_selection import CAMPS_POLITIQUES, NOMS_INTERDITS

LIMITES = {"aujourdhui": 180, "resume_court": 220, "argument_pour": 160, "argument_contre": 160}


def complements(c):
    """Situation actuelle, résumé court et arguments (consignes etape3_arguments), après vérification
    IA puis contrôle mécanique : citations exactes, du bon camp, sans nom de parti, longueurs respectées."""
    f_arg = INTERIM / "ia/etape3_arguments" / f"{c['uid']}.json"
    f_ver = INTERIM / "ia/etape3_arguments_verif" / f"{c['uid']}.json"
    if not f_arg.exists() or not f_ver.exists():
        return {}
    arg, ver = charger_json(f_arg), charger_json(f_ver)
    if ver.get("verdict") == "rejete":
        return {}
    arg.update(ver.get("corrections") or {})
    if ver.get("verdict") == "sans_arguments":
        arg["argument_pour"] = arg["argument_contre"] = None
    sortie = {}
    for champ in ("aujourdhui", "resume_court"):
        t = arg.get(champ)
        if t and len(t) <= LIMITES[champ] and not NOMS_INTERDITS.search(t) and not CAMPS_POLITIQUES.search(t):
            sortie[champ] = t
    extrait = charger_json(INTERIM / "extraits" / f"{c['uid']}.json")
    f_elargi = INTERIM / "debats_elargis" / f"{c['uid']}.json"
    if f_elargi.exists():  # débat élargi aux autres séances consacrées au texte (etape3_debat_elargi)
        extrait = {**extrait, "interventions": extrait["interventions"] + charger_json(f_elargi)["interventions"]}

    def valide(camp):
        texte, groupe, cit = arg.get(f"argument_{camp}"), arg.get(f"groupe_{camp}"), canon(arg.get(f"citation_{camp}"))
        if not texte or len(texte) > LIMITES[f"argument_{camp}"] or NOMS_INTERDITS.search(texte):
            return False
        if c["positions"].get(groupe) != camp or not cit:
            return False
        return any(cit in canon(i["texte"]) for i in extrait["interventions"] if i.get("groupe") == groupe)

    if valide("pour") and valide("contre"):  # jamais un seul camp
        sortie["arguments"] = {"pour": arg["argument_pour"], "contre": arg["argument_contre"],
                               # citations exactes, affichées anonymement pendant le jeu
                               "citation_pour": arg["citation_pour"], "citation_contre": arg["citation_contre"]}
    return sortie

SORTIE = RACINE / "app" / "public" / "data"
DEPOT = os.environ.get("DEPOT", "https://github.com/guillaumerollando/depute-d-un-jour")
SIGLES = {"LFI": "LFI-NFP", "UDR": "UDR"}


def acteurs():
    """acteur -> (nom affiché, département du mandat de la 17e législature)."""
    res = {}
    for f in glob.glob(str(RAW / "amo30/json/acteur/*.json")):
        a = charger_json(f)["acteur"]
        uid = a["uid"]["#text"] if isinstance(a["uid"], dict) else a["uid"]
        ident = a["etatCivil"]["ident"]
        mandats = a.get("mandats", {}).get("mandat") or []
        mandats = mandats if isinstance(mandats, list) else [mandats]
        dep = None
        for m in mandats:
            if m.get("typeOrgane") == "ASSEMBLEE" and str(m.get("legislature")) == "17":
                lieu = (m.get("election") or {}).get("lieu") or {}
                dep = lieu.get("departement") if isinstance(lieu.get("departement"), str) else dep
        res[uid] = (f"{ident['prenom']} {ident['nom']}", dep)
    return res


def coherence(carte):
    """Passe de cohérence (consigne etape3_coherence) : corrections appliquées seulement si le contrôle les accepte."""
    f_cor = INTERIM / "ia/etape3_coherence" / f"{carte['uid']}.json"
    f_ver = INTERIM / "ia/etape3_coherence_verif" / f"{carte['uid']}.json"
    if not f_cor.exists() or not f_ver.exists():
        return carte
    cor, ver = charger_json(f_cor).get("corrections") or {}, charger_json(f_ver)
    acceptes = set(cor) if ver.get("verdict") == "valide" else set(ver.get("champs_acceptes") or []) if ver.get("verdict") == "partiel" else set()
    limites = {"titre": 90, "ce_que_ca_change": 450, "contexte": 300, **LIMITES}
    for champ in acceptes & set(cor):
        texte = cor[champ]
        if not texte or len(texte) > limites.get(champ, 400) or NOMS_INTERDITS.search(texte):
            continue
        if champ in ("argument_pour", "argument_contre"):
            if carte.get("arguments"):
                carte["arguments"][champ.split("_")[1]] = texte
        else:
            carte[champ] = texte
    return carte


def accroche(carte):
    """Titre d'accroche d'un texte entier (consigne etape3_accroche) : appliqué seulement si le contrôle le valide."""
    f_acc = INTERIM / "ia/etape3_accroche" / f"{carte['uid']}.json"
    f_ver = INTERIM / "ia/etape3_accroche_verif" / f"{carte['uid']}.json"
    if not f_acc.exists() or not f_ver.exists():
        return carte
    acc, ver = charger_json(f_acc), charger_json(f_ver)
    titre = acc.get("titre") or ""
    if acc.get("modifie") and ver.get("verdict") == "valide" and 0 < len(titre) <= 90 and not NOMS_INTERDITS.search(titre):
        carte["titre"] = titre
    return carte


def main():
    cartes = charger_json(RACINE / "data/publie/cartes.json")
    bruts = {}
    for f in glob.glob(str(RAW / "scrutins/json/*.json")):
        s = charger_json(f)["scrutin"]
        bruts[s["uid"]] = s

    # Sièges : effectif de chaque groupe au dernier scrutin
    dernier = max(bruts.values(), key=lambda s: (s["dateScrutin"], int(s["numero"])))
    sieges = {}
    for g in dernier["ventilationVotes"]["organe"]["groupes"]["groupe"]:
        gid = GROUPES.get(ALIAS.get(g["organeRef"], g["organeRef"]))
        if gid:
            sieges[gid] = int(g["nombreMembresGroupe"])

    groupes = []
    for gid in ORDRE:
        ref = next(k for k, v in GROUPES.items() if v == gid)
        o = charger_json(glob.glob(str(RAW / f"amo30/**/{ref}.json"), recursive=True)[0])["organe"]
        groupes.append({"id": gid, "sigle": SIGLES.get(gid, o["libelleAbrev"]), "nom": o["libelle"],
                        "couleur": o["couleurAssociee"], "sieges": sieges.get(gid, 0)})

    noms, app = acteurs(), appartenances()
    index_deputes, deputes = {}, []

    def idx(acteur, date):
        if acteur not in index_deputes:
            nom, dep = noms.get(acteur, (acteur, None))
            index_deputes[acteur] = len(deputes)
            deputes.append({"nom": nom, "groupe": groupe_a_la_date(app, acteur, date), "departement": dep})
        return index_deputes[acteur]

    sortie = []
    for c in cartes:
        votes = {"p": [], "c": []}
        for g in bruts[c["uid"]]["ventilationVotes"]["organe"]["groupes"]["groupe"]:
            nominatif = g["vote"].get("decompteNominatif") or {}
            for cle, cat in (("p", "pours"), ("c", "contres")):
                v = (nominatif.get(cat) or {}).get("votant") if isinstance(nominatif.get(cat), dict) else None
                for x in ([v] if isinstance(v, dict) else v or []):
                    votes[cle].append(idx(x["acteurRef"], c["date"]))
        sortie.append({k: c[k] for k in ("uid", "numero", "date", "type", "theme", "titre", "ce_que_ca_change",
                                          "contexte", "resultat", "positions", "neutralises", "citations", "liens")}
                      | {"socle": c.get("socle", False), "deputes": votes} | complements(c))
        sortie[-1] = accroche(coherence(sortie[-1]))

    meta = {"date_donnees": dernier["dateScrutin"], "scrutins_analyses": len(bruts), "cartes": len(sortie), "depot": DEPOT}
    for nom, contenu in (("groupes", groupes), ("cartes", sortie), ("deputes", deputes), ("meta", meta)):
        SORTIE.mkdir(parents=True, exist_ok=True)
        with open(SORTIE / f"{nom}.json", "w", encoding="utf-8") as f:
            json.dump(contenu, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Exporté : {len(groupes)} groupes, {len(sortie)} cartes, {len(deputes)} députés → {SORTIE}")


if __name__ == "__main__":
    main()
