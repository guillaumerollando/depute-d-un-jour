# Député d'un jour : synthèse de la nuit

## Ce qui est livré

- **Une application web installable sur téléphone** (PWA, React), qui fonctionne de bout en bout :
  - swipe à droite pour voter pour, à gauche pour contre, vers le bas pour « je ne sais pas » ;
  - une étoile pour qu'un sujet compte double ;
  - une partie de 15 cartes, qu'on peut prolonger par séries de 10.
- **L'écran de résultat** montre :
  - l'hémicycle aux couleurs officielles, avec ton siège dans le groupe le plus proche ;
  - ton accord avec chaque groupe, avec les ex aequo à moins de 10 points d'écart ;
  - le groupe le plus éloigné ;
  - ton **député jumeau**, à partir des votes nominatifs ;
  - le détail **vote par vote** : la position de chaque groupe, ce qu'ils ont dit dans l'hémicycle, et des liens vers le texte, le scrutin et le débat officiels ;
  - un bouton de partage.
- **Un paquet de 80 cartes** tiré de 8 609 scrutins, dont **35 votes solennels**, avec 13 thèmes couverts. On y trouve par exemple l'aide à mourir, le budget de la Sécu, le narcotrafic, la Corse, la Nouvelle-Calédonie et les réseaux sociaux avant 15 ans.
- **Une page « Comment ça marche »** dans l'appli, et **[METHODE.md](METHODE.md)**, la méthode complète, sans historique des versions.
- **Un dépôt GitHub privé** : [guillaumerollando/depute-d-un-jour](https://github.com/guillaumerollando/depute-d-un-jour). Il contient le code, le pipeline, les consignes données aux IA et toutes leurs sorties, publiées pour audit.

## La méthode en 5 lignes

1. Un groupe a une position s'il vote à 80 % dans le même sens. Une abstention ne compte jamais, et un groupe majoritairement abstentionniste n'a pas de position.
2. Les votes solennels entrent d'office. Un algorithme déterministe ajoute ensuite ceux qui départagent le mieux les groupes, avec un seul vote par sujet.
3. Si un groupe déclare soutenir une mesure mais vote contre (« pas assez loin », « déjà satisfait »…), sa position est neutralisée sur cette carte. Il faut pour cela deux citations exactes, vérifiées automatiquement.
4. Une IA rédige chaque résumé, sans aucun nom de parti. Une seconde IA le vérifie face au **texte réellement adopté** en séance. Cette vérification a corrigé des chiffres faux, des mesures oubliées et une erreur de sens.
5. Ton score avec un groupe est la part des cartes où il a voté comme toi.

## Ce qu'il te reste à faire

- **Tester sur ton téléphone** :

  ```bash
  cd ~/Dev/depute-d-un-jour/app && npm run dev -- --host
  ```

- **Relire quelques cartes.** Le plus simple est `data/interim/selection.md`, qui contient les 80 cartes avec leurs résumés.
- **Publier quand tu veux** : rends le dépôt public, active Pages (Settings → Pages → Source : GitHub Actions), puis lance le workflow « Publication » depuis l'onglet Actions.

## Points d'attention

- **Deux textes majeurs sont absents** : la loi énergie-climat et la première partie du budget 2025. Ils ont été rejetés en séance, et la version exacte mise aux voix n'est publiée nulle part. La règle les écarte plutôt que de risquer une carte fausse.
- **Quelques cartes restent un peu techniques**, par exemple « Réduire de 500 000 € la hausse du budget de l'audiovisuel ». Elles sont là parce qu'elles départagent bien les groupes. L'ordre adaptatif les fait passer après les votes solennels.
- **Les groupes alliés se départagent peu** (EPR et MoDem, RN et UDR, LFI et les communistes). C'est un fait des données, que l'appli affiche honnêtement en ex aequo.
- **Pages légales** : l'appli ne collecte rien, donc une courte page de confidentialité suffira. Je peux la faire avec ton skill habituel.
