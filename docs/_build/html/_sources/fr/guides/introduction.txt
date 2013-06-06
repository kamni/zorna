##########################
ZORNA Présentation
##########################

************
Introduction
************
ZORNA est une puissante plate-forme pour le travail collaboratif et la gestion de contenus.
Développé en utilisant le framework DJANGO, ZORNA fournit une architecture simple et extensible qui permet, par son API, de lui ajouter de nouvelles fonctionnalités pour des besoins spécifiques.

Le but de ce guide est de fournir assez d'informations pour commprendre comment fonctionne ZORNA.

****************
Caractéristiques
****************
* Pages de navigation hiérarchiques
* Editeur WYSIWYG 
* Publication d'articles organisés par catétgories
* Publication d'un même article dans plusieurs catégories
* Ajout de fichiers joints à l'article
* Droits d'accès sur les catégories (Lecteur/Editeur)
* Gestion et partage de fichiers (personnels et partagés)
* Gestion des utilisateurs et des groupes d'utilisateurs
* Partage d'agendas
* FAQs
* Notes
* Un générateur de formulaires WEB
* Authentification LDAP
* ...

On peut développer facilement des modules pour ajouter de nouvelles fonctionnalités. Quelques exemples de modules développés par AFRAZ_ :

* Module de gestion de projets (Tâches, Agenda, Gantt, etc...)
* Module de gestion électronique de documents (GED)
* Module de visioconférence s'appuyant sur BigBlueButton
* ...

.. _AFRAZ: http://www.afraz.fr

************
Installation
************
ZORNA nécessite Python 2.7. Vérifiez donc que vous avez bien Python installé sur votre machine.

La meilleure façon de tester ZORNA est d'utilisez virtualenv. Virtualenv permet de créer un environnement virtuel et d'isoler l'installation de Python et des packages nécessaires de l'OS.

Pour cela, installer virtualenv comme suit:

.. code-block:: bash

	$ sudo pip install virtualenv
	
Une fois l'installation faite, créez un environnement virtuel comme suit:

.. code-block:: bash

	$ cd ~
	$ virtualenv MyENV
	$ cd MyENV

Activez l'environnement virtuel en tapant la commande suivante:

.. code-block:: bash

	$ source bin/activate      ( ou bin/activate on Windows )

Vous remarquez que le prompt change. Ceci indique que votre environnement virtuel est actif. Pour désactiver l'environnement, il faut taper la commande **deactivate**.

Continuez en tapant les commandes suivantes ( mise à jour de distribute et création du répertoire qui contiendra notre site de test )

.. code-block:: bash

	(myENV)$ easy_install -U distribute
	(myENV)$ mkdir zornasite

Téléchargez la dernière version_ et décompressez le contenu de l'archive dans le répertoire zornasite.

.. _version: https://github.com/zorna/zorna/archive/master.zip

Installez les requirements:

.. code-block:: bash

	(myENV)$ pip install -r zornasite/requirements.txt

Lancez les commandes suivantes pour créer les tables de la base de données et faire la migration:

.. code-block:: bash

	(myENV)$ cd zornasite
	(myENV)$ python manage.py syncdb --all
	(myENV)$ python manage.py migrate --fake

Lors de la création des tables, il vous sera demandé les informations nécessaires pour créer le super administrateur.

Créez le répertoire où ZORNA stockera les documents chargés par l'utilisateur:

.. code-block:: bash

	(myEnv)$ mkdir upload && mkdir upload/ickeditor

Créez les liens symboliques suivants:

.. code-block:: bash

	(myENV)$ cd public
	(myENV)$ ln -s ../../lib/python2.7/site-packages/ckeditor/static/ckeditor/ ckeditor

Enfin, dans le répertoire zornasite, lancez la commande suivante:

.. code-block:: bash

	(myENV)$ python manage.py runserver

Et pointez votre navigateur vers l'url!:

	http://127.0.0.1:8000/



