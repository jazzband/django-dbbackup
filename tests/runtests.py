#!/usr/bin/env python
"""
Configuration and launcher for dbbackup tests.
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import call_command

# Add testproject dbbackup in path
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(HERE)
sys.path[0:0] = [HERE, PARENT_DIR]

# Settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'tests/media')
INSTALLED_APPS = (
    'testapp',
    'dbbackup',
)
GPG_RECIPIENT = "test@test"


settings.configure(
    ADMIN=('foo@bar'),
    ALLOWED_HOSTS=['*'],
    MEDIA_ROOT=MEDIA_ROOT,
    MIDDLEWARE_CLASSES=(),
    # CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    INSTALLED_APPS=INSTALLED_APPS,
    DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}},
    ROOT_URLCONF='testapp.urls',
    SECRET_KEY="it's a secret to everyone",
    SITE_ID=1,
    BASE_DIR=BASE_DIR,
    DBBACKUP_GPG_RECIPIENT=GPG_RECIPIENT,
    DBBACKUP_GPG_ALWAYS_TRUST=True,
    DBBACKUP_STORAGE='dbbackup.tests.utils'
)


def main():
    if django.VERSION >= (1, 7):
        django.setup()
    command_args = sys.argv[1:] or ['test', 'dbbackup']
    call_command(*command_args)
    exit(0)

if __name__ == '__main__':
    main()
