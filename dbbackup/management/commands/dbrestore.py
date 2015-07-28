"""
Restore database.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import tempfile
import gzip
import sys
from getpass import getpass

from django.conf import settings
from django.core.management.base import CommandError
from django.utils import six
from django.db import connection

from optparse import make_option

from dbbackup.management.commands._base import BaseDbBackupCommand
from dbbackup import utils
from dbbackup.dbcommands import DBCommands
from dbbackup.storage.base import BaseStorage, StorageError
from dbbackup import settings as dbbackup_settings

input = raw_input if six.PY2 else input  # @ReservedAssignment


class Command(BaseDbBackupCommand):
    help = "dbrestore [-d <dbname>] [-f <filename>] [-s <servername>]"
    option_list = BaseDbBackupCommand.option_list + (
        make_option("-d", "--database", help="Database to restore"),
        make_option("-f", "--filepath", help="Specific file to backup from"),
        make_option("-x", "--backup-extension", help="The extension to use when scanning for files to restore from."),
        make_option("-s", "--servername", help="Use a different servername backup"),
        make_option("-l", "--list", action='store_true', default=False, help="List backups in the backup directory"),
        make_option("-c", "--decrypt", help="Decrypt data before restoring", default=False, action='store_true'),
        make_option("-p", "--passphrase", help="Passphrase for decrypt file", default=None),
        make_option("-z", "--uncompress", help="Uncompress gzip data before restoring", action='store_true'),
    )

    def handle(self, **options):
        """ Django command handler. """
        self.verbosity = int(options.get('verbosity'))
        self.quiet = options.get('quiet')
        try:
            connection.close()
            self.filepath = options.get('filepath')
            self.backup_extension = options.get('backup_extension') or 'backup'
            self.servername = options.get('servername')
            self.decrypt = options.get('decrypt')
            self.uncompress = options.get('uncompress')
            self.passphrase = options.get('passphrase')
            self.database = self._get_database(options)
            self.storage = BaseStorage.storage_factory()
            self.dbcommands = DBCommands(self.database)
            if options.get('list'):
                return self.list_backups()
            self.restore_backup()
        except StorageError as err:
            raise CommandError(err)

    def _get_database(self, options):
        """ Get the database to restore. """
        database_key = options.get('database')
        if not database_key:
            if len(settings.DATABASES) >= 2:
                errmsg = "Because this project contains more than one database, you"
                errmsg += " must specify the --database option."
                raise CommandError(errmsg)
            database_key = list(settings.DATABASES.keys())[0]
        return settings.DATABASES[database_key]

    def restore_backup(self):
        """ Restore the specified database. """
        self.log("Restoring backup for database: %s" % self.database['NAME'], 1)
        # Fetch the latest backup if filepath not specified
        if not self.filepath:
            self.log("  Finding latest backup", 1)
            filepaths = self.storage.list_directory()
            # TODO: It is a bad filter
            # filepaths = [f for f in filepaths if f.endswith('.' + self.backup_extension)]
            if not filepaths:
                raise CommandError("No backup files found in: /%s" % self.storage.backup_dir)
            self.filepath = filepaths[-1]
        # Restore the specified filepath backup
        self.log("  Restoring: %s" % self.filepath, 1)
        input_filename = self.filepath
        inputfile = self.storage.read_file(input_filename)
        if self.decrypt:
            unencrypted_file, input_filename = self.unencrypt_file(inputfile, input_filename)
            inputfile.close()
            inputfile = unencrypted_file
        if self.uncompress:
            uncompressed_file = self.uncompress_file(inputfile)
            inputfile.close()
            inputfile = uncompressed_file
        self.log("  Restore tempfile created: %s" % utils.handle_size(inputfile), 1)
        answer = input("Are you sure you want to continue? [Y/n]")
        if answer.lower() not in ('y', 'yes', ''):
            self.log("Quitting", 1)
            sys.exit(0)
        inputfile.seek(0)
        self.dbcommands.run_restore_commands(inputfile)

    def get_extension(self, filename):
        _, extension = os.path.splitext(filename)
        return extension

    def uncompress_file(self, inputfile):
        """ Uncompress this file using gzip. The input and the output are filelike objects. """
        outputfile = tempfile.SpooledTemporaryFile(
            max_size=500 * 1024 * 1024,
            dir=dbbackup_settings.TMP_DIR)
        zipfile = gzip.GzipFile(fileobj=inputfile, mode="rb")
        try:
            inputfile.seek(0)
            outputfile.write(zipfile.read())
        finally:
            zipfile.close()
        return outputfile

    def unencrypt_file(self, inputfile, inputfilename):
        """ Unencrypt this file using gpg. The input and the output are filelike objects. """
        import gnupg

        def get_passphrase():
            return self.passphrase or getpass('Input Passphrase: ') or None

        temp_dir = tempfile.mkdtemp(dir=dbbackup_settings.TMP_DIR)
        try:
            new_basename = os.path.basename(inputfilename).replace('.gpg', '')
            temp_filename = os.path.join(temp_dir, new_basename)
            try:
                inputfile.seek(0)
                g = gnupg.GPG()
                result = g.decrypt_file(file=inputfile, passphrase=get_passphrase(), output=temp_filename)
                if not result:
                    raise Exception('Decryption failed; status: %s' % result.status)
                outputfile = tempfile.SpooledTemporaryFile(
                    max_size=10 * 1024 * 1024,
                    dir=dbbackup_settings.TMP_DIR)
                outputfile.name = new_basename
                f = open(temp_filename)
                try:
                    outputfile.write(f.read())
                finally:
                    f.close()
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        finally:
            os.rmdir(temp_dir)
        return outputfile, new_basename

    def list_backups(self):
        """ List backups in the backup directory. """
        self.log("Listing backups on %s in /%s:" % (self.storage.name, self.storage.backup_dir), 1)
        for filepath in self.storage.list_directory():
            self.log("  %s" % os.path.basename(filepath), 1)
            # TODO: Implement filename_details method
            # print(utils.filename_details(filepath))
