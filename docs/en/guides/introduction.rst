##########################
Getting started with ZORNA
##########################

************
Introduction
************
ZORNA is a powerful platform for collaboration and content management.
Developed using the Django framework, ZORNA provides a simple and extensible
architecture that allows, through its API, to add new features for specific
needs.

The purpose of this guide is to provide enough information to understand how
ZORNA works.

****************
Features
****************
* Hierarchical page navigation
* WYSIWYG editor
* Publication of articles organized by category
* Publication of an article in multiple categories
* Attaching files to an article
* Access rights on articles (reading/editing)
* Management and sharing of files (personal and group)
* Managing users and user groups
* Sharing calendars
* FAQs
* Notes
* A webform generator
* LDAP Authentication
* ...

It is easy for a developer to create modules to add new features. Some examples
of modules developed by AFRAZ_ :

* Module for managing projects (Tasks, Calendar, Gantt charts, etc ...)
* Module for managing electronic documents
* Videoconferencing module based on BigBlueButton
* ...

.. _AFRAZ: http://www.afraz.fr

************
Installation
************
ZORNA requires Python 2.7. You should verify that you have the correct Python
installed on your machine.

The best way to test ZORNA is to use virtualenv. Virtualenv allows you to
create a virtual environment that separates the Python packages for ZORNA from
those on your OS.

To do this, install virtualenv as follows:

.. code-block:: bash

	$ sudo pip install virtualenv

Once the installation is done, create a virtual environment as follows:

.. code-block:: bash

	$ cd ~
	$ virtualenv MyENV
	$ cd MyENV

Activate the virtual environment by typing the following command:

.. code-block:: bash

	$ source bin/activate      (or bin/activate on Windows)

Notice that the prompt changes. This indicates that your virtual environment is
active. To disable the environment, you must type the command **deactivate**.

Continue by typing the following commands (to update distribute and create the
directory that will contain your test site):

.. code-block:: bash

	(myENV)$ easy_install -U distribute
	(myENV)$ mkdir zornasite

Download the latest version_ and unpack the contents of the archive in the
directory zornasite.

.. _version: https://github.com/zorna/zorna/archive/master.zip

Install the requirements:

.. code-block:: bash

	(myENV)$ pip install -r zornasite/requirements.txt

Create the directory where ZORNA will store documents uploaded by the user:

.. code-block:: bash

    (myEnv)$ mkdir -p upload/ickeditor

Create the following symbolic links:

.. code-block:: bash

    (myENV)$ cd public
    (myENV)$ ln -s ../../lib/python2.7/site-packages/ckeditor/static/ckeditor/ ckeditor

Run the following commands to create the tables in the database and do the
migration:

.. code-block:: bash

	(myENV)$ cd zornasite
	(myENV)$ python manage.py syncdb --all
	(myENV)$ python manage.py migrate --fake

When creating tables, you will be asked for information needed to create the
superuser.

Finally, in the zornasite directory, run the following command:

.. code-block:: bash

	(myENV)$ python manage.py runserver

And point your browser to the url:

	http://127.0.0.1:8000/



