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
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from dbbackup import utils
from dbbackup.storage.base import BaseStorage
from dbbackup.storage.base import StorageError
from dbbackup import settings as dbbackup_settings


class Command(BaseCommand):
    help = "backup_media [--encrypt]"
    option_list = BaseCommand.option_list + (
        make_option("-c", "--clean", help="Clean up old backup files", action="store_true", default=False),
        make_option("-s", "--servername", help="Specify server name to include in backup filename"),
        make_option("-e", "--encrypt", help="Encrypt the backup files", action="store_true", default=False),
    )

    @utils.email_uncaught_exception
    def handle(self, *args, **options):
        try:
            self.servername = options.get('servername')
            self.storage = BaseStorage.storage_factory()

            self.backup_mediafiles(options.get('encrypt'))

            if options.get('clean'):
                self.cleanup_old_backups()

        except StorageError as err:
            raise CommandError(err)

    def backup_mediafiles(self, encrypt):
        source_dir = self.get_source_dir()
        if not source_dir:
            print("No media source dir configured.")
            sys.exit(0)
        print("Backing up media files in %s" % source_dir)
        output_file = self.create_backup_file(source_dir, self.get_backup_basename())

        if encrypt:
            encrypted_file = utils.encrypt_file(output_file)
            output_file = encrypted_file

        print("  Backup tempfile created: %s (%s)" % (output_file.name, utils.handle_size(output_file)))
        print("  Writing file to %s: %s" % (self.storage.name, self.storage.backup_dir))
        self.storage.write_file(output_file, self.get_backup_basename())

    def get_backup_basename(self):
        # TODO: use DBBACKUP_FILENAME_TEMPLATE
        server_name = self.get_servername()
        if server_name:
            server_name = '-%s' % server_name

        return '%s%s-%s.media.tar.gz' % (
            self.get_databasename(),
            server_name,
            datetime.now().strftime(dbbackup_settings.DATE_FORMAT)
        )

    def get_databasename(self):
        # TODO: WTF is this??
        return settings.DATABASES['default']['NAME']

    def create_backup_file(self, source_dir, backup_basename):
        temp_dir = tempfile.mkdtemp()
        try:
            backup_filename = os.path.join(temp_dir, backup_basename)
            try:
                tar_file = tarfile.open(backup_filename, 'w|gz')
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

    def get_source_dir(self):
        return dbbackup_settings.MEDIA_PATH

    def cleanup_old_backups(self):
        """ Cleanup old backups, keeping the number of backups specified by
        DBBACKUP_CLEANUP_KEEP and any backups that occur on first of the month.
        """
        print("Cleaning Old Backups for media files")

        file_list = self.get_backup_file_list()

        for backup_date, filename in file_list[0:-dbbackup_settings.CLEANUP_KEEP_MEDIA]:
            if int(backup_date.strftime("%d")) != 1:
                print("  Deleting: %s" % filename)
                self.storage.delete_file(filename)

    def get_backup_file_list(self):
        """ Return a list of backup files including the backup date. The result is a list of tuples (datetime, filename).
            The list is sorted by date.
        """
        server_name = self.get_servername()
        if server_name:
            server_name = '-%s' % server_name

        media_re = re.compile(r'^%s%s-(.*)\.media\.tar\.gz' % (self.get_databasename(), server_name))

        def is_media_backup(filename):
            return media_re.search(filename)

        def get_datetime_from_filename(filename):
            datestr = re.findall(media_re, filename)[0]
            return datetime.strptime(datestr, dbbackup_settings.DATE_FORMAT)

        file_list = [
            (get_datetime_from_filename(f), f)
            for f in self.storage.list_directory()
            if is_media_backup(f)
        ]
        return sorted(file_list, key=lambda v: v[0])

    def get_servername(self):
        return self.servername or dbbackup_settings.SERVER_NAME