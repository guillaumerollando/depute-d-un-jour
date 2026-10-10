"""Étape 2a (METHODE §4) : extraire des comptes rendus le débat qui précède chaque vote présélectionné.

Le vote est retrouvé dans le compte rendu de sa séance grâce à ses chiffres exacts
(votants, pour, contre). Le débat retenu va du vote précédent (résultat annoncé) jusqu'à ce vote.

Entrée : data/interim/preselection.json
Sortie : data/interim/extraits/<uid>.json
"""
import bisect
import glob
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

from commun import ALIAS, GROUPES, INTERIM, RAW, charger_json, ecrire_json

MAX_INTERVENTIONS = 80
MAX_CARACTERES = 30000
FIN_DE_VOTE = re.compile(r"\((?:L[’'](?:amendement|article|ensemble)|Les amendements|Le sous-amendement|La motion|La proposition|Le projet|L[’']article)[^)]*(?:adopté|rejeté)[^)]*\)|Il est procédé au scrutin")


def local(e):
    return e.tag.split("}")[-1]


def texte(e):
    return " ".join("".join(e.itertext()).split()) if e is not None else ""


def appartenances():
    """acteur -> liste triée de (date, groupe), d'après les votes nominatifs."""
    vus = defaultdict(dict)
    for f in glob.glob(str(RAW / "scrutins/json/*.json")):
        s = charger_json(f)["scrutin"]
        for g in s["ventilationVotes"]["organe"]["groupes"]["groupe"]:
            nom = GROUPES.get(ALIAS.get(g["organeRef"], g["organeRef"]), "NI")
            nominatif = g["vote"].get("decompteNominatif") or {}
            for cat in nominatif.values():
                if not cat:
                    continue
                votants = cat.get("votant") if isinstance(cat, dict) else None
                if isinstance(votants, dict):
                    votants = [votants]
                for v in votants or []:
                    vus[v["acteurRef"]][s["dateScrutin"]] = nom
    return {a: sorted(d.items()) for a, d in vus.items()}


def groupe_a_la_date(app, acteur, date):
    hist = app.get(acteur)
    if not hist:
        return None
    i = bisect.bisect_right([d for d, _ in hist], date)
    return hist[max(i - 1, 0)][1]


def lire_compte_rendu(chemin):
    racine = ET.parse(chemin).getroot()
    paras = []
    bloc_article = 0
    for p in racine.iter():
        if local(p) == "point" and p.get("nivpoint") in ("1", "2", "3"):
            bloc_article += 1  # nouvel intertitre : « Article 3 », « Explications de vote »…
        if local(p) != "paragraphe":
            continue
        orateur = next((o for o in p.iter() if local(o) == "orateur"), None)
        nom = texte(next((c for c in orateur if local(c) == "nom"), None)) if orateur is not None else ""
        qualite = texte(next((c for c in orateur if local(c) == "qualite"), None)) if orateur is not None else ""
        corps = next((c for c in p if local(c) == "texte"), None)
        paras.append({
            "acteur": p.get("id_acteur"),
            "nom": nom,
            "qualite": qualite,
            "role": p.get("roledebat") or "",
            "grammaire": p.get("code_grammaire") or "",
            "point": p.get("valeur_ptsodj"),
            "bloc": bloc_article,
            "texte": texte(corps),
        })
    return paras


VOTES_DE_TEXTE = {"ensemble", "partie", "resolution"}
# METHODE §4 (v0.4) : un rapporteur ou président de commission compte pour son groupe s'il l'annonce
AU_NOM_DU_GROUPE = re.compile(r"au nom (?:du|de mon|de notre) groupe", re.IGNORECASE)


def fusionner(paras, app, date):
    """Regroupe les paragraphes consécutifs d'un même orateur en une intervention."""
    sortie = []
    for p in paras:
        if not p["texte"]:
            continue
        president = p["role"] == "president" or p["nom"].startswith(("M. le président", "Mme la présidente"))
        acteur = p["acteur"] if p["acteur"] and p["acteur"].startswith("PA") else None
        if sortie and acteur and sortie[-1]["_acteur"] == acteur:
            sortie[-1]["texte"] += " " + p["texte"]
            continue
        sortie.append({
            "_acteur": acteur,
            "orateur": p["nom"] or None,
            "qualite": p["qualite"] or None,
            "groupe": None,
            "president_de_seance": president,
            "texte": p["texte"],
        })
    for i in sortie:
        acteur = i.pop("_acteur")
        if not i["president_de_seance"] and (not i["qualite"] or AU_NOM_DU_GROUPE.search(i["texte"])):
            i["groupe"] = groupe_a_la_date(app, acteur, date)
    return sortie


def dernieres_par_groupe(interventions, par_groupe=2, min_caracteres=300):
    """Pour un vote sur un texte entier : les dernières prises de parole substantielles de chaque groupe,
    du Gouvernement et des rapporteurs, plus la mise aux voix."""
    gardees, compte = set(), defaultdict(int)
    for k in range(len(interventions) - 1, -1, -1):
        i = interventions[k]
        cle = i["groupe"] or i["qualite"]
        if not cle or i["president_de_seance"] or len(i["texte"]) < min_caracteres:
            continue
        if compte[cle] < par_groupe:
            compte[cle] += 1
            gardees.add(k)
    fin = [k for k in range(len(interventions) - 4, len(interventions)) if k >= 0]
    return [interventions[k] for k in sorted(gardees | set(fin))]


def borner(interventions):
    """Limite la taille en gardant les interventions les plus proches du vote."""
    garde, total = [], 0
    for i in reversed(interventions[-MAX_INTERVENTIONS:]):
        if total > MAX_CARACTERES:
            break
        garde.append(i)
        total += len(i["texte"])
    return list(reversed(garde))


def seance_precedente(chemin, ordonnes):
    i = ordonnes.index(chemin)
    return ordonnes[i - 1] if i > 0 else None


def chiffres(scrutin):
    d = scrutin["syntheseVote"]["decompte"]
    return (int(scrutin["syntheseVote"]["nombreVotants"]), int(d["pour"]), int(d["contre"]))


def chiffres_resultat(paras, i):
    """Votants, pour, contre annoncés à partir du paragraphe i."""
    bloc = " ".join(p["texte"] for p in paras[i:i + 3])
    def n(motif):
        m = re.search(motif + r"\D{0,40}?(\d+)", bloc)
        return int(m.group(1)) if m else None
    return n(r"Nombre de votants"), n(r"Pour l[’']adoption"), n(r"[Cc]ontre")


def main():
    preselection = charger_json(INTERIM / "preselection.json")
    bruts, par_seance = {}, defaultdict(list)
    for f in glob.glob(str(RAW / "scrutins/json/*.json")):
        s = charger_json(f)["scrutin"]
        bruts[s["uid"]] = s
        par_seance[s["seanceRef"]].append(s)
    comptes_rendus, dates_cr = {}, {}
    for f in glob.glob(str(RAW / "debats/xml/compteRendu/*.xml")):
        with open(f, encoding="utf-8") as fh:
            entete = fh.read(2000)
        m = re.search(r"<seanceRef>([^<]+)</seanceRef>", entete)
        d = re.search(r"<dateSeance>(\d+)</dateSeance>", entete)
        if m:
            comptes_rendus[m.group(1)] = f
            dates_cr[f] = d.group(1) if d else ""
    comptes_rendus_ordonnes = sorted(comptes_rendus.values(), key=lambda f: (dates_cr[f], f))
    app = appartenances()
    cache = {}
    trouves = 0
    for carte in preselection:
        brut = bruts[carte["uid"]]
        seance = brut["seanceRef"]
        sortie = {
            "uid": carte["uid"],
            "titre": carte["titre"],
            "type": carte["type"],
            "date": carte["date"],
            "dossier": carte["dossier"],
            "dossier_titre": carte["dossier_titre"],
            "sort": carte["sort"],
            "positions": carte["positions"],
            "voix": carte["voix"],
            "amendement": carte.get("amendement"),
            "seance": seance,
            "compte_rendu": None,
            "interventions": [],
        }
        chemin = comptes_rendus.get(seance)
        if chemin:
            if chemin not in cache:
                cache = {chemin: lire_compte_rendu(chemin)}
            paras = cache[chemin]
            attendu = chiffres(brut)
            # Deux scrutins d'une même séance peuvent avoir les mêmes chiffres :
            # le k-ième scrutin (par numéro) correspond à la k-ième annonce identique.
            jumeaux = sorted(int(b["numero"]) for b in par_seance[seance] if chiffres(b) == attendu)
            rang = jumeaux.index(int(brut["numero"]))
            annonces = [i for i, p in enumerate(paras)
                        if "résultat du scrutin" in p["texte"] and chiffres_resultat(paras, i) == attendu]
            if carte["type"] == "amendement" and carte.get("amendement_numero"):
                # La mise aux voix qui précède l'annonce doit citer le numéro de l'amendement
                motif = re.compile(rf"\bn(?:o|os|°)\s*(?:\d+\s*(?:,|et)\s*)*{carte['amendement_numero']}\b")
                annonces = [i for i in annonces
                            if any(motif.search(q["texte"]) for q in paras[max(i - 4, 0):i])]
                rang = 0 if len(annonces) == 1 else rang
            idx = annonces[rang] if rang < len(annonces) else None
            if idx is not None:
                trouves += 1
                # remonter jusqu'à « Je mets aux voix », puis jusqu'au vote précédent
                # Remonter jusqu'à la mise aux voix, sans dépasser l'annonce de résultat précédente
                borne = max((i for i in range(idx) if "résultat du scrutin" in paras[i]["texte"]), default=0)
                debut_vote = idx
                while debut_vote > borne and not re.search(r"Il est procédé au scrutin|Je mets aux voix",
                                                           paras[debut_vote]["texte"]):
                    debut_vote -= 1
                j = debut_vote - 1
                while j > 0 and not FIN_DE_VOTE.search(paras[j]["texte"]):
                    j -= 1
                vote_de_texte = carte["type"] in VOTES_DE_TEXTE or "article unique" in carte["titre"]
                if vote_de_texte:
                    # Tout le point de l'ordre du jour : discussion générale et explications de vote
                    point = paras[debut_vote]["point"]
                    j = debut_vote - 1
                    while j > 0 and paras[j]["point"] == point:
                        j -= 1
                elif carte["type"] == "article":
                    # Tout l'examen de l'article : prises de parole sur l'article et amendements
                    bloc = paras[debut_vote]["bloc"]
                    j = debut_vote - 1
                    while j > 0 and paras[j]["bloc"] == bloc:
                        j -= 1
                bruts_fenetre = paras[j + 1:debut_vote + 1]
                if j <= 0:
                    # Vote en début de séance : le débat s'est tenu à la fin de la séance précédente
                    prec = seance_precedente(chemin, comptes_rendus_ordonnes)
                    if prec:
                        pp = lire_compte_rendu(prec)
                        k = len(pp) - 1
                        while k > 0 and not FIN_DE_VOTE.search(pp[k]["texte"]):
                            k -= 1
                        bruts_fenetre = pp[k + 1:] + bruts_fenetre
                        sortie["compte_rendu_precedent"] = prec.split("/")[-1].removesuffix(".xml")
                fenetre = fusionner(bruts_fenetre, app, carte["date"])
                if vote_de_texte or carte["type"] == "article":
                    fenetre = dernieres_par_groupe(fenetre)
                sortie["interventions"] = borner(fenetre)
                sortie["compte_rendu"] = chemin.split("/")[-1].removesuffix(".xml")
        ecrire_json(INTERIM / "extraits" / f"{carte['uid']}.json", sortie)
    # Vote sur un article : son examen comprend aussi les débats sur ses amendements mis aux voix
    # au scrutin public juste avant, dans la même séance (sinon l'extrait peut être presque vide)
    def article_vise(titre):
        m = re.search(r"l.article (\d+(?:\s(?:bis|ter|quater|quinquies|sexies|[a-z]))*|premier|unique)", titre.lower())
        return m.group(1) if m else None

    for carte in preselection:
        if carte["type"] != "article" or "article unique" in carte["titre"] or not article_vise(carte["titre"]):
            continue
        f = INTERIM / "extraits" / f"{carte['uid']}.json"
        sortie = charger_json(f)
        voisins = sorted(
            (c for c in preselection if c["uid"] != carte["uid"] and c["numero"] < carte["numero"]
             and bruts[c["uid"]]["seanceRef"] == bruts[carte["uid"]]["seanceRef"]
             and article_vise(c["titre"]) == article_vise(carte["titre"])),
            key=lambda c: c["numero"])
        if not voisins:
            continue
        avant = [i for c in voisins for i in charger_json(INTERIM / "extraits" / f"{c['uid']}.json")["interventions"]]
        sortie["interventions"] = borner(dernieres_par_groupe(avant + sortie["interventions"]))
        sortie["debats_amendements"] = [c["uid"] for c in voisins]
        ecrire_json(f, sortie)

    # Amendements en discussion commune : plusieurs amendements au même endroit du texte sont débattus ensemble,
    # puis mis aux voix l'un après l'autre. Un amendement dont l'extrait ne contient aucune prise de parole de groupe
    # reprend le débat du vote précédent au même endroit, dans la même séance.
    def emplacement(titre):
        m = re.search(r"(?:à|après|avant) l.article [^(]*?(?= du | de la |\()", titre.lower())
        return m.group(0).strip() if m else None

    def a_des_groupes(x):
        return any(i.get("groupe") for i in x["interventions"])

    extraits = {c["uid"]: charger_json(INTERIM / "extraits" / f"{c['uid']}.json") for c in preselection}
    for carte in sorted(preselection, key=lambda c: c["numero"]):
        x = extraits[carte["uid"]]
        if carte["type"] != "amendement" or a_des_groupes(x) or not emplacement(carte["titre"]):
            continue
        precedents = [c for c in preselection if c["numero"] < carte["numero"]
                      and bruts[c["uid"]]["seanceRef"] == bruts[carte["uid"]]["seanceRef"]
                      and emplacement(c["titre"]) == emplacement(carte["titre"]) and a_des_groupes(extraits[c["uid"]])]
        if precedents:
            source = max(precedents, key=lambda c: c["numero"])
            x["interventions"] = borner(extraits[source["uid"]]["interventions"] + x["interventions"])
            x["discussion_commune"] = source["uid"]
            ecrire_json(INTERIM / "extraits" / f"{carte['uid']}.json", x)

    print(f"Votes retrouvés dans les comptes rendus : {trouves} / {len(preselection)}")


if __name__ == "__main__":
    main()
