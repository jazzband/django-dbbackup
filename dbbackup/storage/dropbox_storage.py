"""
Dropbox API Storage object.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .base import StorageError
from .builtin_django import Storage as DjangoStorage

STORAGE_PATH = 'storages.backends.dropbox.DropBoxStorage'


class Storage(DjangoStorage):
    """Dropbox API Storage."""
    name = 'Dropbox'
    default_path = '/'

    def __init__(self, server_name=None, **options):
        self._check_settings(options)
        self._check_settings(options)
        super(Storage, self).__init__(
            storage_path=STORAGE_PATH,
            oauth2_access_token=options['oauth2_access_token'])

    def _check_settings(self, options):
        """Check we have all the required settings defined."""
        required_args = ('oauth2_access_token',)
        err_msg = "%s storage requires settings.DBBACKUP_STORAGE_OPTIONS['%s'] to be define"
        for arg in required_args:
            if arg not in options:
                raise StorageError(err_msg % (self.name, arg))
