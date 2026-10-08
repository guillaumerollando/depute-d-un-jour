"""Télécharge et décompresse les données ouvertes de l'Assemblée nationale (17e législature) dans data/raw/."""
import io
import urllib.request
import zipfile

from commun import RAW

BASE = "https://data.assemblee-nationale.fr/static/openData/repository/17/"
JEUX = {
    "scrutins": "loi/scrutins/Scrutins.json.zip",
    "dossiers": "loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip",
    "amendements": "loi/amendements_div_legis/Amendements.json.zip",
    "debats": "vp/syceronbrut/syseron.xml.zip",
    "amo30": "amo/tous_acteurs_mandats_organes_xi_legislature/AMO30_tous_acteurs_tous_mandats_tous_organes_historique.json.zip",
}


def main():
    for dossier, chemin in JEUX.items():
        print(f"Téléchargement : {chemin}")
        with urllib.request.urlopen(BASE + chemin, timeout=600) as r:
            archive = zipfile.ZipFile(io.BytesIO(r.read()))
        cible = RAW / dossier
        cible.mkdir(parents=True, exist_ok=True)
        for membre in archive.namelist():
            # Garde-fou : aucun chemin ne doit sortir du dossier cible
            if membre.startswith("/") or ".." in membre.split("/"):
                raise ValueError(f"chemin suspect dans l'archive : {membre}")
        archive.extractall(cible)
    print("Terminé.")


if __name__ == "__main__":
    main()
