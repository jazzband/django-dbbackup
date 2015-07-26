"""
Save database.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import re
import datetime
import tempfile
import gzip
from shutil import copyfileobj

from django.conf import settings
from django.core.management.base import CommandError
from optparse import make_option

from dbbackup.management.commands._base import BaseDbBackupCommand
from dbbackup import utils
from dbbackup.dbcommands import DBCommands
from dbbackup.storage.base import BaseStorage
from dbbackup.storage.base import StorageError
from dbbackup import settings as dbbackup_settings


class Command(BaseDbBackupCommand):
    help = "dbbackup [-c] [-d <dbname>] [-s <servername>] [--compress] [--encrypt]"
    option_list = BaseDbBackupCommand.option_list + (
        make_option("-c", "--clean", help="Clean up old backup files", action="store_true", default=False),
        make_option("-d", "--database", help="Database to backup (default: everything)"),
        make_option("-s", "--servername", help="Specify server name to include in backup filename"),
        make_option("-z", "--compress", help="Compress the backup files", action="store_true", default=False),
        make_option("-e", "--encrypt", help="Encrypt the backup files", action="store_true", default=False),
    )

    @utils.email_uncaught_exception
    def handle(self, **options):
        """ Django command handler. """
        self.verbosity = options.get('verbosity')
        self.quiet = options.get('quiet')
        try:
            self.clean = options.get('clean')
            self.clean_keep = settings.CLEANUP_KEEP
            self.database = options.get('database')
            self.servername = options.get('servername')
            self.compress = options.get('compress')
            self.encrypt = options.get('encrypt')
            self.storage = BaseStorage.storage_factory()
            if self.database:
                database_keys = self.database,
            else:
                database_keys = dbbackup_settings.DATABASES
            for database_key in database_keys:
                database = settings.DATABASES[database_key]
                self.dbcommands = DBCommands(database)
                self.save_new_backup(database, database_key)
                self.cleanup_old_backups(database)
        except StorageError as err:
            raise CommandError(err)

    def save_new_backup(self, database):
        """ Save a new backup file. """
        self.log("Backing Up Database: %s" % database['NAME'], 1)
        filename = self.dbcommands.filename(self.servername)
        outputfile = tempfile.SpooledTemporaryFile(
            max_size=10 * 1024 * 1024,
            dir=dbbackup_settings.TMP_DIR)
        self.dbcommands.run_backup_commands(outputfile)
        outputfile.name = filename
        if self.compress:
            compressed_file = self.compress_file(outputfile)
            outputfile.close()
            outputfile = compressed_file
        if self.encrypt:
            encrypted_file = utils.encrypt_file(outputfile)
            outputfile = encrypted_file
        self.log("  Backup tempfile created: %s" % (utils.handle_size(outputfile)), 1)
        self.log("  Writing file to %s: %s, filename: %s" % (self.storage.name, self.storage.backup_dir, filename), 1)
        self.storage.write_file(outputfile, filename)

    def cleanup_old_backups(self, database):
        """ Cleanup old backups, keeping the number of backups specified by
            DBBACKUP_CLEANUP_KEEP and any backups that occur on first of the month.
        """
        if self.clean:
            self.log("Cleaning Old Backups for: %s" % database['NAME'], 1)
            filepaths = self.storage.list_directory()
            filepaths = self.dbcommands.filter_filepaths(filepaths)
            for filepath in sorted(filepaths[0:-self.clean_keep]):
                regex = r'^%s' % self.dbcommands.filename_match(self.servername, '(.*?)')
                datestr = re.findall(regex, os.path.basename(filepath))[0]
                dateTime = datetime.datetime.strptime(datestr, dbbackup_settings.DATE_FORMAT)
                if int(dateTime.strftime("%d")) != 1:
                    self.log("  Deleting: %s" % filepath, 1)
                    self.storage.delete_file(filepath)

    def compress_file(self, inputfile):
        """ Compress this file using gzip.
            The input and the output are filelike objects.
        """
        outputfile = tempfile.SpooledTemporaryFile(
            max_size=10 * 1024 * 1024,
            dir=dbbackup_settings.TMP_DIR)
        outputfile.name = inputfile.name + '.gz'
        zipfile = gzip.GzipFile(fileobj=outputfile, mode="wb")
        # TODO: Why do we have an exception block without handling exceptions?
        try:
            inputfile.seek(0)
            copyfileobj(inputfile, zipfile, 2 * 1024 * 1024)
        finally:
            zipfile.close()

        return outputfile
