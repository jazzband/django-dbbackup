"""
Save media files.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import sys
from datetime import datetime
import tarfile
import tempfile
from optparse import make_option
import re

from django.core.management.base import CommandError

from ._base import BaseDbBackupCommand
from ... import utils
from ...dbcommands import DBCommands
from ...storage.base import BaseStorage, StorageError
from ... import settings as settings


class Command(BaseDbBackupCommand):
    help = """
    Backup media files, gather all in a tarball and encrypt or compress.
    """
    option_list = BaseDbBackupCommand.option_list + (
        make_option("-c", "--clean", help="Clean up old backup files", action="store_true", default=False),
        make_option("-s", "--servername", help="Specify server name to include in backup filename"),
        make_option("-e", "--encrypt", help="Encrypt the backup files", action="store_true", default=False),
        make_option("-x", "--no-compress", help="Do not compress the archive", action="store_true", default=False),
    )

    @utils.email_uncaught_exception
    def handle(self, *args, **options):
        self.encrypt = options.get('encrypt')
        self.compress = not options.get('no_compress')
        self.servername = options.get('servername') or settings.HOSTNAME
        try:
            self.storage = BaseStorage.storage_factory()
            self.backup_mediafiles(self.encrypt, self.compress)
            if options.get('clean'):
                self.cleanup_old_backups()

        except StorageError as err:
            raise CommandError(err)

    def backup_mediafiles(self, encrypt, compress):
        """
        Create backup file and write it to storage.

        :param encrypt: Encrypt file or not
        :type encrypt: ``bool``

        :param compress: Compress file or not
        :type compress: ``bool``
        """
        # TODO: Remove MEDIA_PATH and list Media Storage
        source_dir = settings.MEDIA_PATH
        if not source_dir:
            self.stderr.write("No media source dir configured.")
            sys.exit(1)
        self.logger.info("Backing up media files in %s", source_dir)
        filename = self.get_backup_basename(compress=compress)
        output_file = self.create_backup_file(source_dir, filename,
                                              compress=compress)
        if encrypt:
            encrypted_file = utils.encrypt_file(output_file, filename)
            output_file, filename = encrypted_file
        self.logger.debug("Backup tempfile created: %s (%s)", filename,
                          utils.handle_size(output_file))
        self.logger.info("Writing file to %s: %s", self.storage.name, self.storage.backup_dir)
        self.storage.write_file(output_file, filename)

    def get_backup_basename(self, **kwargs):
        extension = "tar%s" % ('.gz' if kwargs.get('compress') else '')
        return utils.filename_generate(extension,
                                       servername=self.servername,
                                       content_type='media')

    def create_backup_file(self, source_dir, backup_basename, **kwargs):
        temp_dir = tempfile.mkdtemp(dir=settings.TMP_DIR)
        try:
            backup_filename = os.path.join(temp_dir, backup_basename)
            try:
                tar_file = tarfile.open(backup_filename, 'w|gz') \
                    if kwargs.get('compress') \
                    else tarfile.open(backup_filename, 'w')

                try:
                    tar_file.add(source_dir)
                finally:
                    tar_file.close()

                return utils.create_spooled_temporary_file(backup_filename)
            finally:
                if os.path.exists(backup_filename):
                    os.remove(backup_filename)
        finally:
            os.rmdir(temp_dir)

    def cleanup_old_backups(self):
        """
        Cleanup old backups, keeping the number of backups specified by
        DBBACKUP_CLEANUP_KEEP and any backups that occur on first of the month.
        """
        self.logger.info("Cleaning Old Backups for media files")
        file_list = self.storage.clean_old_backups(encrypted=self.encrypt,
                                                   compressed=self.compress,
                                                   keep_number=settings.CLEANUP_KEEP_MEDIA)
