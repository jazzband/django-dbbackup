"""
Abstract Storage class.
"""
from importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from .. import settings


def get_storage(path=None, options={}):
    """
    Get the specified storage configured with options.

    :param path: Path in Python dot style to module containing the storage
                 class. If empty settings.DBBACKUP_STORAGE will be used.
    :type path: ``str``

    :param options: Parameters for configure the storage, if empty
                    settings.DBBACKUP_STORAGE_OPTIONS will be used.
    :type options: ``dict``

    :return: Storage configured
    :rtype: :class:`.Storage`
    """
    path = path or settings.STORAGE
    options = options or settings.STORAGE_OPTIONS
    if not path:
        raise ImproperlyConfigured('You must specify a storage class using '
                                   'DBBACKUP_STORAGE settings.')
    storage_module = import_module(path)
    return storage_module.Storage(**options)


class StorageError(Exception):
    pass


class BaseStorage(object):
    """Abstract storage class."""
    def __init__(self, server_name=None):
        if not self.name:
            raise Exception("Programming Error: storage.name not defined.")

    def __str__(self):
        return self.name

    # TODO: Remove in favor of get_storage
    @classmethod
    def storage_factory(cls):
        return get_storage()

    def latest_backup(self, regex):
        """Return the latest backup file matching regex."""
        pass

    def backup_dir(self):
        raise NotImplementedError("Programming Error: backup_dir() not defined.")

    def delete_file(self, filepath):
        raise NotImplementedError("Programming Error: delete_file() not defined.")

    def list_backups(self, database):
        raise NotImplementedError("Programming Error: list_backups() not defined.")

    def write_file(self, filehandle, filename):
        raise NotImplementedError("Programming Error: write_file() not defined.")

    def read_file(self, filepath):
        raise NotImplementedError("Programming Error: read_file() not defined.")
