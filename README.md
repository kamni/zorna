Zorna
=====

Open source, Django based CMS and collaborative web portal

[Website](http://en.zornaproject.com)

Installation
------------
The best way to test ZORNA is to use virtualenv. Virtualenv creates a virtual environment and isolate the installation of Python packages needed and the OS.

To do this, install virtualenv as follows:

	$ sudo pip install virtualenv
	
Once the installation is done, create a virtual environment as follows:

	$ cd ~
	$ virtualenv MyENV
	$ cd MyENV
Activate the virtual environment by typing the following command:

	$ source bin/activate      ( ou bin/activate on Windows )
Notice that the prompt changes. This indicates that your virtual environment is active. To disable the environment, you must type the command deactivate.

Continue by typing the following commands (update distribute and create the directory that will contain our test site)

	(myENV)$ easy_install -U distribute
	(myENV)$ mkdir zornasite

[Download the latest release](https://github.com/zorna/zorna/zipball/master)

Unpack the archive in the directory zornasite:

	(myENV)$ tar -xvf zipfile -C zornasite/

Install requirements:

	(myENV)$ pip install -r zornasite/requirements.txt
Execute the following commands to create tables in the database and do the migration:

	(myENV)$ cd zornasite
	(myENV)$ python manage.py syncdb --all
	(myENV)$ python manage.py migrate --fake

When creating tables, you will be asked for information needed to create the super administrator.

Create folder where ZORNA will store media files ( user-uploaded content )

	(myEnv)$ mkdir upload && mkdir upload/ickeditor

Create the following symbolic link for ckeditor static files :

	(myENV)$ cd public
	(myENV)$ ln -s ../../lib/python2.7/site-packages/ckeditor/static/ckeditor/ ckeditor

Finally execute the following command from zornasite directory

	(myENV)$ python manage.py runserver
And fire your browser to:

	http://127.0.0.1:8000/

License
-------
This project is open sourced under [GNU GPL Version 3](http://www.gnu.org/licenses/gpl-3.0.html).

Author
------
Noureddine AYACHI - [Twitter](http://twitter.com/infoafraz) [E-mail](mailto://nayachi@afraz.fr)

