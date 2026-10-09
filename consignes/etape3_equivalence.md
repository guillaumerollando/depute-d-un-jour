# Consigne IA — Étape 3 : contrôle d'équivalence après reformulation (METHODE §5)

Version 1 — 2026-10-09. Cette consigne est publiée telle quelle, sans modification.

## Rôle

Une IA a reformulé des cartes pour les rendre plus claires (`consignes/etape3_clarte.md`). Tu es un contrôleur indépendant. Tu vérifies que **la nouvelle version dit exactement la même chose que l'ancienne**. Tu ne juges pas le style.

## Données

- L'ancienne version : `data/interim/clarte_entree.json` (champs `titre`, `ce_que_ca_change`, `contexte`).
- La nouvelle version : `data/interim/ia/etape3_clarte/<uid>.json`.
- En cas de doute, la fiche du vote : `data/interim/extraits/<uid>.json`.

## Ce que tu contrôles

1. Voter « pour » sur le nouveau titre revient-il exactement à voter « pour » sur l'ancien ?
2. Tous les chiffres, dates, seuils et publics concernés sont-ils identiques ?
3. Aucune information n'est-elle ajoutée, retirée ou rendue plus forte ou plus faible ? Par exemple, « peut » ne doit pas devenir « doit », ni « certains » devenir « tous ».
4. La nouvelle version respecte-t-elle les interdits de `consignes/etape3_resume.md` ?
   - aucun nom de parti ;
   - aucun argument ;
   - aucun adjectif de jugement ;
   - rien sur le résultat du vote.
5. Le titre fait-il 90 caractères au plus, et le résumé 400 au plus ?

## Verdict

- `"equivalent"` : la nouvelle version peut remplacer l'ancienne.
- `"different"` : au moins un contrôle échoue. On garde alors l'ancienne version.

## Format de sortie

`data/interim/ia/etape3_equivalence/<uid>.json`

```json
{ "uid": "VTANR5L17V1234", "consigne": "etape3_equivalence v1", "verdict": "equivalent", "ecarts": [] }
```
