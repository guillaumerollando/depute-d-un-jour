# Consigne IA — Étape 3 : titre d'accroche d'un texte entier (METHODE §5)

Version 1 — 2026-10-10. Cette consigne est publiée telle quelle, sans modification.

## Rôle

Certaines cartes portent sur l'**ensemble d'une loi**, et leur titre ne nomme que la loi : « Adopter la loi assouplissant plusieurs règles du métier d'agriculteur ». On ne comprend pas, à la première lecture, ce qu'on vote.

Ton travail : réécrire ce titre pour qu'il dise **en une phrase ce que fait la loi**, à partir de ses **mesures phares**. Le détail reste dans le résumé.

## Données

- Les textes affichés de la carte : `app/public/data/cartes.json` (titre, `ce_que_ca_change`, `aujourdhui`, `contexte`, arguments).
- Le débat avant le vote : `data/interim/extraits/<uid>.json` (`interventions`) et, s'il existe, `data/interim/debats_elargis/<uid>.json`.
- Le texte officiel : voir `data/interim/sources.json`.

## Choix des mesures phares

Ce n'est pas un choix personnel. Les mesures phares sont **celles dont les groupes ont le plus parlé dans le débat avant le vote**, tous camps confondus :
1. Relève les mesures citées dans les interventions, et par combien de groupes différents chacune est citée.
2. Ne garde que les mesures qui figurent dans le résumé de la carte : le titre annonce ce que la carte explique.
3. Parmi elles, retiens **une ou deux** mesures, les plus citées. À égalité, prends celle qui figure en premier dans le résumé.

## Règles du titre

- Une phrase à l'infinitif, 90 caractères maximum, qui commence par le verbe de la mesure : « Réautoriser… », « Interdire… », « Créer… ».
- Pas de « Adopter la loi… ».
- Voter « pour » le titre doit rester voter pour la loi : le titre décrit ce que la loi fait, rien d'autre.
- Les termes exacts du résumé : ni plus large, ni plus étroit, ni plus fort.
- Pas de date limite (règle de `consignes/etape3_resume.md`). Une année qui désigne le texte reste (« budget pour 2026 »).
- Tous les autres interdits de `consignes/etape3_resume.md` s'appliquent : aucun nom de parti, aucun adjectif de jugement.
- **Un budget** (État, Sécurité sociale) ou une loi de programmation : nomme le budget, puis une ou deux mesures phares si elles tiennent dans la longueur. Sinon, garde le titre.
- Si le titre actuel nomme déjà clairement ce que fait la loi, garde-le.

## Format de sortie

`data/interim/ia/etape3_accroche/<uid>.json`

```json
{
  "uid": "VTANR5L17V1234",
  "consigne": "etape3_accroche v1",
  "modifie": true,
  "mesures_citees": [{ "mesure": "…", "groupes": ["…", "…"] }],
  "titre": "…"
}
```

Les groupes sont désignés par leur sigle, uniquement dans ce fichier de travail ; le titre n'en contient jamais.
