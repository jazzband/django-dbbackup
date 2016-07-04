"""
Restore media files.
"""
import tarfile
from optparse import make_option

from django.core.management.base import CommandError
from django.core.files.storage import get_storage_class

from ._base import BaseDbBackupCommand
from ...storage.base import BaseStorage, StorageError
from ... import utils


class Command(BaseDbBackupCommand):
    help = """Restore a media backup from storage, encrypted and/or
    compressed."""
    content_type = 'media'

    option_list = BaseDbBackupCommand.option_list + (
        make_option("-i", "--input-filename", help="Specify filename to backup from"),
        make_option("-I", "--input-path", help="Specify path on local filesystem to backup from"),

        make_option("-e", "--decrypt", help="Decrypt data before restoring", default=False, action='store_true'),
        make_option("-p", "--passphrase", help="Passphrase for decrypt file", default=None),
        make_option("-z", "--uncompress", help="Uncompress gzip data before restoring", action='store_true'),
        make_option("-r", "--replace", help="Replace existing files", action='store_true'),
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
        self.replace = options.get('replace')
        self.passphrase = options.get('passphrase')
        self.interactive = options.get('interactive')
        self.storage = BaseStorage.storage_factory()
        self.media_storage = get_storage_class()()
        self._restore_backup()

    def _upload_file(self, name, media_file):
        if self.media_storage.exists(name):
            if self.replace:
                self.media_storage.delete(name)
                self.logger.info("%s deleted", name)
            else:
                return
        self.media_storage.save(name, media_file)
        self.logger.info("%s uploaded", name)

    def _restore_backup(self):
        self.logger.info("Restoring backup for media files")
        input_filename, input_file = self._get_backup_file()
        self.logger.info("Restoring: %s", input_filename)

        if self.decrypt:
            unencrypted_file, input_filename = utils.unencrypt_file(input_file, input_filename,
                                                                    self.passphrase)
            input_file.close()
            input_file = unencrypted_file

        self.logger.info("Backup size: %s", utils.handle_size(input_file))
        if self.interactive:
            self._ask_confirmation()

        input_file.seek(0)
        tar_file = tarfile.open(fileobj=input_file, mode='r:gz') \
            if self.uncompress \
            else tarfile.open(fileobj=input_file, mode='r:')
        # Restore file 1 by 1
        for media_file_info in tar_file:
            if media_file_info.path == 'media':
                continue  # Don't copy root directory
            media_file = tar_file.extractfile(media_file_info)
            if media_file is None:
                continue  # Skip directories
            name = media_file_info.path.replace('media/', '')
            self._upload_file(name, media_file)
