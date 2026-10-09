# Consigne IA — Étape 3 : contrôle d'un titre d'accroche

Version 1 — 2026-10-10. Cette consigne est publiée telle quelle, sans modification.

## Rôle

Une IA a réécrit le titre d'une carte « texte entier » selon `consignes/etape3_accroche.md` (lis-la). Tu es un contrôleur indépendant et strict.

## Contrôles

1. **Mesures phares.** Recompte, dans le débat (`data/interim/extraits/<uid>.json` et `data/interim/debats_elargis/<uid>.json`), les mesures citées par les groupes. Les mesures du titre sont-elles bien les plus citées ?
2. **Exactitude.** Le titre décrit-il fidèlement ce que fait la loi, avec les termes du résumé et du texte officiel, sans exagérer ni atténuer ?
3. **Sens du vote.** Voter « pour » le titre revient-il bien à voter pour la loi ?
4. **Neutralité et lisibilité.** Aucun mot de jugement, aucun nom de parti, pas de date limite ; une phrase française complète, comprise du premier coup ; 90 caractères maximum.

## Format de sortie

`data/interim/ia/etape3_accroche_verif/<uid>.json`

```json
{ "uid": "…", "consigne": "etape3_accroche_verification v1", "verdict": "valide", "problemes": [] }
```

`verdict` vaut `"valide"` ou `"refuse"`. Un titre refusé n'est pas appliqué : l'ancien titre reste.
