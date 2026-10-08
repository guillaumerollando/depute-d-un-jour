# Exploration des données — 2026-10-08

Source : data.assemblee-nationale.fr, législature 17 (fichiers mis à jour quotidiennement).

| Jeu | URL (repository/17/…) |
|---|---|
| Scrutins | loi/scrutins/Scrutins.json.zip |
| Dossiers + documents | loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip |
| Députés, groupes | amo/deputes_actifs_mandats_actifs_organes/AMO10_….json.zip |

## Chiffres
- 8 609 scrutins (2024-10-08 → 2026-10-08) : 7 354 amendements, 908 articles, 222 « ensemble », 81 motions.
- Participation médiane : 132 votants ; 360 scrutins à ≥ 300 votants.
- Lien scrutin → dossier : 2 783 directs (`objet.dossierLegislatif`), 251 via `voteRefs` des dossiers.
- Rattachement par titre de loi (titre du scrutin ↔ `titrePrincipal` des documents) : **8 093 / 8 609 (94 %)**, méthode encore naïve ; les échecs sont des variantes de titre.
- Chemin vers le texte : dossier → document (`PIONANR5L17B…`, `PRJLANR5L17B…`) → `titrePrincipal`, exposé, PDF.
- Positions par groupe dans chaque scrutin (`ventilationVotes…groupe[].vote.decompteVoix`).

## Points d'attention
- Motions de censure : seuls les « pour » sont comptés → à traiter à part.
- Groupes qui changent en cours de législature (PO847173 inconnu dans AMO10, remplacé par UDDPLR) → utiliser l'historique AMO30.
- Un score de clivage global (variance) sélectionne surtout des votes gauche / reste : il faut une sélection qui départage **toutes les paires de groupes** (ex. RN vs EPR, LFI vs SOC).

## Clivages par paire (pipeline/explore_paires.py)
Règles : abstentions ignorées, position de groupe si ≥ 80 % des voix pour+contre (≥ 3 voix), scrutins ≥ 100 votants, hors censure → 5 887 scrutins.
- Toutes les paires sont départagées au moins une fois.
- Paires les plus proches (scrutins pour/contre opposés, dont article/ensemble) : LFI–GDR 49|12, ECOS–GDR 45|7, RN–UDR 90|10, LIOT–DEM 155|9, EPR–DEM 175|9, EPR–HOR 242|20, DEM–HOR 235|16.
- DR se distingue nettement du bloc central (EPR–DR 976|72) ; SOC se distingue de LFI (636|122).
- Conséquence : en 10-15 cartes, certains groupes alliés ne pourront pas être départagés → afficher les ex aequo honnêtement.
- UDR : PO847173 (jusqu'au 2025-09-04) et PO872880 (depuis) fusionnés.
