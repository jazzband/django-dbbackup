"""
Restore media files.
"""
import sys
import tarfile
from optparse import make_option

from django.core.management.base import CommandError
from django.utils import six
from django.conf import settings

from ._base import BaseDbBackupCommand
from ...storage.base import BaseStorage, StorageError
from ...storage.filesystem_storage import Storage as FileSystemStorage
from ... import utils

input = raw_input if six.PY2 else input  # @ReservedAssignment


class Command(BaseDbBackupCommand):
    option_list = BaseDbBackupCommand.option_list + (
        make_option("-d", "--database", help="Database to restore"),
        make_option("-i", "--input-filename", help="Specify filename to backup from"),
        make_option("-I", "--input-path", help="Specify path on local filesystem to backup from"),
        make_option("-l", "--list", action='store_true', default=False, help="List backups in the backup directory"),

        make_option("-c", "--decrypt", help="Decrypt data before restoring", default=False, action='store_true'),
        make_option("-p", "--passphrase", help="Passphrase for decrypt file", default=None),
        make_option("-z", "--uncompress", help="Uncompress gzip data before restoring", action='store_true'),
    )

    def handle(self, *args, **options):
        """Django command handler."""
        self.verbosity = int(options.get('verbosity'))
        self.quiet = options.get('quiet')
        self.filename = options.get('input_filename')
        self.path = options.get('input_path')
        self.servername = options.get('servername')
        self.decrypt = options.get('decrypt')
        self.uncompress = options.get('uncompress')
        self.passphrase = options.get('passphrase')
        self.interactive = options.get('interactive')
        self.storage = BaseStorage.storage_factory()
        self._restore_backup()

    def _get_backup_file(self):
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
                    input_filename = self.storage.get_latest_backup(
                        encrypted=self.decrypt,
                        compressed=self.uncompress,
                        content_type='media')
                except StorageError as err:
                    raise CommandError(err.args[0])
            input_file = self.storage.read_file(input_filename)
        return input_filename, input_file

    def _restore_backup(self):
        self.logger.info("Restoring backup for media files")
        input_filename, input_file = self._get_backup_file()
        self.logger.info("Restoring: %s" % input_filename)

        if self.decrypt:
            unencrypted_file, input_filename = utils.unencrypt_file(input_file, input_filename,
                                                                    self.passphrase)
            input_file.close()
            input_file = unencrypted_file

        self.logger.info("Restore tempfile created: %s", utils.handle_size(input_file))
        if self.interactive:
            answer = input("Are you sure you want to continue? [Y/n]")
            if answer.lower().startswith('n'):
                self.logger.info("Quitting")
                sys.exit(0)
        input_file.seek(0)

        tar_file = tarfile.open(fileobj=input_file, mode='r|gz') \
            if self.uncompress \
            else tarfile.open(fileobj=input_file, mode='r')
        # tar_file.extractall(path=settings.MEDIA_ROOT)
        tar_file.extractall(path='/')
