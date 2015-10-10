"""
Restore database.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import sys
import warnings
from optparse import make_option

from django.conf import settings
from django.core.management.base import CommandError
from django.utils import six
from django.db import connection

from ._base import BaseDbBackupCommand
from ... import utils
from ...dbcommands import DBCommands, MongoDBCommands
from ...storage.base import BaseStorage, StorageError

input = raw_input if six.PY2 else input  # @ReservedAssignment


class Command(BaseDbBackupCommand):
    help = """
    Restore a backup from storage, encrypted and/or compressed.
    """
    option_list = BaseDbBackupCommand.option_list + (
        make_option("-d", "--database", help="Database to restore"),
        make_option("-i", "--input-filename", help="Specify filename to backup from"),
        make_option("-I", "--input-path", help="Specify path on local filesystem to backup from"),
        make_option("-x", "--backup-extension", help="The extension to use when scanning for files to restore from."),
        make_option("-s", "--servername", help="Use a different servername backup"),
        make_option("-l", "--list", action='store_true', default=False, help="List backups in the backup directory"),

        make_option("-c", "--decrypt", help="Decrypt data before restoring", default=False, action='store_true'),
        make_option("-p", "--passphrase", help="Passphrase for decrypt file", default=None),
        make_option("-z", "--uncompress", help="Uncompress gzip data before restoring", action='store_true'),
    )

    def handle(self, *args, **options):
        """Django command handler."""
        self.verbosity = int(options.get('verbosity'))
        self.quiet = options.get('quiet')
        try:
            connection.close()
            self.filename = options.get('input_filename')
            self.path = options.get('input_path')
            self.backup_extension = options.get('backup_extension') or 'backup'
            self.servername = options.get('servername')
            self.decrypt = options.get('decrypt')
            self.uncompress = options.get('uncompress')
            self.passphrase = options.get('passphrase')
            self.interactive = options.get('interactive')
            self.database = self._get_database(options)
            self.storage = BaseStorage.storage_factory()
            self.database = self._get_database(options)
            if 'mongo' in self.database['ENGINE']:
                self.dbcommands = MongoDBCommands(self.database)
            else:
                self.dbcommands = DBCommands(self.database)

            if not self.backup_extension:
                self.backup_extension = self.dbcommands.settings.extension or 'backup'
            if options.get('list'):
                return self._list_backups()
            self._restore_backup()
        except StorageError as err:
            raise CommandError(err)

    def _get_database(self, options):
        """Get the database to restore."""
        database_key = options.get('database')
        if not database_key:
            if len(settings.DATABASES) >= 2:
                errmsg = "Because this project contains more than one database, you"\
                    " must specify the --database option."
                raise CommandError(errmsg)
            database_key = list(settings.DATABASES.keys())[0]
        return settings.DATABASES[database_key]

    def _restore_backup(self):
        """Restore the specified database."""
        self.logger.info("Restoring backup for database: %s", self.database['NAME'])
        if self.path:
            input_filename = self.path
            input_file = self.read_local_file(self.path)
        else:
            if self.filename:
                input_filename = self.filename
            # Fetch the latest backup if filepath not specified
            else:
                self.logger.info("Finding latest backup")
                try:
                    input_filename = self.storage.get_latest_backup(encrypted=self.decrypt,
                                                                    compressed=self.uncompress)
                except StorageError as err:
                    raise CommandError(err.args[0])
            input_file = self.storage.read_file(input_filename)

        self.logger.info("Restoring: %s" % input_filename)
        if self.decrypt:
            unencrypted_file, input_filename = utils.unencrypt_file(input_file, input_filename,
                                                                    self.passphrase)
            input_file.close()
            input_file = unencrypted_file
        if self.uncompress:
            uncompressed_file, input_filename = utils.uncompress_file(input_file, input_filename)
            input_file.close()
            input_file = uncompressed_file
        self.logger.info("Restore tempfile created: %s", utils.handle_size(input_file))
        if self.interactive:
            answer = input("Are you sure you want to continue? [Y/n]")
            if answer.lower().startswith('n'):
                self.logger.info("Quitting")
                sys.exit(0)
        input_file.seek(0)
        self.dbcommands.run_restore_commands(input_file)

    # TODO: Remove this
    def _list_backups(self):
        """List backups in the backup directory."""
        msg = "'dbbrestore --list' is deprecated, use 'listbackup'."
        warnings.warn(msg, DeprecationWarning)
        self.logger.info("Listing backups on %s in /%s:", self.storage.name, self.storage.backup_dir)
        for filepath in self.storage.list_directory():
            self.logger.info("  %s", os.path.basename(filepath))
            # TODO: Implement filename_details method
            # print(utils.filename_details(filepath))

    def read_local_file(self, path):
        """Open file on local filesystem."""
        return open(path)
