# DO NOT IMPORT THIS BEFORE django.configure() has been run!

import os
import tempfile
import socket
import warnings
from django.conf import settings

DATABASES = getattr(settings, 'DBBACKUP_DATABASES', list(settings.DATABASES.keys()))

# Fake host
HOSTNAME = getattr(settings, 'DBBACKUP_HOSTNAME', socket.gethostname())

# Directory to use for temporary files
TMP_DIR = getattr(settings, 'DBBACKUP_TMP_DIR', tempfile.gettempdir())
TMP_FILE_MAX_SIZE = getattr(settings, 'DBBACKUP_TMP_FILE_MAX_SIZE', 10*1024*1024)
TMP_FILE_READ_SIZE = getattr(settings, 'DBBACKUP_TMP_FILE_READ_SIZE', 1024*1000)

# Days to keep
CLEANUP_KEEP = getattr(settings, 'DBBACKUP_CLEANUP_KEEP', 10)
CLEANUP_KEEP_MEDIA = getattr(settings, 'DBBACKUP_CLEANUP_KEEP_MEDIA', CLEANUP_KEEP)

MEDIA_PATH = getattr(settings, 'DBBACKUP_MEDIA_PATH', settings.MEDIA_ROOT)

DATE_FORMAT = getattr(settings, 'DBBACKUP_DATE_FORMAT', '%Y-%m-%d-%H%M%S')
FORCE_ENGINE = getattr(settings, 'DBBACKUP_FORCE_ENGINE', '')
FILENAME_TEMPLATE = getattr(settings, 'DBBACKUP_FILENAME_TEMPLATE', '{databasename}-{servername}-{datetime}.{extension}')
MEDIA_FILENAME_TEMPLATE = getattr(settings, 'DBBACKUP_MEDIA_FILENAME_TEMPLATE', '{servername}-{datetime}.{extension}')

READ_FILE = '<READ_FILE>'
WRITE_FILE = '<WRITE_FILE>'

# Environment dictionary
BACKUP_ENVIRONMENT = {}
RESTORE_ENVIRONMENT = {}

FAILURE_RECIPIENTS = getattr(settings, 'DBBACKUP_FAILURE_RECIPIENTS', settings.ADMINS)
SEND_EMAIL = getattr(settings, 'DBBACKUP_SEND_EMAIL', True)
SERVER_EMAIL = getattr(settings, 'DBBACKUP_SERVER_EMAIL', settings.SERVER_EMAIL)

GPG_ALWAYS_TRUST = getattr(settings, 'DBBACKUP_GPG_ALWAYS_TRUST', False)
GPG_RECIPIENT = GPG_ALWAYS_TRUST = getattr(settings, 'DBBACKUP_GPG_RECIPIENT', None)

STORAGE = getattr(settings, 'DBBACKUP_STORAGE', 'dbbackup.storage.filesystem_storage')
BUILTIN_STORAGE = getattr(settings, 'DBBACKUP_BUILTIN_STORAGE', None)
STORAGE_OPTIONS = getattr(settings, 'DBBACKUP_STORAGE_OPTIONS', {})

CONNECTORS = getattr(settings, 'DBBACKUP_CONNECTORS', {})

# Logging
import logging, dbbackup.log
LOGGING = getattr(settings, 'DBBACKUP_LOGGING', dbbackup.log.DEFAULT_LOGGING)
LOG_CONFIGURATOR = logging.config.DictConfigurator(LOGGING)
LOG_CONFIGURATOR.configure()


# Deprecation
if hasattr(settings, 'DBBACKUP_BACKUP_DIRECTORY'):  # pragma: no cover
    BACKUP_DIRECTORY = STORAGE_OPTIONS['location'] = \
        getattr(settings, 'DBBACKUP_BACKUP_DIRECTORY', os.getcwd())
    warnings.warn("DBBACKUP_BACKUP_DIRECTORY is deprecated, use DBBACKUP_STORAGE_OPTIONS['location']", DeprecationWarning)

if hasattr(settings, 'DBBACKUP_FAKE_HOST'):  # pragma: no cover
    warnings.warn("DBBACKUP_FAKE_HOST is deprecated, use DBBACKUP_HOSTNAME", DeprecationWarning)
    HOSTNAME = settings.DBBACKUP_FAKE_HOST

UNSED_AWS_SETTINGS = ('DIRECTORY',)
DEPRECATED_AWS_SETTINGS = (
    ('BUCKET', 'bucket_name'),
    ('ACCESS_KEY', 'access_key'),
    ('SECRET_KEY', 'secret_key'),
    ('DOMAIN', 'host'),
    ('IS_SECURE', 'use_ssl'),
    ('SERVER_SIDE_ENCRYPTION', 'encryption'),
)
if hasattr(settings, 'DBBACKUP_S3_BUCKET'):
    for old_suffix, new_key in DEPRECATED_AWS_SETTINGS:
        old_key = 'DBBACKUP_S3_%s' % old_suffix
        if hasattr(settings, old_key):
            STORAGE_OPTIONS[new_key] = getattr(settings, old_key)
            msg = "%s is deprecated, use DBBACKUP_STORAGE_OPTIONS['%s']" % (old_key, new_key)
            warnings.warn(msg, DeprecationWarning)
    for old_suffix in UNSED_AWS_SETTINGS:
        if hasattr(settings, 'DBBACKUP_S3_%s' % old_suffix):
            msg = "DBBACKUP_S3_%s is now useless" % old_suffix
            warnings.warn(msg, DeprecationWarning)
    del old_suffix, new_key
