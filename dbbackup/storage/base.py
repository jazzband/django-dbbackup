"""
Abstract Storage class.
"""
from django.conf import settings
from importlib import import_module


class StorageError(Exception):
    pass


###################################
#  Abstract Storage Class
###################################

class BaseStorage:
    """ Abstract storage class. """
    BACKUP_STORAGE = getattr(settings, 'DBBACKUP_STORAGE', 'dbbackup.storage.filesystem_storage')

    def __init__(self, server_name=None):
        if not self.name:
            raise Exception("Programming Error: storage.name not defined.")

    def __str__(self):
        return self.name

    @classmethod
    def storage_factory(cls):
        """ Return the correct storage object based on the specified Django settings. """
        if not cls.BACKUP_STORAGE:
            raise StorageError('You must specify a storage class using DBBACKUP_STORAGE.')
        storage_module = import_module(cls.BACKUP_STORAGE)
        return storage_module.Storage()

    def latest_backup(self, regex):
        """ Return the latest backup file matching regex. """
        pass

    ###################################
    #  Storage Access Methods
    ###################################

    def backup_dir(self):
        raise StorageError("Programming Error: backup_dir() not defined.")

    def delete_file(self, filepath):
        raise StorageError("Programming Error: delete_file() not defined.")

    def list_backups(self, database):
        raise StorageError("Programming Error: list_backups() not defined.")

    def write_file(self, filehandle, filename):
        raise StorageError("Programming Error: write_file() not defined.")

    def read_file(self, filepath):
        raise StorageError("Programming Error: read_file() not defined.")
