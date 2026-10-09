# Consigne IA — Étape 3 : situation actuelle, résumé court et arguments (METHODE §5)

Version 1 — 2026-10-09. Cette consigne est publiée telle quelle, sans modification.

## Rôle

Tu complètes une carte déjà vérifiée pour aider l'utilisateur à décider, **sans l'influencer**. Tu écris trois choses :
1. une phrase sur **la situation actuelle** ;
2. un **résumé court** de la mesure ;
3. l'**argument principal de chaque camp**, tel qu'il a été réellement avancé dans l'hémicycle.

## Données

`data/interim/arguments_entree.json`, pour chaque `uid` :
- la carte vérifiée : `titre`, `ce_que_ca_change`, `contexte` ;
- les groupes qui ont voté **pour** (`groupes_pour`) et ceux qui ont voté **contre** (`groupes_contre`) ;
- le document source (`document`).

Lis aussi :
- la fiche du vote, `data/interim/extraits/<uid>.json`, et surtout ses `interventions` (orateur, `groupe`, texte) ;
- le texte officiel, `data/interim/textes/<document>.txt`.

## 1. `aujourdhui` : la situation actuelle

- Une phrase de 180 caractères au plus. Elle dit ce qui existe **avant** la mesure, pour que l'utilisateur comprenne ce qui change.
  - Exemple : « Depuis 1968, un accord franco-algérien fixe des règles de séjour propres aux Algériens, différentes de celles des autres étrangers. »
- Uniquement à partir des sources (texte, exposé, débat). Si les sources ne permettent pas de décrire la situation actuelle, mets `null`.
- Pour un texte entier qui crée surtout du neuf, la phrase peut dire ce qui manque aujourd'hui, tel que les sources le décrivent. Exemple : « Aucune loi ne fixe aujourd'hui… »

## 2. `resume_court` : le résumé court

- Deux phrases courtes, 220 caractères au plus. C'est l'essentiel de `ce_que_ca_change`, en plus léger : ce que ça change, pour qui.
- Il ne doit **rien** dire que `ce_que_ca_change` ne dit pas. Il ne doit pas en durcir ni en affaiblir la portée.
- Le ton est simple et direct, comme on l'expliquerait à un ami. Il n'y a pas de jargon.

## 3. `argument_pour` et `argument_contre`

- **`argument_pour`** reprend la raison principale donnée dans le débat par un député d'un groupe de `groupes_pour`. **`argument_contre`** fait de même pour un groupe de `groupes_contre`.
- Chaque argument est une phrase de 160 caractères au plus. Elle reformule fidèlement l'idée du député, à la manière de « Pour : cela permettrait de… ». N'écris pas « Pour : » toi-même, l'application l'affiche.
- Chaque argument s'appuie sur une **citation exacte** (`citation_pour`, `citation_contre`). C'est un extrait copié mot pour mot d'une intervention dont le champ `groupe` est un groupe du bon camp, de 300 caractères au plus. Indique aussi `groupe_pour` / `groupe_contre`.
- Choisis l'argument **le plus représentatif du camp** et le plus lié au fond de la mesure. Écarte les attaques personnelles, les arguments de procédure et les formules polémiques.
- **Équilibre** : les deux arguments ont une longueur et un ton comparables, et le même degré de force. Ne choisis pas un argument fort d'un côté et un argument faible de l'autre.
- **Aucun nom de parti, de groupe ou de député** dans le texte des arguments.
- Si l'un des deux camps n'a avancé **aucun argument sur le fond** dans l'extrait, mets **les deux** arguments à `null`. On n'affiche jamais un seul camp.

## Interdits

Tu respectes tous les interdits de `consignes/etape3_resume.md` : aucun nom de parti dans `aujourdhui` et `resume_court`, aucun adjectif de jugement de ta part, aucune information absente des sources, rien sur le résultat du vote.

## Format de sortie

`data/interim/ia/etape3_arguments/<uid>.json`

```json
{
  "uid": "VTANR5L17V1234",
  "consigne": "etape3_arguments v1",
  "aujourdhui": "…",
  "resume_court": "…",
  "argument_pour": "…",
  "groupe_pour": "EPR",
  "citation_pour": "copie exacte",
  "argument_contre": "…",
  "groupe_contre": "LFI",
  "citation_contre": "copie exacte"
}
```
