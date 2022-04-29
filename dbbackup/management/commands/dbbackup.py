"""
Command for backup database.
"""

from django.core.management.base import CommandError

from ... import settings, utils
from ...db.base import get_connector
from ...storage import StorageError, get_storage
from ._base import BaseDbBackupCommand, make_option


class Command(BaseDbBackupCommand):
    help = "Backup a database, encrypt and/or compress and write to " "storage." ""
    content_type = "db"

    option_list = BaseDbBackupCommand.option_list + (
        make_option(
            "-c",
            "--clean",
            dest="clean",
            action="store_true",
            default=False,
            help="Clean up old backup files",
        ),
        make_option(
            "-d",
            "--database",
            help="Database(s) to backup specified by key separated by"
            " commas(default: all)",
        ),
        make_option(
            "-s",
            "--servername",
            help="Specify server name to include in backup filename",
        ),
        make_option(
            "-z",
            "--compress",
            action="store_true",
            default=False,
            help="Compress the backup files",
        ),
        make_option(
            "-e",
            "--encrypt",
            action="store_true",
            default=False,
            help="Encrypt the backup files",
        ),
        make_option(
            "-o", "--output-filename", default=None, help="Specify filename on storage"
        ),
        make_option(
            "-O",
            "--output-path",
            default=None,
            help="Specify where to store on local filesystem",
        ),
        make_option(
            "-x", "--exclude-tables", default=None, help="Exclude tables from backup"
        ),
    )

    @utils.email_uncaught_exception
    def handle(self, **options):
        self.verbosity = options.get("verbosity")
        self.quiet = options.get("quiet")
        self._set_logger_level()

        self.clean = options.get("clean")

        self.servername = options.get("servername")
        self.compress = options.get("compress")
        self.encrypt = options.get("encrypt")

        self.filename = options.get("output_filename")
        self.path = options.get("output_path")
        self.exclude_tables = options.get("exclude_tables")
        self.storage = get_storage()

        self.database = options.get("database") or ""
        database_keys = self.database.split(",") or settings.DATABASES

        for database_key in database_keys:
            self.connector = get_connector(database_key)
            if self.connector and self.exclude_tables:
                self.connector.exclude.extend(
                    list(self.exclude_tables.replace(" ", "").split(","))
                )
            database = self.connector.settings
            try:
                self._save_new_backup(database)
                if self.clean:
                    self._cleanup_old_backups(database=database_key)
            except StorageError as err:
                raise CommandError(err) from err

    def _save_new_backup(self, database):
        """
        Save a new backup file.
        """
        self.logger.info("Backing Up Database: %s", database["NAME"])
        # Get backup and name
        filename = self.connector.generate_filename(self.servername)
        outputfile = self.connector.create_dump()
        # Apply trans
        if self.compress:
            compressed_file, filename = utils.compress_file(outputfile, filename)
            outputfile = compressed_file
        if self.encrypt:
            encrypted_file, filename = utils.encrypt_file(outputfile, filename)
            outputfile = encrypted_file
        # Set file name
        filename = self.filename or filename
        self.logger.debug("Backup size: %s", utils.handle_size(outputfile))
        # Store backup
        outputfile.seek(0)
        if self.path is None:
            self.write_to_storage(outputfile, filename)
        else:
            self.write_local_file(outputfile, self.path)
