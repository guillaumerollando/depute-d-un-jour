# Consigne IA — Étape 3 : regroupement des cartes par sujet (METHODE §6)

Version 1 — 2026-10-09. Cette consigne est publiée telle quelle, sans modification.

## Rôle

Tu regroupes des cartes de vote par **sujet**. L'objectif est d'éviter qu'un utilisateur se voie poser deux fois la même question sous deux formes. Tu ne juges ni l'importance ni l'intérêt des cartes.

## Données

`data/interim/sujets_entree.json` : la liste des cartes publiables. Chaque carte donne `uid`, `titre`, `ce_que_ca_change` et `dossier`.

## Règle

Deux cartes ont le **même sujet** si un citoyen y verrait essentiellement **la même question**. Par exemple :
- deux votes sur l'abrogation de la retraite à 64 ans, même dans deux textes différents ;
- la création d'un impôt minimum sur les très grands patrimoines, et la suppression de ce même impôt.

Deux cartes ont des **sujets différents** si la question posée diffère, même quand elles relèvent du même texte ou du même thème. Par exemple :
- deux mesures distinctes d'un même texte agricole ;
- l'abattage des loups et la méthode de comptage des loups.

En cas de doute, considère que les sujets sont différents.

## Format de sortie

`data/interim/ia/sujets.json` :

```json
{
  "consigne": "etape3_sujets v1",
  "sujets": {
    "VTANR5L17V1234": "retraite-64-ans",
    "VTANR5L17V5678": "retraite-64-ans",
    "VTANR5L17V9012": "comptage-des-loups"
  }
}
```

- Chaque `uid` reçoit exactement une étiquette.
- L'étiquette est courte, en minuscules, avec des tirets.
- Les cartes d'un même sujet portent la même étiquette.
