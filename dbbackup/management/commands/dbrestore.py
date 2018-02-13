"""
Restore database.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from django.conf import settings
from django.core.management.base import CommandError
from django.db import connection

from ._base import BaseDbBackupCommand, make_option
from ... import utils
from ...db.base import get_connector
from ...storage import get_storage, StorageError


class Command(BaseDbBackupCommand):
    help = """Restore a database backup from storage, encrypted and/or
    compressed."""
    content_type = 'db'

    option_list = BaseDbBackupCommand.option_list + (
        make_option("-d", "--database", help="Database to restore"),
        make_option("-i", "--input-filename", help="Specify filename to backup from"),
        make_option("-I", "--input-path", help="Specify path on local filesystem to backup from"),
        make_option("-s", "--servername",
                    help="If backup file is not specified, filter the "
                         "existing ones with the given servername"),
        make_option("-c", "--decrypt", default=False, action='store_true',
                    help="Decrypt data before restoring"),
        make_option("-p", "--passphrase", help="Passphrase for decrypt file", default=None),
        make_option("-z", "--uncompress", action='store_true', default=False,
                    help="Uncompress gzip data before restoring")
    )

    def handle(self, *args, **options):
        """Django command handler."""
        self.verbosity = int(options.get('verbosity'))
        self.quiet = options.get('quiet')
        self._set_logger_level()

        try:
            connection.close()
            self.filename = options.get('input_filename')
            self.path = options.get('input_path')
            self.servername = options.get('servername')
            self.decrypt = options.get('decrypt')
            self.uncompress = options.get('uncompress')
            self.passphrase = options.get('passphrase')
            self.interactive = options.get('interactive')
            self.database_name, self.database = self._get_database(options)
            self.storage = get_storage()
            self._restore_backup()
        except StorageError as err:
            raise CommandError(err)

    def _get_database(self, options):
        """Get the database to restore."""
        database_name = options.get('database')
        if not database_name:
            if len(settings.DATABASES) > 1:
                errmsg = "Because this project contains more than one database, you"\
                    " must specify the --database option."
                raise CommandError(errmsg)
            database_name = list(settings.DATABASES.keys())[0]
        if database_name not in settings.DATABASES:
            raise CommandError("Database %s does not exist." % database_name)
        return database_name, settings.DATABASES[database_name]

    def _restore_backup(self):
        """Restore the specified database."""
        input_filename, input_file = self._get_backup_file(database=self.database_name,
                                                           servername=self.servername)
        self.logger.info("Restoring backup for database '%s' and server '%s'",
                         self.database_name, self.servername)
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
            self._ask_confirmation()

        input_file.seek(0)
        self.connector = get_connector(self.database_name)
        self.connector.restore_dump(input_file)
