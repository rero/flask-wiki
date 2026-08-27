title: Gérer les langues
tags: guide, langues

Chaque page appartient à une langue : le fichier porte un code de langue — `home_fr.md`, `home_it.md` — alors que l'URL n'en porte pas. `/help/home` sert donc la variante qui correspond à la langue du lecteur.

Cette page-ci n'existe qu'en français. Si vous la lisez dans une autre langue, le bandeau au-dessus vous le dit : elle vous est servie par la cascade de repli décrite ci-dessous.

## Quand la traduction manque

Le wiki parcourt `WIKI_FALLBACK_LANGUAGES` dans l'ordre et sert la première traduction qu'il trouve. Pour un lecteur italien, avec la configuration de cette démonstration :

1. `guides/languages_it.md` — absent ;
2. `guides/languages_en.md` — absent ;
3. `guides/languages_fr.md` — servi, avec un bandeau.

Une page ne répond 404 que si elle n'existe dans aucune langue.

## Ajouter une traduction

Dans l'éditeur, le menu *Edit in* ouvre la même page dans une autre langue. La barre d'onglets rappelle en permanence quelle variante sera écrite, et le formulaire part vide tant que la traduction n'existe pas : il n'y a pas de risque d'écraser le texte d'une autre langue.

Voir aussi [[guides/editing|Éditer une page]].
