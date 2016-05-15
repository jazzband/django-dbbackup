"""
Command for backup database.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from optparse import make_option
from shutil import copyfileobj

from django.core.management.base import CommandError

from ._base import BaseDbBackupCommand
from ...db.base import get_connector
from ...storage.base import BaseStorage, StorageError
from ... import utils, settings as dbbackup_settings


class Command(BaseDbBackupCommand):
    help = """
    Backup a database, encrypt and/or compress and write to storage.
    """
    option_list = BaseDbBackupCommand.option_list + (
        make_option("-c", "--clean", help="Clean up old backup files", action="store_true", default=False),
        make_option("-d", "--database", help="Database to backup (default: everything)"),
        make_option("-s", "--servername", help="Specify server name to include in backup filename"),
        make_option("-z", "--compress", help="Compress the backup files", action="store_true", default=False),
        make_option("-e", "--encrypt", help="Encrypt the backup files", action="store_true", default=False),
        make_option("-o", "--output-filename", help="Specify filename on storage", default=None),
        make_option("-O", "--output-path", help="Specify where to store on local filesystem", default=None),
    )

    @utils.email_uncaught_exception
    def handle(self, **options):
        """Django command handler."""
        self.verbosity = int(options.get('verbosity'))
        self.quiet = options.get('quiet')
        self.clean = options.get('clean')
        self.clean_keep = dbbackup_settings.CLEANUP_KEEP
        self.database = options.get('database')
        self.servername = options.get('servername')
        self.compress = options.get('compress')
        self.encrypt = options.get('encrypt')
        self.filename = options.get('output_filename')
        self.path = options.get('output_path')
        self.storage = BaseStorage.storage_factory()
        database_keys = (self.database,) if self.database else dbbackup_settings.DATABASES
        for database_key in database_keys:
            self.connector = get_connector(database_key)
            database = self.connector.settings
            try:
                self._save_new_backup(database)
                if self.clean:
                    self.storage.clean_old_backups(self.encrypt,
                                                   self.compress,
                                                   content_type='db',
                                                   database=self.database)
            except StorageError as err:
                raise CommandError(err)

    def _save_new_backup(self, database):
        """
        Save a new backup file.
        """
        if not self.quiet:
            self.logger.info("Backing Up Database: %s", database['NAME'])
        filename = self.connector.generate_filename(self.servername)
        outputfile = self.connector.create_dump()
        if self.compress:
            compressed_file, filename = utils.compress_file(outputfile, filename)
            outputfile = compressed_file
        if self.encrypt:
            encrypted_file, filename = utils.encrypt_file(outputfile, filename)
            outputfile = encrypted_file
        filename = self.filename if self.filename else filename
        if not self.quiet:
            self.logger.info("Backup tempfile created: %s", utils.handle_size(outputfile))
        # Store backup
        if self.path is None:
            self.logger.info("Writing file to %s: %s, filename: %s",
                             self.storage.name, self.storage.backup_dir,
                             filename)
            self.storage.write_file(outputfile, filename)
        else:
            self.logger.info("Writing file to %s", self.path)
            self.write_local_file(outputfile, self.path)

    # TODO: Define chunk size
    def write_local_file(self, outputfile, path):
        """Write file to the desired path."""
        outputfile.seek(0)
        with open(path, 'wb') as fd:
            copyfileobj(outputfile, fd)
