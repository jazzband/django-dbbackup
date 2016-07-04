"""
Save media files.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import tarfile
from optparse import make_option

from django.core.management.base import CommandError
from django.core.files.storage import get_storage_class

from ._base import BaseDbBackupCommand
from ... import utils
from ...storage.base import BaseStorage, StorageError
from ... import settings


class Command(BaseDbBackupCommand):
    help = """
    Backup media files, gather all in a tarball and encrypt or compress.
    """

    content_type = "media"

    option_list = BaseDbBackupCommand.option_list + (
        make_option("-c", "--clean", help="Clean up old backup files", action="store_true",
                    default=False),
        make_option("-s", "--servername", help="Specify server name to include in backup filename"),
        make_option("-e", "--encrypt", help="Encrypt the backup files", action="store_true",
                    default=False),
        make_option("-z", "--compress", help="Do not compress the archive", action="store_true",
                    default=False),
    )

    @utils.email_uncaught_exception
    def handle(self, *args, **options):
        self.encrypt = options.get('encrypt', False)
        self.compress = options.get('compress', False)
        self.servername = options.get('servername') or settings.HOSTNAME
        try:
            self.media_storage = get_storage_class()()
            self.storage = BaseStorage.storage_factory()
            self.backup_mediafiles()
            if options.get('clean'):
                self._cleanup_old_backups()

        except StorageError as err:
            raise CommandError(err)

    def backup_mediafiles(self):
        """
        Create backup file and write it to storage.
        """
        # Create file name
        extension = "tar%s" % ('.gz' if self.compress else '')
        filename = utils.filename_generate(extension,
                                           servername=self.servername,
                                           content_type=self.content_type)

        outputfile = self._create_tar(filename)

        if self.encrypt:
            encrypted_file = utils.encrypt_file(outputfile, filename)
            outputfile, filename = encrypted_file

        self.logger.debug("Backup size: %s", utils.handle_size(outputfile))
        self.logger.info("Writing file to %s" % filename)
        self.storage.write_file(outputfile, filename)

    def _explore_storage(self):
        """Generator of a all files contained in media storage."""
        path = ''
        dirs = [path]
        while dirs:
            path = dirs.pop()
            subdirs, files = self.media_storage.listdir(path)
            for media_filename in files:
                yield os.path.join(path, media_filename)
            dirs.extend([os.path.join(path, subdir) for subdir in subdirs])

    def _create_tar(self, name):
        """Create TAR file."""
        fileobj = utils.create_spooled_temporary_file()
        tar_file = tarfile.open(name=name, fileobj=fileobj, mode='w:gz') \
            if self.compress \
            else tarfile.open(name=name, fileobj=fileobj, mode='w')
        for media_filename in self._explore_storage():
            tarinfo = tarfile.TarInfo(media_filename)
            media_file = self.media_storage.open(media_filename)
            tar_file.addfile(tarinfo, media_file)
        # Close the TAR for writing
        tar_file.close()
        return fileobj

    def _cleanup_old_backups(self):
        """
        Cleanup old backups, keeping the number of backups specified by
        DBBACKUP_CLEANUP_KEEP and any backups that occur on first of the month.
        """
        self.logger.info("Cleaning Old Backups for media files")
        file_list = self.storage.clean_old_backups(encrypted=self.encrypt,
                                                   compressed=self.compress,
                                                   keep_number=settings.CLEANUP_KEEP_MEDIA)
