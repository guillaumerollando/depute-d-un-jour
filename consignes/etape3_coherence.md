# Consigne IA — Étape 3 : cohérence d'une carte (METHODE §5)

Version 1 — 2026-10-10. Cette consigne est publiée telle quelle, sans modification.

## Rôle

Chaque carte affiche plusieurs textes, écrits à des étapes différentes :
- le titre ;
- le résumé (`ce_que_ca_change`) ;
- la situation actuelle (`aujourdhui`) ;
- le contexte du vote ;
- les arguments pour et contre.

Lus ensemble, ces textes doivent **se répondre** : mêmes mots pour les mêmes choses, mêmes publics, mêmes chiffres. Ton travail est de les harmoniser, **sans rien changer au fond**.

## Données

- `data/interim/coherence_entree.json` : pour chaque `uid`, les textes affichés.
- En cas de doute sur le bon terme : la fiche du vote `data/interim/extraits/<uid>.json` et le texte officiel (voir `data/interim/sources.json`).

## Ce que tu corriges

1. **Un même objet désigné de plusieurs façons.** Par exemple, « agents des services publics de transport » dans le résumé, mais « fonctionnaires » dans un argument. Choisis le terme **exact**, celui des sources, et emploie-le partout. Un terme plus large ou plus étroit que la réalité est une erreur.
2. **Des contradictions** entre les textes : chiffre, date, public concerné, obligation ou possibilité.
3. **Un texte qui ne répond pas aux autres.** Par exemple, une situation « aujourd'hui » qui parle d'autre chose que ce que la mesure change, ou un argument qui vise une autre mesure que celle du titre.

## Ce que tu ne fais pas

- Tu n'ajoutes aucune information et tu n'en retires aucune, sauf pour supprimer une contradiction.
- Tu ne changes pas le sens de « pour » du titre.
- Tu ne rends aucun argument plus fort ou plus faible. Un argument reste fidèle à ce qu'a dit le député.
- Tu respectes tous les interdits de `consignes/etape3_resume.md` et les longueurs maximales :
  - titre : 90 caractères ;
  - `ce_que_ca_change` : 400 ;
  - `aujourdhui` : 180 ;
  - chaque argument : 160.
- Si la carte est déjà cohérente, tu ne la changes pas.

## Format de sortie

`data/interim/ia/etape3_coherence/<uid>.json`

```json
{
  "uid": "VTANR5L17V1234",
  "consigne": "etape3_coherence v1",
  "modifie": true,
  "problemes": ["Le résumé parle des agents des services publics de transport, un argument dit « fonctionnaires »."],
  "corrections": { "argument_pour": "…" }
}
```

`corrections` ne contient que les champs modifiés, parmi `titre`, `ce_que_ca_change`, `aujourdhui`, `contexte`, `argument_pour` et `argument_contre`.
