"""
Azure Storage object.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from .base import StorageError
from .builtin_django import Storage as DjangoStorage

STORAGE_PATH = 'azure_storage.storage.AzureStorage'


class Storage(DjangoStorage):
    """Filesystem API Storage."""
    def __init__(self, server_name=None, **options):
        self.name = 'AzureStorage'
        super(Storage, self).__init__(
            storage_path=STORAGE_PATH,
            **options
        )
