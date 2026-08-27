title: Éditer une page
tags: guide, markdown

Une page est un fichier Markdown précédé de quelques métadonnées. Le bouton *Éditer* ouvre l'éditeur, qui écrit le fichier de la langue annoncée dans la barre d'onglets.

## Métadonnées

Les lignes qui précèdent la première ligne vide décrivent la page :

| Clé | Rôle |
|-----|------|
| `title` | Titre affiché en tête de page, dans l'index et dans les résultats de recherche |
| `tags` | Mots-clés séparés par des virgules |

```markdown
title: Éditer une page
tags: guide, markdown

Le contenu commence ici.
```

## Liens

Un lien interne s'écrit à la manière d'un wiki, `[[home|Accueil]]`, ou comme un lien Markdown ordinaire vers [une autre page](/help/guides/languages/). Dans les deux cas l'adresse ne porte pas de code de langue : le wiki sert la variante qui correspond à la langue du lecteur.

## Images

Les images sont déposées depuis la page *Fichiers*, puis appelées par leur URL :

![Le logo de Flask](/help/files/flask-logo.png "Le logo de Flask")

## Table des matières

Les titres de niveau 2 et 3 alimentent la table des matières affichée à droite de la page.
