# Député d'un jour

**Vote sur de vrais textes de l'Assemblée nationale, et découvre de quels groupes tu es le plus proche, d'après ce qu'ils ont réellement voté.**

Les tests politiques habituels comparent tes opinions à des programmes, c'est-à-dire à des promesses. *Député d'un jour* compare tes réponses à des **votes réels**. Tu votes pour ou contre des mesures votées à l'Assemblée, puis tu vois ton taux d'accord avec chaque groupe, ton siège dans l'hémicycle et ton « député jumeau ».

- 🗳️ Des cartes tirées de 8 609 scrutins publics de la 17e législature.
- ⚖️ Une sélection faite par des règles publiques, sans aucun choix éditorial. Voir [METHODE.md](METHODE.md).
- 🔎 Chaque carte renvoie vers le texte, le scrutin et le débat officiels.
- 🔒 Aucun compte, aucune donnée collectée : tout se calcule sur l'appareil.

## Structure

| Dossier | Contenu |
|---|---|
| `app/` | L'application web (React, Vite, PWA installable) |
| `pipeline/` | Les scripts Python qui transforment les données de l'Assemblée en cartes |
| `consignes/` | Les consignes exactes données aux IA (classement, résumé, vérification, sujets) |
| `data/interim/` | Les données intermédiaires, dont toutes les sorties des IA, publiées pour audit |
| `data/publie/` | Le paquet final de cartes |

## Lancer l'application

```bash
cd app
npm install
npm run dev
```

Pour publier sous un sous-chemin : `BASE=/depute-d-un-jour/ npm run build`. Pour GitHub Pages, il suffit d'activer Pages (Settings → Pages → Source : GitHub Actions), puis de lancer le workflow « Publication » depuis l'onglet Actions.

## Régénérer les données

Voir la section « Reproduire » de [METHODE.md](METHODE.md). Les étapes mécaniques ne demandent que Python 3, sans dépendance externe, et `pdftotext` pour quelques textes. Les étapes rédactionnelles (classement, résumés, vérifications) ont été faites par IA à partir des consignes de `consignes/`. Leurs sorties sont conservées dans `data/interim/ia/`.

## Licences

- Code : MIT, voir [LICENSE](LICENSE).
- Données : Assemblée nationale, [Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/). Les cartes et résumés dérivés sont publiés sous la même licence.

## Signaler une erreur

Une carte te semble fausse ou orientée ? Ouvre une *issue* en indiquant l'identifiant du scrutin (par exemple `VTANR5L17V1234`). Toutes les corrections sont tracées dans le dépôt.
