import re
from django.core.checks import Warning, register, Tags
from django.utils.six import string_types
from dbbackup import settings

W001 = Warning('Invalid HOSTNAME parameter',
               hint='Set a non empty string to this settings.DBBACKUP_HOSTNAME',
               id='dbbackup.W001')
W002 = Warning('Invalid STORAGE parameter',
               hint='Set a valid path to a storage in settings.DBBACKUP_STORAGE',
               id='dbbackup.W002')
W003 = Warning('Invalid FILENAME_TEMPLATE parameter',
               hint='Include {datetime} to settings.DBBACKUP_FILENAME_TEMPLATE',
               id='dbbackup.W003')
W004 = Warning('Invalid DATE_FORMAT parameter',
               hint='settings.DBBACKUP_DATE_FORMAT can contain only [A-Za-z0-9%_-]',
               id='dbbackup.W004')


@register(Tags.compatibility)
def check_settings(app_configs, **kwargs):
    errors = []
    if not settings.HOSTNAME:
        errors.append(W001)

    if not settings.STORAGE or not isinstance(settings.STORAGE, string_types):
        errors.append(W002)

    if not callable(settings.FILENAME_TEMPLATE):
        if '{datetime}' not in settings.FILENAME_TEMPLATE:
            errors.append(W003)

    if re.search(r'[^A-Za-z0-9%_-]', settings.DATE_FORMAT):
        errors.append(W004)

    return errors
