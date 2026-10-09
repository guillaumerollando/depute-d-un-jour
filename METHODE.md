# Méthode

Ce document explique comment *Député d'un jour* passe des données brutes de l'Assemblée nationale aux cartes de l'application, puis au résultat affiché. Chaque règle a été fixée avant d'être appliquée. Le pipeline est déterministe : relancé sur les mêmes données, il produit le même paquet de cartes.

## Principes

1. **Seuls les faits comptent.** Le score repose uniquement sur des votes publics enregistrés à l'Assemblée nationale.
2. **Personne ne choisit les cartes.** Des règles écrites les sélectionnent.
3. **Aucune interprétation des votes.** Une abstention ne compte ni pour ni contre.
4. **Tout est vérifiable.** Chaque carte renvoie vers ses sources officielles. Le code, les consignes données à l'IA et les données intermédiaires sont publiés.
5. **Aucune consigne de vote.** L'application dit « tu as voté comme… », jamais « vote pour… ». Elle ne fait aucune projection sur les votes futurs.

## 1. Sources

Toutes les données viennent de [data.assemblee-nationale.fr](https://data.assemblee-nationale.fr), 17e législature, sous Licence Ouverte.

| Donnée | Fichier |
|---|---|
| Scrutins et votes nominatifs | `loi/scrutins/Scrutins.json.zip` |
| Dossiers législatifs et documents | `loi/dossiers_legislatifs/Dossiers_Legislatifs.json.zip` |
| Amendements | `loi/amendements_div_legis/Amendements.json.zip` |
| Comptes rendus des débats | `vp/syceronbrut/syseron.xml.zip` |
| Députés et groupes (historique) | `amo/tous_acteurs_mandats_organes_xi_legislature/AMO30_…json.zip` |

Les textes de loi viennent du site assemblee-nationale.fr. On essaie trois formats, dans cet ordre : la version open data en HTML, puis la version brute, puis le PDF converti en texte.

## 2. Groupes et positions

**Groupes.** Ce sont les groupes politiques de l'Assemblée. Leur nom et leur couleur sont ceux fournis par l'Assemblée. Les non-inscrits ne forment pas un groupe et ne sont pas comparés. Un groupe recréé sous un nouvel identifiant est fusionné avec l'ancien : c'est le cas de l'UDR.

**Position d'un groupe sur un scrutin.** On compte les voix « pour » (P) et « contre » (C) de ses membres. Les abstentions (A) et les non-votants sont ignorés.

| Condition | Position |
|---|---|
| P + C ≥ 3, P + C > A et P / (P + C) ≥ 80 % | **pour** |
| P + C ≥ 3, P + C > A et C / (P + C) ≥ 80 % | **contre** |
| Tous les autres cas, notamment un groupe divisé ou majoritairement abstentionniste | **sans position** |

Une carte ne compte jamais pour un groupe sans position, ni en accord ni en désaccord.

## 3. Des scrutins aux cartes

**Rattachement.** Chaque scrutin est relié à son dossier législatif. Cinq méthodes sont essayées dans cet ordre :
1. le lien officiel ;
2. l'amendement voté, retrouvé par le couple (séance, numéro) ;
3. les références de vote du dossier ;
4. le titre de loi cité par un scrutin déjà rattaché ;
5. la comparaison avec le titre des documents.

Au total, 99,6 % des 8 609 scrutins sont rattachés.

**Scrutins éligibles.** Un scrutin peut devenir une carte s'il remplit toutes ces conditions :
- il porte sur un texte entier, une partie de budget, un article, un amendement dont on a le texte, ou une résolution ;
- il compte au moins 100 votants, et au moins 200 pour un article ou un amendement ;
- au moins 6 groupes y ont une position ;
- au moins un groupe vote pour et un autre contre.

Sont exclus :
- les motions de censure ;
- les motions de rejet, dont le sens est inversé ;
- les déclarations du Gouvernement ;
- les sous-amendements ;
- les amendements qui ne modifient que le titre d'un texte.

Quand un texte est voté plusieurs fois sur l'ensemble, seule la dernière lecture est retenue.

## 4. Votes ambigus

Un groupe peut voter contre une mesure qui va dans son sens, parce qu'il la juge insuffisante, mal rédigée, déjà satisfaite, ou parce qu'il en préfère une autre version. Il peut aussi voter pour une mesure dont il conteste le principe, « par responsabilité ».

**Ce qu'on lit.** Pour chaque carte candidate, on extrait du compte rendu officiel ce que chaque groupe a déclaré avant le vote :
- pour un amendement, sa discussion ;
- pour un article, son examen ;
- pour un texte entier, les dernières interventions de chaque groupe.

Seuls comptent les députés du groupe, et les rapporteurs qui déclarent parler « au nom du groupe ».

**Quand on neutralise.** Une IA classe la déclaration de chaque groupe selon la consigne [`consignes/etape2_ambiguite.md`](consignes/etape2_ambiguite.md). La position du groupe est **neutralisée sur cette carte** seulement si deux éléments sont **tous deux explicites** :
- le groupe adhère au principe de la mesure (ou s'y oppose). Juger qu'elle « ne va pas assez loin » vaut adhésion ;
- il donne lui-même une raison étrangère au fond.

Ces deux éléments doivent être des citations exactes. Un contrôle automatique vérifie qu'elles figurent mot pour mot dans les paroles du groupe ; sinon, la neutralisation est annulée. En cas de doute, la position est conservée. Au final, la neutralisation reste rare.

Les citations des groupes sont affichées dans l'application, mais jamais comptées dans le score.

## 5. Résumés

**Rédaction.** Une IA rédige chaque carte selon la consigne [`consignes/etape3_resume.md`](consignes/etape3_resume.md). La carte contient :
- un thème, choisi dans une liste fermée de 13 ;
- un titre à l'infinitif, qui dit exactement ce que signifie voter « pour » ;
- deux ou trois phrases factuelles ;
- le contexte du vote.

Elle ne contient ni nom de parti, ni argument, ni adjectif de jugement, ni information absente des sources, ni le résultat du vote.

**Vérification.** Une **seconde IA, indépendante**, contrôle chaque carte selon la consigne [`consignes/etape3_verification.md`](consignes/etape3_verification.md) : sens du vote, fidélité, neutralité et lisibilité. Pour un texte adopté, la référence est le **texte adopté en séance le jour du vote**, c'est-à-dire la version exacte mise aux voix.

**Français clair.** Une troisième IA reformule chaque carte pour qu'elle se lise du premier coup (phrases courtes, ordre naturel, jargon expliqué), selon [`consignes/etape3_clarte.md`](consignes/etape3_clarte.md). Une quatrième IA, indépendante, compare l'ancienne et la nouvelle version ([`consignes/etape3_equivalence.md`](consignes/etape3_equivalence.md)). La reformulation n'est retenue que si elle dit exactement la même chose : même sens, mêmes chiffres, même portée.

**Situation actuelle, résumé court et arguments.** Selon [`consignes/etape3_arguments.md`](consignes/etape3_arguments.md), chaque carte reçoit trois compléments :
- une phrase « Aujourd'hui » sur la situation avant la mesure ;
- un résumé court ;
- quand c'est possible, **l'argument principal de chaque camp**.

Chaque argument reformule une intervention **réellement prononcée** dans l'hémicycle par un député d'un groupe ayant voté dans ce sens. La citation exacte est conservée, et un contrôle automatique vérifie qu'elle figure mot pour mot dans les paroles d'un groupe du bon camp. Une seconde IA vérifie l'exactitude et l'**équilibre** des deux arguments ([`consignes/etape3_arguments_verification.md`](consignes/etape3_arguments_verification.md)). Si l'un des deux camps n'a avancé aucun argument de fond dans le débat, la carte n'affiche aucun argument : on ne présente jamais un seul camp. Les arguments restent derrière un bouton et ne comptent pas dans le score.

**Cartes écartées :**
- les cartes trop techniques ;
- celles dont le contenu voté ne peut pas être établi (c'est le cas de certains textes rejetés) ;
- les demandes de rapport, qui ne changent aucune règle ;
- les cartes qui nomment un camp politique.

## 6. Sélection du paquet

1. **Socle.** Les votes **solennels** sur un texte entrent d'office, un par texte. Ce sont ceux que la Conférence des présidents de l'Assemblée, où siègent tous les groupes, désigne elle-même comme ses votes majeurs.
2. **Complément.** Un algorithme glouton et déterministe ajoute une à une les cartes qui départagent le plus de **paires de groupes** encore peu départagées. Une paire est départagée quand l'un vote pour et l'autre contre. Il respecte trois limites :
   - au plus 8 cartes par thème ;
   - au plus 2 cartes par dossier ;
   - un seul vote par **sujet**. Une IA regroupe les cartes qui poseraient la même question, selon la consigne [`consignes/etape3_sujets.md`](consignes/etape3_sujets.md).
3. **Égalités.** Elles se règlent, dans l'ordre, par :
   1. le type de vote (texte entier, puis article, puis amendement) ;
   2. le nombre de votants ;
   3. la date ;
   4. le numéro du scrutin.
4. **Taille.** Le paquet compte au plus 80 cartes.

Les paires que les données ne départagent pas, parce que les groupes votent pareil, ne sont pas départagées artificiellement.

## 7. Résultat

**Gestes.** Boutons **pour** et **contre** ; à la souris, on peut aussi glisser la carte à droite ou à gauche. Le bouton **je ne sais pas** passe la carte sans qu'elle compte. L'**étoile** fait compter une carte double.

**Accord avec un groupe.** C'est la somme des poids des cartes où l'utilisateur et le groupe ont la même position, divisée par la somme des poids des cartes où tous deux ont une position. Deux groupes à moins de 10 points d'écart sont annoncés **ex aequo**.

**Pourquoi pas de « plutôt pour » ?** Un groupe vote pour ou contre : un « plutôt » n'existe pas dans les données. La nuance passe par l'étoile et par les citations.

**Ordre des cartes.**
- Les quatre premières viennent du socle, sur des thèmes tous différents.
- Ensuite, la carte suivante est celle qui départage le plus de paires parmi les groupes encore en tête. Un tirage au sort départage les cartes de valeur proche.
- Les cartes déjà vues lors des parties précédentes, mémorisées sur l'appareil, passent après les autres : deux parties de suite proposent des votes différents.
- Une partie compte 15 cartes, et on peut en ajouter par séries de 10.

**Député jumeau.** C'est le député dont les votes nominatifs ressemblent le plus aux tiens, parmi ceux qui ont voté sur au moins 60 % de tes cartes.

## 8. Limites connues

- Le résumé d'un texte long ne retient que ses mesures principales. Le texte complet reste accessible depuis chaque carte.
- Si un groupe ne s'exprime pas dans le débat, une éventuelle ambiguïté de son vote ne peut pas être détectée.
- Les IA peuvent se tromper. C'est pourquoi chaque carte est relue par une seconde IA, contrôlée mécaniquement, et entièrement publiée, pour que chacun puisse signaler une erreur.

## Reproduire

```bash
python3 pipeline/telecharger.py          # données brutes de l'Assemblée
python3 pipeline/etape0_scrutins.py      # positions et rattachements
python3 pipeline/etape1_preselection.py
python3 pipeline/etape2_extraits.py      # débats, puis classement IA (consigne etape2)
python3 pipeline/etape2_controle.py
python3 pipeline/etape3_sources.py       # textes officiels, puis résumés, vérifications et sujets (consignes etape3)
python3 pipeline/etape3_selection.py
python3 pipeline/etape4_export.py        # données de l'application
```

Les sorties des IA sont conservées dans `data/interim/ia/`. On peut donc relancer les étapes mécaniques sans refaire appel à une IA.
