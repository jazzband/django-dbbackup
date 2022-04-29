"""
Configuration and launcher for dbbackup tests.
"""
import os
import sys
import tempfile

from dotenv import load_dotenv

test = len(sys.argv) <= 1 or sys.argv[1] == "test"
if not test:
    load_dotenv()

DEBUG = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTAPP_DIR = os.path.join(BASE_DIR, "testapp/")
BLOB_DIR = os.path.join(TESTAPP_DIR, "blobs/")

ADMINS = (("ham", "foo@bar"),)
ALLOWED_HOSTS = ["*"]
MIDDLEWARE_CLASSES = ()
ROOT_URLCONF = "dbbackup.tests.testapp.urls"
SECRET_KEY = "it's a secret to everyone"
SITE_ID = 1
MEDIA_ROOT = os.environ.get("MEDIA_ROOT") or tempfile.mkdtemp()
INSTALLED_APPS = (
    "dbbackup",
    "dbbackup.tests.testapp",
)

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", ":memory:"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
    }
}
if os.environ.get("CONNECTOR"):
    CONNECTOR = {"CONNECTOR": os.environ["CONNECTOR"]}
    DBBACKUP_CONNECTORS = {"default": CONNECTOR}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

SERVER_EMAIL = "dbbackup@test.org"

DBBACKUP_GPG_RECIPIENT = "test@test"
DBBACKUP_GPG_ALWAYS_TRUST = (True,)

DBBACKUP_STORAGE = os.environ.get("STORAGE", "dbbackup.tests.utils.FakeStorage")
DBBACKUP_STORAGE_OPTIONS = dict(
    [
        keyvalue.split("=")
        for keyvalue in os.environ.get("STORAGE_OPTIONS", "").split(",")
        if keyvalue
    ]
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"handlers": ["console"], "level": "DEBUG"},
    "handlers": {
        "console": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "loggers": {
        "django.db.backends": {
            # uncomment to see all queries
            # 'level': 'DEBUG',
            "handlers": ["console"],
        }
    },
}
