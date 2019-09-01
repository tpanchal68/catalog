#!/usr/bin/python3

import sys

sys.path.insert(0, '/var/www/html/catalog')
from catalog_project import app as application
application.secret_key = "super-secret-key"

