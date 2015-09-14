"""
Abstract Storage class.
"""
import logging
from importlib import import_module
from django.core.exceptions import ImproperlyConfigured
from .. import settings, utils


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


class FileNotFound(StorageError):
    pass


class BaseStorage(object):
    """Abstract storage class."""

    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger('dbbackup.storage')
        return self._logger

    def __init__(self, server_name=None):
        if not self.name:
            raise Exception("Programming Error: storage.name not defined.")

    def __str__(self):
        return self.name

    # TODO: Remove in favor of get_storage
    @classmethod
    def storage_factory(cls):
        return get_storage()

    def backup_dir(self):
        raise NotImplementedError("Programming Error: backup_dir() not defined.")

    def delete_file(self, filepath):
        raise NotImplementedError("Programming Error: delete_file() not defined.")

    def write_file(self, filehandle, filename):
        raise NotImplementedError("Programming Error: write_file() not defined.")

    def read_file(self, filepath):
        raise NotImplementedError("Programming Error: read_file() not defined.")

    def list_backups(self, encrypted=None, compressed=None, content_type=None,
                     database=None):
        """
        List stored files except given filter. If filter is None, it won't be
        used. ``content_type`` must be ``'db'`` for database backups or
        ``'media'`` for media backups.

        :param encrypted: Filter by encrypted or not
        :type encrypted: ``bool`` or ``None``

        :param compressed: Filter by compressed or not
        :type compressed: ``bool`` or ``None``

        :param content_type: Filter by media or database backup, must be
                             ``'db'`` or ``'media'``

        :type content_type: ``str`` or ``None``

        :param database: Filter by source database's name
        :type: ``str`` or ``None``

        :returns: List of files
        :rtype: ``list`` of ``str``
        """
        if content_type not in ('db', 'media', None):
            msg = "Bad content_type %s, must be 'db', 'media', or None" % (
                content_type)
            raise TypeError(msg)
        files = self.list_directory()
        if encrypted is not None:
            files = [f for f in files if ('.gpg' in f) == encrypted]
        if compressed is not None:
            files = [f for f in files if ('.gz' in f) == compressed]
        if content_type is not None:
            files = [f for f in files if '%s' % content_type in f]
        if database is not None:
            files = [f for f in files if '%s' % database in f]
        return files

    def write_file(self, filehandle, filename):
        raise NotImplementedError("Programming Error: write_file() not defined.")

    def read_file(self, filepath):
        raise NotImplementedError("Programming Error: read_file() not defined.")

    def get_latest_backup(self, encrypted=None, compressed=None,
                          content_type=None, database=None):
        """
        Return the latest backup file name.

        :param encrypted: Filter by encrypted or not
        :type encrypted: ``bool`` or ``None``

        :param compressed: Filter by compressed or not
        :type compressed: ``bool`` or ``None``

        :param content_type: Filter by media or database backup, must be
                             ``'db'`` or ``'media'``

        :type content_type: ``str`` or ``None``

        :param database: Filter by source database's name
        :type: ``str`` or ``None``

        :returns: Most recent file
        :rtype: ``str``

        :raises: FileNotFound: If no backup file is found
        """
        files = self.list_backups(encrypted=encrypted, compressed=compressed,
                                  content_type=content_type, database=database)
        if not files:
            raise FileNotFound("There's no backup file available.")
        return max(files, key=utils.filename_to_date)

    def get_older_backup(self, encrypted=None, compressed=None,
                          content_type=None, database=None):
        """
        Return the older backup's file name.

        :param encrypted: Filter by encrypted or not
        :type encrypted: ``bool`` or ``None``

        :param compressed: Filter by compressed or not
        :type compressed: ``bool`` or ``None``

        :param content_type: Filter by media or database backup, must be
                             ``'db'`` or ``'media'``

        :type content_type: ``str`` or ``None``

        :param database: Filter by source database's name
        :type: ``str`` or ``None``

        :returns: Older file
        :rtype: ``str``

        :raises: FileNotFound: If no backup file is found
        """
        files = self.list_backups(encrypted=encrypted, compressed=compressed,
                                  content_type=content_type, database=database)
        if not files:
            raise FileNotFound("There's no backup file available.")
        return min(files, key=utils.filename_to_date)

    def clean_old_backups(self, encrypted=None, compressed=None,
                          content_type=None, database=None,
                          keep_number=None):
        """
        Delete olders backups and hold the number defined.

        :param encrypted: Filter by encrypted or not
        :type encrypted: ``bool`` or ``None``

        :param compressed: Filter by compressed or not
        :type compressed: ``bool`` or ``None``

        :param content_type: Filter by media or database backup, must be
                             ``'db'`` or ``'media'``

        :type content_type: ``str`` or ``None``

        :param database: Filter by source database's name
        :type: ``str`` or ``None``

        :param keep_number: Number of files to keep, other will be deleted
        :type keep_number: ``int`` or ``None``
        """
        files = self.list_backups(encrypted=encrypted, compressed=compressed,
                                  content_type=content_type, database=database)
        files = sorted(files, key=utils.filename_to_date, reverse=True)
        files_to_delete = [fi for i, fi in enumerate(files) if i >= keep_number]
        for filename in files_to_delete:
            self.delete_file(filename)
