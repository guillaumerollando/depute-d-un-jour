"""Exploration : quels scrutins départagent chaque paire de groupes ?

Règles (provisoires, à reporter dans METHODE.md) :
- abstentions ignorées : seule compte la position pour / contre ;
- position d'un groupe retenue si au moins MIN_EXPRIMES voix pour+contre
  et si la majorité représente au moins COHESION des voix exprimées ;
- scrutin retenu si au moins MIN_VOTANTS votants ;
- une paire est « départagée » si un groupe est pour et l'autre contre.
"""
import glob
import itertools
import json
import re
import sys
from collections import Counter, defaultdict

RAW = sys.argv[1]
MIN_VOTANTS = 100
MIN_EXPRIMES = 3
COHESION = 0.8

ALIAS = {"PO847173": "PO872880"}  # UDR réenregistré le 2025-09-05
NOMS = {
    "PO845401": "RN", "PO845407": "EPR", "PO845413": "LFI", "PO845419": "SOC",
    "PO845425": "DR", "PO845439": "ECOS", "PO845454": "DEM", "PO845470": "HOR",
    "PO845485": "LIOT", "PO845514": "GDR", "PO872880": "UDR",
}
ORDRE = ["LFI", "GDR", "ECOS", "SOC", "LIOT", "DEM", "EPR", "HOR", "DR", "UDR", "RN"]


def categorie(titre):
    t = titre.lower()
    if re.search(r"^l.amendement|^les amendements|sous-amendement", t):
        return "amendement"
    if re.search(r"^l.article", t):
        return "article"
    if re.search(r"l.ensemble", t):
        return "ensemble"
    return "autre"


def positions(s):
    pos = {}
    for g in s["ventilationVotes"]["organe"]["groupes"]["groupe"]:
        nom = NOMS.get(ALIAS.get(g["organeRef"], g["organeRef"]))
        if not nom:
            continue
        d = g["vote"]["decompteVoix"]
        p, c = int(d["pour"]), int(d["contre"])
        if p + c < MIN_EXPRIMES:
            continue
        if p / (p + c) >= COHESION:
            pos[nom] = "pour"
        elif c / (p + c) >= COHESION:
            pos[nom] = "contre"
    return pos


scrutins = []
for f in glob.glob(f"{RAW}/scrutins/json/*.json"):
    s = json.load(open(f))["scrutin"]
    if s["typeVote"]["codeTypeVote"] == "MOC":
        continue
    if int(s["syntheseVote"]["nombreVotants"]) < MIN_VOTANTS:
        continue
    scrutins.append((s, positions(s), categorie(s["titre"])))

print(f"Scrutins retenus (>= {MIN_VOTANTS} votants, hors censure) : {len(scrutins)}\n")

paires = defaultdict(list)
for s, pos, cat in scrutins:
    for a, b in itertools.combinations(ORDRE, 2):
        if a in pos and b in pos and pos[a] != pos[b]:
            paires[(a, b)].append((s, pos, cat))

print("Nombre de scrutins départageant chaque paire (tous types | dont article/ensemble)")
print("      " + "".join(f"{g:>10}" for g in ORDRE))
for a in ORDRE:
    ligne = f"{a:>6}"
    for b in ORDRE:
        k = (a, b) if ORDRE.index(a) < ORDRE.index(b) else (b, a)
        if a == b:
            ligne += f"{'-':>10}"
        else:
            L = paires[k]
            n2 = sum(1 for x in L if x[2] in ("article", "ensemble"))
            ligne += f"{f'{len(L)}|{n2}':>10}"
    print(ligne)

DIFFICILES = [("EPR", "DEM"), ("EPR", "HOR"), ("EPR", "DR"), ("DR", "RN"), ("RN", "UDR"),
              ("EPR", "RN"), ("LFI", "SOC"), ("SOC", "ECOS"), ("LFI", "GDR"), ("SOC", "LIOT")]
for a, b in DIFFICILES:
    k = (a, b) if ORDRE.index(a) < ORDRE.index(b) else (b, a)
    L = sorted(paires[k], key=lambda x: (x[2] == "amendement", -int(x[0]["syntheseVote"]["nombreVotants"])))
    print(f"\n=== {a} vs {b} : {len(L)} scrutins")
    for s, pos, cat in L[:6]:
        print(f"  [{cat}] {s['dateScrutin']} {a}:{pos[a]} {b}:{pos[b]} — {s['titre'][:170]}")
