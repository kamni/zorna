################################
Personnalisation d'un site ZORNA
################################


************
Introduction
************
ZORNA vous permet de personnaliser les pages d'accueils de votre site en contenus et en graphisme. On distingue deux sortes de pages d'accueil:

* **La page d'accueil publique**

	Cette page est la page d'arrivée sur le site lorsque l'utilisateur n'est pas encore authentifié
* **La page d'accueil privée**

	C'est la page où l'utilisateur sera dirigé une fois authentifié.

ZORNA vous permet de personnaliser ces deux pages pour adopter votre charte graphique ou pour présenter des contenus spécifiques.
Le design de ces pages est du ressort du web master. Les connaissances du HTML, CSS et éventuellement du Javascript sont nécessaires. En plus pour une bonne connaissance du langage du moteur de template de DJANGO est requise pour afficher du contenu provenant de la base de données de ZORNA.

Dans le répertoire "skins/default" à la racine de votre site, on trouve ces deux pages et d'autres:

* **public.html** est la page d'accueil publique
* **private.html** est la page d'accueil privée
* **base.html** pour personnaliser la description, les mots clés ( meta ) du site
* **header.html** contient les menus en haut à droite et le logo du site
* **footer.html** contient le bas de la page
* **page_menu.html** contient les menus de la page

Ce sont des pages HTML qu'on peut modifier et adapter pour le site
Ces pages sont aussi des pages templates, c'est à dire, contiennent des variables et des tags du système de template de DJANGO.

