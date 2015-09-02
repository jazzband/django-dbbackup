"""
Filesystem Storage API.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base import StorageError
from .builtin_django import Storage as DjangoStorage

STORAGE_PATH = 'django.core.files.storage.FileSystemStorage'


class Storage(DjangoStorage):
    """Filesystem API Storage."""
    name = 'Filesystem'

    def __init__(self, server_name=None, **options):
        self._check_filesystem_errors(options)
        super(Storage, self).__init__(storage_path=STORAGE_PATH,
                                      **options)

    def _check_filesystem_errors(self, options):
        """ Check we have all the required settings defined. """
        location = options.get('location')
        if location is None:
            raise StorageError('Filesystem storage requires '
                               'DBBACKUP_STORAGE_OPTIONS["location"] to be '
                               'defined in settings.')
        if location == '':
            raise StorageError('Filesystem storage requires '
                               'DBBACKUP_STORAGE_OPTIONS["location"] to be '
                               'defined with a non empty string.')

        if settings.MEDIA_ROOT and \
                options.get('location', '').startswith(settings.MEDIA_ROOT):
            if not settings.DEBUG:
                msg = "Backups can't be stored in MEDIA_ROOT if DEBUG is "\
                      "False, Please use an another location for your storage."
                raise ImproperlyConfigured(msg)
            msg = "Backups are saved in MEDIA_ROOT, this is a critical issue "\
                  "in production."
            warnings.warn(msg)
