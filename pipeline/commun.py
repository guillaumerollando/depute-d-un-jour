"""Constantes et règles partagées — chaque valeur correspond à une règle de METHODE.md."""
import json
import re
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RAW = RACINE / "data" / "raw"
INTERIM = RACINE / "data" / "interim"

# METHODE §2 — position d'un groupe
MIN_EXPRIMES = 3
COHESION = 0.8
# METHODE §2 — scrutin éligible
MIN_VOTANTS = 100
MIN_GROUPES_POSITIONNES = 6
# METHODE §2 (v0.3) — votes d'article et d'amendement : participation minimale plus haute
MIN_VOTANTS_DETAIL = 200

# METHODE §2 — groupes (organes GP de la 17e législature) ; les non-inscrits sont exclus
ALIAS = {"PO847173": "PO872880"}  # UDR réenregistré le 2025-09-05
GROUPES = {
    "PO845413": "LFI", "PO845514": "GDR", "PO845439": "ECOS", "PO845419": "SOC",
    "PO845485": "LIOT", "PO845454": "DEM", "PO845407": "EPR", "PO845470": "HOR",
    "PO845425": "DR", "PO872880": "UDR", "PO845401": "RN",
}
ORDRE = ["LFI", "GDR", "ECOS", "SOC", "LIOT", "DEM", "EPR", "HOR", "DR", "UDR", "RN"]

# METHODE §6 — priorité des types en cas d'égalité (plus petit = prioritaire)
PRIORITE_TYPE = {"ensemble": 0, "resolution": 0, "partie": 1, "article": 1, "amendement": 2}


def normaliser(texte):
    t = unicodedata.normalize("NFKD", texte.lower()).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", t).split())


def categorie(titre):
    """Type de scrutin d'après son intitulé (METHODE §2)."""
    t = titre.lower().strip()
    if "motion de censure" in t:
        return "censure"
    if re.match(r"la motion (de rejet|de renvoi)", t):
        return "motion"
    if re.match(r"la déclaration", t):
        return "declaration"
    if re.match(r"la (proposition|demande) (du gouvernement de prolonger|de suspension)", t):
        return "procedure"
    if re.search(r"^l.amendement|^les amendements|^le sous-amendement|^les sous-amendements", t):
        return "amendement"
    if re.match(r"l.article|les articles", t):
        return "article"
    if re.search(r"l.ensemble", t):
        return "ensemble"
    if re.match(r"la (première|seconde|deuxième|troisième|quatrième) partie", t):
        return "partie"
    if re.match(r"la proposition de résolution", t):
        return "resolution"
    return "autre"


TYPES_ELIGIBLES = {"ensemble", "resolution", "partie", "article", "amendement"}


def charger_json(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def ecrire_json(chemin, donnees):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1)
