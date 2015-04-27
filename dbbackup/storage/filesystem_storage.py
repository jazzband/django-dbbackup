"""
Filesystem Storage object.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
from .base import BaseStorage, StorageError

from dbbackup import settings


################################
#  Filesystem Storage Object
################################

class Storage(BaseStorage):
    """ Filesystem API Storage. """

    def __init__(self, server_name=None):
        self._check_filesystem_errors()
        self.name = 'Filesystem'
        BaseStorage.__init__(self)

    def _check_filesystem_errors(self):
        """ Check we have all the required settings defined. """
        if not self.backup_dir:
            raise StorageError('Filesystem storage requires DBBACKUP_BACKUP_DIRECTORY to be defined in settings.')

    ###################################
    #  DBBackup Storage Methods
    ###################################
    
    @property
    def backup_dir(self):
        return settings.BACKUP_DIRECTORY

    def delete_file(self, filepath):
        """ Delete the specified filepath. """
        os.unlink(filepath)

    def list_directory(self):
        """ List all stored backups for the specified. """
        filepaths = os.listdir(self.backup_dir)
        filepaths = [os.path.join(self.backup_dir, path) for path in filepaths]
        return sorted(filter(os.path.isfile, filepaths))

    def write_file(self, filehandle, filename):
        """ Write the specified file. """
        filehandle.seek(0)
        backuppath = os.path.join(self.backup_dir, filename)
        backupfile = open(backuppath, 'wb')
        data = filehandle.read(1024)
        while data:
            backupfile.write(data)
            data = filehandle.read(1024)
        backupfile.close()

    def read_file(self, filepath):
        """ Read the specified file and return it's handle. """
        return open(filepath, 'rb')
