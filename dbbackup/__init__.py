"""Management commands to help backup and restore a project database and media"""

import django

VERSION = (3, 3, 0)
__version__ = '.'.join([str(i) for i in VERSION])
__author__ = 'Michael Shepanski'
__email__ = 'mjs7231@gmail.com'
__url__ = 'https://github.com/django-dbbackup/django-dbbackup'

if django.VERSION < (3, 2):
    default_app_config = 'dbbackup.apps.DbbackupConfig'
