# DO NOT IMPORT THIS BEFORE django.configure() has been run!

import tempfile
import socket
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
FILENAME_TEMPLATE = getattr(settings, 'DBBACKUP_FILENAME_TEMPLATE', '{databasename}-{servername}-{datetime}.{extension}')

FAILURE_RECIPIENTS = getattr(settings, 'DBBACKUP_FAILURE_RECIPIENTS', settings.ADMINS)
SEND_EMAIL = getattr(settings, 'DBBACKUP_SEND_EMAIL', True)
SERVER_EMAIL = getattr(settings, 'DBBACKUP_SERVER_EMAIL', settings.SERVER_EMAIL)

GPG_ALWAYS_TRUST = getattr(settings, 'DBBACKUP_GPG_ALWAYS_TRUST', False)
GPG_RECIPIENT = GPG_ALWAYS_TRUST = getattr(settings, 'DBBACKUP_GPG_RECIPIENT', None)

STORAGE = getattr(settings, 'DBBACKUP_STORAGE', 'dbbackup.storage.filesystem_storage')
STORAGE_OPTIONS = getattr(settings, 'DBBACKUP_STORAGE_OPTIONS', {})

CONNECTORS = getattr(settings, 'DBBACKUP_CONNECTORS', {})

# Logging
from logging import config as log_config
import dbbackup.log
LOGGING = getattr(settings, 'DBBACKUP_LOGGING', dbbackup.log.DEFAULT_LOGGING)
LOG_CONFIGURATOR = log_config.DictConfigurator(LOGGING)
LOG_CONFIGURATOR.configure()
