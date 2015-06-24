# DO NOT IMPORT THIS BEFORE django.configure() has been run!

import os
from django.conf import settings

DATABASES = getattr(settings, 'DBBACKUP_DATABASES', list(settings.DATABASES.keys()))

BACKUP_DIRECTORY = getattr(settings, 'DBBACKUP_BACKUP_DIRECTORY', os.getcwd())

# Fake host
DBBACKUP_FAKE_HOST = getattr(settings, 'DBBACKUP_FAKE_HOST', 'django-dbbackup')

# Directory to use for temporary files
TMP_DIR = getattr(settings, 'DBBACKUP_TMP_DIR', '/tmp')

# Days to keep backups
CLEANUP_KEEP = getattr(settings, 'DBBACKUP_CLEANUP_KEEP', 10)

# Days to keep backed up media (default: same as CLEANUP_KEEP)
CLEANUP_KEEP_MEDIA = getattr(settings, 'DBBACKUP_CLEANUP_KEEP_MEDIA', CLEANUP_KEEP)

MEDIA_PATH = getattr(settings, 'DBBACKUP_MEDIA_PATH', settings.MEDIA_ROOT)

DATE_FORMAT = getattr(settings, 'DBBACKUP_DATE_FORMAT', '%Y-%m-%d-%H%M%S')
SERVER_NAME = getattr(settings, 'DBBACKUP_SERVER_NAME', '')
FORCE_ENGINE = getattr(settings, 'DBBACKUP_FORCE_ENGINE', '')
FILENAME_TEMPLATE = getattr(settings, 'DBBACKUP_FILENAME_TEMPLATE', '{databasename}-{servername}-{datetime}.{extension}')

READ_FILE = '<READ_FILE>'
WRITE_FILE = '<WRITE_FILE>'

# Environment dictionary
BACKUP_ENVIRONMENT = {}
RESTORE_ENVIRONMENT = {}

# TODO: Unify backup and restore commands to support adding extra flags instead
# of just having full statements.

SQLITE_BACKUP_COMMANDS = getattr(settings, 'DBBACKUP_SQLITE_BACKUP_COMMANDS', [
    [READ_FILE, '{databasename}'],
])
SQLITE_RESTORE_COMMANDS = getattr(settings, 'DBBACKUP_SQLITE_RESTORE_COMMANDS', [
    [WRITE_FILE, '{databasename}'],
])

# TODO: Why are these even here? The MySQL commands are built in a dynamic
# fashion through MySQLSettings
MYSQL_BACKUP_COMMANDS = getattr(settings, 'DBBACKUP_MYSQL_BACKUP_COMMANDS', None)
MYSQL_RESTORE_COMMANDS = getattr(settings, 'DBBACKUP_MYSQL_RESTORE_COMMANDS', None)

POSTGRESQL_BACKUP_COMMANDS = getattr(settings, 'DBBACKUP_POSTGRESQL_BACKUP_COMMANDS', None)
POSTGRESQL_RESTORE_COMMANDS = getattr(settings, 'DBBACKUP_POSTGRESQL_RESTORE_COMMANDS', None)
POSTGRESQL_RESTORE_SINGLE_TRANSACTION = getattr(settings, 'DBBACKUP_POSTGRESQL_RESTORE_SINGLE_TRANSACTION', True)
POSTGIS_SPATIAL_REF = getattr(settings, 'DBBACKUP_POSTGIS_SPACIAL_REF', False)

FAILURE_RECIPIENTS = getattr(settings, 'DBBACKUP_FAILURE_RECIPIENTS', settings.ADMINS)
SEND_EMAIL = getattr(settings, 'DBBACKUP_SEND_EMAIL', True)
SERVER_EMAIL = getattr(settings, 'DBBACKUP_SERVER_EMAIL', settings.SERVER_EMAIL)

GPG_ALWAYS_TRUST = getattr(settings, 'DBBACKUP_GPG_ALWAYS_TRUST', False)

GPG_RECIPIENT = GPG_ALWAYS_TRUST = getattr(settings, 'DBBACKUP_GPG_RECIPIENT', None)
