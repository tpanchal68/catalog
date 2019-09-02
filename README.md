# Fullstack Web Development Nano Degree Final Project:

## Virtual machine setup:

The intent of this project is to setup a linux machine on AWS cloud using lightsail instance to host my web application.
This virtual machine is running Ubuntu 16.04 os.  All updates are installed.
"root" access is blocked.  User account ubuntu, and grader has been created.  Both account are given with sudo permission.
To disable access with password, ssh key are also generated for both users and added appropriately.

To acces web server using non-default port (port 2222) the AWS lightsail instance has been modified as below:

 1. Go to your instance site on https://lightsail.aws.amazon.com
 2. Go to Networking
 3. In the Firewall section add another rule "Custom TCP 2222" and save.


## Web server setup:

It will be hosting web server using apache2.  Since the web application is developed in python 3,
the server will be setup using mod-wsgi for python 3.  Python 3 package, pip3 package, as well as
all necessary packages (mentioned in requirement.txt file) to run the applicaion, are also installed.
The web application is installed in path "/var/www/html/catalog/".  Along with all application files,
mod wsgi required file called catalog.wsgi is also created and copied in same folder.  This is the file
that runs the application.  For application to run in production environment, an application specific
config file named "catalog.conf" is created in path "/etc/apache2/sites-available".  This file contains
all the directives for wsgi to perform to run the web application.  The catalog application is started
using "sudo a2ensite catalog.conf" command from the config file path directory.  Apache server was
restarted using "sudo service apache2 restart" to take catalog.conf execution in effect.  Any errors generated
during accessing the wer server is stored in "/var/log/apache2/error.log" file.

Along with all the project files, all the necessary python packages were installed using "sudo pip install <package>"
command.  Initially, I had lots of struggles getting mod-wsgi to see the packages; eventhough, packages were
installed.  After lots of struggle, I found that I had installed package without sudo mode by simply using
"pip install <package>".  The issue with that is that this way, pip creates ".local" directory in user's homepage;
thus, mod-wsgi just doesn't see it.  Then if you try to install using sudo, pip always tells that the requirement
is satisfied.  To overcome the issue, I had to delete ".local" directory using "rm -r .local" command from
user's home directory.  Then I installed each packages using "sudo pip install <package>", and it worked fine.

### catalog.wsgi file:

#!/usr/bin/python3

```
import sys

sys.path.insert(0, '/var/www/html/catalog')
from catalog_project import app as application
application.secret_key = "super-secret-key"
```

### catalog.conf file:

```
<VirtualHost *:80>
	ServerName localhost
	WSGIScriptAlias / /var/www/html/catalog/catalog.wsgi
	<Directory /var/www/html/catalog/>
		# WSGIApplicationGroup %{GLOBAL}
		WSGIScriptReloading On
		Require all granted
	</Directory>
	ErrorLog ${APACHE_LOG_DIR}/error.log
	LogLevel warn
	CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

## Security setup:

Security for this machine is setup using Ubuntu Firewall (ufw) package.  By default, all ingress and egress ports are blocked.
All necessary ports are opened for web application to perform properly as well as all necessary application upgrade
functionality to function properly.  List of port open are 2222, 80, and 123.


## Accessing web server:

The web server can be access via a browser and using ssh.

1. To access via browser, please type url "http://34.214.235.37/" in any browser.  The page has been tested using
firefox.  Once you are on homepage, you can click links to browse the content.  Since I don't have a
registered domain name, currently, the login page which users Google OAuth, is not working.
2. You can also use ssh protocol "ssh grader@34.214.235.37 -p 2222 -i ~/.ssh/grader" and challenge phrase "grader" to login.

## Catalog App Project:

The intent of this project is to create:

1. Website that displays the catalog of different ethnicity food group.
2. It also displays food dishes available for each ethnicity food group.
3. Furthermore, it also displays recipe for each food dishes.

This application is developed using full stack concepts which includes python, Flask, SQL database, OAuth concepts, html, css, and java script.  The data for the project resides in sqlite database.  Python program connects to database using sqlalchemy connector module.

## Design:

This project provides catalog of ethnic food for users to choose from.  If you are the creator of the food group, it also presents you with options to be able to edit or delete the group.  Once user makes the selection, it presents user with all dishes available.  User can click to any of those dishes to reach to the recipe of that dish.  If you are the creator of the dish, it also presents you with options to be able to edit or delete the dish.  For each of these pages, as long as you are sign in to the website using OAuth method, you will be able to add new item.

This project contains below files:

1. catalog_project.py:
    This file contains all the necessary code for the catalog app project.  It has all the view files.  This is the file user need to execute in order to start web server.
2. recipecatalog.db:
    This is the sqlite database for the project.
3. database_setup.py
    This file contains all the necessary code to connect to sqlite database using SQLAlchemy module. It all the necessary functions to create necessary tables for the project.
4. populate_db.py
    This file contains all the necessary code to populate all necessary database tables with default values for the project.
5. client_secrets.py
    This file contains necessary secrets for google OAuth.
6. requirements.txt
    This file contains all the required packages for the project.
7. README.md
    Current file with all necessary project documentation.
8. static/
    This folder has all the necessary css, images, and java scripts for the project.
9. templates/
    This folder has all the necessary html files for the project.
10. catalog.wsgi
    This is the file use by mod-wsgi application to execute the application in production mode.
11. catalog.conf
    This file is copied here but it doesn't belong here.  It belongs in directory "/etc/apache2/sites-available".
    This file provides catalog application configuration to mod-wsgi module to execute and start the application.


## Execution:

This code has been tested with Python 3.  Below is the syntex to execute:

Should you choose to run code in development mode using python 3:

### Create database:

python3 database_setup.py

### Populate database:

python3 populate_db.py

### Execute code:

python3 catalog_project.py

### Browse website:

Dev server: http://localhost:8000/

Prod server: http://34.214.235.37/

Since dns is not required, I am not going to waste money to get hostname.

## Github Repo:
https://github.com/tpanchal68/catalog

## Third-party Resource:
1. https://stackoverflow.com
2. https://www.codementor.io/abhishake/minimal-apache-configuration-for-deploying-a-flask-app-ubuntu-18-04-phu50a7ft
3. https://flask.palletsprojects.com/en/1.1.x/deploying/mod_wsgi/
4. https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
