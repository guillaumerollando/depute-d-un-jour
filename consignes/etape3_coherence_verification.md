# Consigne IA — Étape 3 : contrôle des corrections de cohérence

Version 1 — 2026-10-10. Cette consigne est publiée telle quelle, sans modification.

## Rôle

Une IA a harmonisé les textes d'une carte selon `consignes/etape3_coherence.md` (lis-la). Tu es un contrôleur indépendant et strict. Tu vérifies que chaque correction **améliore la cohérence sans changer le fond**.

## Données

- Les textes d'origine : `data/interim/coherence_entree.json`.
- Les corrections : `data/interim/ia/etape3_coherence/<uid>.json`.
- Les sources : la fiche `data/interim/extraits/<uid>.json` et le texte officiel, via `data/interim/sources.json`.

## Contrôles

Pour chaque champ corrigé :

1. **Exactitude.** Le terme retenu est-il bien celui des sources, sans être plus large ou plus étroit que la réalité ?
2. **Fond intact.**
   - Rien n'est ajouté ni retiré, sauf pour supprimer une contradiction.
   - Le sens de « pour » est inchangé.
   - Les chiffres, les publics et les modalités sont inchangés, par exemple « peut » ne devient pas « doit ».
3. **Arguments.** Un argument corrigé reste-t-il fidèle à ce qu'a dit le député, ni renforcé ni affaibli ?
4. **Interdits et longueurs.** Les règles de `consignes/etape3_resume.md` sont-elles respectées ? Les limites de longueur aussi : titre 90 caractères, `ce_que_ca_change` 400, `aujourdhui` 180, chaque argument 160.

## Verdict

- `"valide"` : toutes les corrections peuvent être appliquées.
- `"partiel"` : seuls les champs listés dans `champs_acceptes` peuvent être appliqués.
- `"refuse"` : aucune correction n'est appliquée.

## Format de sortie

`data/interim/ia/etape3_coherence_verif/<uid>.json`

```json
{ "uid": "…", "consigne": "etape3_coherence_verification v1", "verdict": "partiel", "champs_acceptes": ["aujourdhui"], "problemes": ["…"] }
```
