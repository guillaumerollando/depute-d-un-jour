"""Mise à jour (METHODE §9) : préparer les fiches d'entrée des consignes IA pour les nouvelles cartes du paquet.

Usage : python3 maj_entrees.py clarte|arguments|coherence AAAA-MM-JJ
Ajoute aux fichiers data/interim/<etape>_entree.json les cartes du paquet (data/publie/cartes.json) votées après la
date donnée (celle des données du paquet précédent) et qui n'y sont pas encore, sans toucher aux entrées existantes. Les textes repris sont ceux que l'étape précédente a validés.
"""
import json
import sys

from commun import INTERIM, ORDRE, RACINE, charger_json


def texte_verifie(uid):
    """Titre, résumé et contexte après la vérification (corrections comprises)."""
    res = charger_json(INTERIM / "ia/etape3" / f"{uid}.json")
    ver = charger_json(INTERIM / "ia/etape3_verif" / f"{uid}.json")
    texte = {k: res.get(k) for k in ("titre", "ce_que_ca_change", "contexte")}
    texte.update({k: v for k, v in (ver.get("corrections") or {}).items() if k in texte})
    return texte


def texte_clair(uid):
    """Comme texte_verifie, puis la passe « français clair » si le contrôle d'équivalence l'a validée."""
    texte = texte_verifie(uid)
    f_cla, f_eq = INTERIM / "ia/etape3_clarte" / f"{uid}.json", INTERIM / "ia/etape3_equivalence" / f"{uid}.json"
    if f_cla.exists() and f_eq.exists() and charger_json(f_eq).get("verdict") == "equivalent":
        cla = charger_json(f_cla)
        texte.update({k: cla[k] for k in texte if cla.get(k)})
    return texte


def main():
    etape, depuis = sys.argv[1], sys.argv[2]
    cartes = charger_json(RACINE / "data/publie/cartes.json")
    sources = charger_json(INTERIM / "sources.json")
    chemin = INTERIM / f"{etape}_entree.json"
    entree = charger_json(chemin)
    ajouts = []
    for c in cartes:
        uid = c["uid"]
        if uid in entree or c["date"] <= depuis:
            continue
        if etape == "clarte":
            entree[uid] = texte_verifie(uid)
        elif etape == "arguments":
            entree[uid] = {**texte_clair(uid),
                           "groupes_pour": [g for g in ORDRE if c["positions"].get(g) == "pour"],
                           "groupes_contre": [g for g in ORDRE if c["positions"].get(g) == "contre"],
                           "document": sources.get(uid, {}).get("document")}
        elif etape == "coherence":
            f_arg = INTERIM / "ia/etape3_arguments" / f"{uid}.json"
            arg = charger_json(f_arg) if f_arg.exists() else {}
            f_ver = INTERIM / "ia/etape3_arguments_verif" / f"{uid}.json"
            if f_ver.exists():
                arg.update(charger_json(f_ver).get("corrections") or {})
            t = texte_clair(uid)
            entree[uid] = {"titre": t["titre"], "ce_que_ca_change": t["ce_que_ca_change"],
                           "aujourdhui": arg.get("aujourdhui"), "contexte": t["contexte"],
                           "argument_pour": arg.get("argument_pour"), "argument_contre": arg.get("argument_contre")}
        else:
            sys.exit(f"étape inconnue : {etape}")
        ajouts.append(uid)
    # Même mise en forme que les fichiers d'origine (indentation de 2), pour un diff lisible
    chemin.write_text(json.dumps(entree, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{chemin.name} : {len(ajouts)} ajout(s) : {' '.join(ajouts)}")


if __name__ == "__main__":
    main()
