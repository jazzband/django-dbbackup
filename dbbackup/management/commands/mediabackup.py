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

from django.conf import settings
from django.core.management.base import CommandError

from ._base import BaseDbBackupCommand
from ... import utils, settings as dbbackup_settings
from ...storage.base import BaseStorage, StorageError


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
        try:
            self.servername = options.get('servername')
            self.storage = BaseStorage.storage_factory()

            self.backup_mediafiles(
                options.get('encrypt'),
                options.get('no_compress', True))

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
        source_dir = self.get_source_dir()
        if not source_dir:
            self.stderr.write("No media source dir configured.")
            sys.exit(0)
        self.log("Backing up media files in %s" % source_dir, 1)
        filename = self.get_backup_basename(compress=compress)
        output_file = self.create_backup_file(
            source_dir,
            filename,
            compress=compress
        )

        if encrypt:
            encrypted_file = utils.encrypt_file(output_file, filename)
            output_file, filename = encrypted_file

        self.log("  Backup tempfile created: %s (%s)" % (filename, utils.handle_size(output_file)), 1)
        self.log("  Writing file to %s: %s" % (self.storage.name, self.storage.backup_dir), 1)
        self.storage.write_file(
            output_file,
            self.get_backup_basename(
                compress=compress)
        )

    def get_backup_basename(self, **kwargs):
        # TODO: use DBBACKUP_FILENAME_TEMPLATE
        server_name = self.get_servername()
        if server_name:
            server_name = '-%s' % server_name

        return '%s%s-%s.media.tar%s' % (
            self.get_databasename(),
            server_name,
            datetime.now().strftime(dbbackup_settings.DATE_FORMAT),
            ('.gz' if kwargs.get('compress') else '')
        )

    def get_databasename(self):
        # TODO: WTF is this??
        return settings.DATABASES['default']['NAME']

    def get_source_dir(self):
        # TODO: WTF again ??
        return dbbackup_settings.MEDIA_PATH

    def create_backup_file(self, source_dir, backup_basename, **kwargs):
        temp_dir = tempfile.mkdtemp(dir=dbbackup_settings.TMP_DIR)
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
        self.log("Cleaning Old Backups for media files", 1)

        file_list = self.get_backup_file_list()

        for backup_date, filename in file_list[0:-dbbackup_settings.CLEANUP_KEEP_MEDIA]:
            if int(backup_date.strftime("%d")) != 1:
                self.log("  Deleting: %s" % filename, 1)
                self.storage.delete_file(filename)

    def get_backup_file_list(self):
        """
        Return a list of backup files including the backup date. The result
        is a list of tuples (datetime, filename).  The list is sorted by date.
        """
        server_name = self.get_servername()
        if server_name:
            server_name = '-%s' % server_name

        media_re = re.compile(r'^%s%s-(.*)\.media\.tar(?:\.gz)?(?:\.\d+)?$' %
            re.escape(self.get_databasename()), re.escape(server_name))

        def is_media_backup(filename):
            return media_re.search(filename)

        def get_datetime_from_filename(filename):
            datestr = media_re.findall(filename)[0]
            return datetime.strptime(datestr, dbbackup_settings.DATE_FORMAT)

        file_list = [
            (get_datetime_from_filename(os.path.basename(f)), f)
            for f in self.storage.list_directory()
            if is_media_backup(os.path.basename(f))
        ]
        return sorted(file_list, key=lambda v: v[0])

    def get_servername(self):
        return self.servername or dbbackup_settings.HOSTNAME
