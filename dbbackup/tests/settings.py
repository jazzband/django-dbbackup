"""
Configuration and launcher for dbbackup tests.
"""
import os
import tempfile
import dj_database_url

DEBUG = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTAPP_DIR = os.path.join(BASE_DIR, 'testapp/')
BLOB_DIR = os.path.join(TESTAPP_DIR, 'blobs/')

ADMINS = (
    ('ham', 'foo@bar'),
)
ALLOWED_HOSTS = ['*']
MIDDLEWARE_CLASSES = ()
ROOT_URLCONF = 'dbbackup.tests.testapp.urls'
SECRET_KEY = "it's a secret to everyone"
SITE_ID = 1
MEDIA_ROOT = os.environ.get('MEDIA_ROOT') or tempfile.mkdtemp()
INSTALLED_APPS = (
    'dbbackup',
    'dbbackup.tests.testapp',
)

DATABASE = dj_database_url.config(default='sqlite:///%s' %
                                  tempfile.mktemp())
DATABASES = {'default': DATABASE}
if os.environ.get('CONNECTOR'):
    CONNECTOR = {'CONNECTOR': os.environ['CONNECTOR']}
    DBBACKUP_CONNECTORS = {'default': CONNECTOR}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SERVER_EMAIL = 'dbbackup@test.org'

DBBACKUP_GPG_RECIPIENT = "test@test"
DBBACKUP_GPG_ALWAYS_TRUST = True,

DBBACKUP_STORAGE = os.environ.get('STORAGE', 'dbbackup.tests.utils.FakeStorage')
DBBACKUP_STORAGE_OPTIONS = dict([keyvalue.split('=') for keyvalue in
                                 os.environ.get('STORAGE_OPTIONS', '').split(',')
                                 if keyvalue])
