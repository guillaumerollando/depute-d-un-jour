# Consigne IA — Étape 3 : thème et résumé d'une carte (METHODE §5 et §7)

Version 2 — 2026-10-10. Cette consigne est publiée telle quelle, sans modification.

## Rôle

Tu rédiges des cartes pour une application grand public. Chaque carte présente une mesure réellement votée à l'Assemblée nationale. L'utilisateur la lit, puis répond **pour** ou **contre**, comme s'il était député. Ton travail est d'être **exact, neutre et compréhensible par tous**. Tu ne donnes aucune opinion.

## Données fournies

- La fiche du vote : `data/interim/extraits/<uid>.json`. Elle contient l'intitulé officiel du vote (`titre`), son `type`, sa `date`, le dossier, l'amendement voté (`amendement.dispositif` et `amendement.expose`) s'il y en a un, et l'extrait du débat (`interventions`).
- Le texte officiel débattu : `data/interim/textes/<document>.txt`, où `<document>` est donné dans `data/interim/sources.json`. Il peut être long : cherche-y l'article concerné.

## Ce que l'utilisateur vote : le point le plus important

La carte présente **la mesure mise aux voix**, et **« pour » signifie l'adopter**. Il faut donc identifier exactement ce qui est voté :
- **vote sur l'ensemble** : adopter le texte entier ;
- **vote sur un article** : adopter cet article ;
- **amendement** : adopter la modification qu'il propose. Lis son `dispositif`, qui est la règle juridique, et pas seulement son exposé.
  - Un **amendement de suppression** propose de supprimer un article. Le `titre` de la carte dit alors « Supprimer … », et tu décris ce que contient l'article supprimé.
  - Un amendement qui **réécrit** ou **complète** un article : décris la règle qui serait ajoutée ou changée.
- **proposition de résolution** : approuver la position exprimée par la résolution.

Si tu ne peux pas déterminer avec certitude ce que signifie « pour », mets `lisibilite` à `"incertain"`.

## Format de sortie

Un fichier JSON par vote : `data/interim/ia/etape3/<uid>.json`

```json
{
  "uid": "VTANR5L17V1234",
  "consigne": "etape3_resume v1",
  "theme": "Santé et protection sociale",
  "titre": "Rendre obligatoire un entretien annuel de santé pour chaque enfant",
  "ce_que_ca_change": "Deux ou trois phrases factuelles, concrètes, sans jargon.",
  "contexte": "Amendement à la proposition de loi sur la protection de l'enfance, voté le 6 octobre 2026.",
  "lisibilite": "ok",
  "remarque": null
}
```

### `theme`

Exactement une valeur de cette liste, sans autre choix possible :

- Économie et impôts
- Travail et retraites
- Santé et protection sociale
- Sécurité et justice
- Immigration et nationalité
- Environnement et énergie
- Agriculture et alimentation
- Institutions et démocratie
- Défense et international
- Société et éthique
- Éducation, culture et numérique
- Territoires et outre-mer
- Logement

Choisis le thème du **contenu** de la mesure, pas celui du texte qui la porte. Par exemple, un amendement sur les retraites dans un budget relève de « Travail et retraites ».

### `titre`

- Une phrase à l'infinitif, de 90 caractères maximum, qui décrit l'action votée : « Interdire… », « Créer… », « Supprimer… », « Autoriser… ».
- Pas de question, pas de négation piège.
- Pas de date limite ni de durée (« jusqu'en 2028 », « au plus tard le 28 juin 2026 ») : une fois la date passée, la mesure paraîtrait périmée. Ces dates vont dans `ce_que_ca_change`. Une année qui désigne le texte lui-même reste (« budget de la Sécurité sociale pour 2026 »).
- Vocabulaire courant.

### `ce_que_ca_change`

- Deux ou trois phrases, 400 caractères maximum.
- Ce que la mesure change **concrètement** et **pour qui**.
- Un chiffre clé, seulement s'il figure dans les sources.
- Explique tout terme technique en mots simples.
  - Exemple : « l'article 49.3 » devient « la procédure qui permet au Gouvernement de faire adopter un texte sans vote ».

### `contexte`

- Une phrase : la nature du vote (texte entier, article ou amendement), le texte concerné en mots simples, et la date.
- **Ne dis pas si la mesure a été adoptée ou rejetée.** L'utilisateur le découvre après son vote.

### `lisibilite`

- `"ok"` : la mesure se comprend sans connaissances techniques.
- `"trop_technique"` : impossible de la rendre compréhensible sans jargon. Par exemple, une correction rédactionnelle, un ajustement de crédits budgétaires sans objet identifiable, ou un renvoi entre articles de code.
- `"incertain"` : le sens de « pour » ou le contenu ne peut pas être établi avec certitude à partir des sources.

### `remarque`

Facultatif. Une phrase pour signaler une difficulté au relecteur.

## Interdits absolus

1. Aucun nom de parti, de groupe ou de député : ni dans le titre, ni dans le résumé, ni dans le contexte.
2. Aucun argument pour ou contre, et aucune conséquence présentée comme certaine si elle n'est qu'espérée ou crainte.
3. Aucun adjectif ou adverbe de jugement : « juste », « dangereux », « historique », « enfin », « seulement », « massif »…
4. Aucune information qui ne figure pas dans les sources fournies. N'utilise ni ta mémoire ni le web.
5. N'utilise pas le vocabulaire militant d'un camp. Préfère le terme juridique, expliqué simplement.
6. Rien sur le résultat du vote.

## Méthode de travail

Si tu as besoin d'un script, travaille uniquement dans le dossier privé qui t'est indiqué. Ne lis ni ne modifie jamais les fichiers d'un autre agent.
