"""
S3 Storage object.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
from boto.s3.key import Key
from boto.s3.connection import S3Connection
from io import BytesIO
from django.conf import settings
from tempfile import SpooledTemporaryFile
from .base import BaseStorage, StorageError


class Storage(BaseStorage):
    """ S3 API Storage. """
    S3_BUCKET = getattr(settings, 'DBBACKUP_S3_BUCKET', None)
    S3_ACCESS_KEY = getattr(settings, 'DBBACKUP_S3_ACCESS_KEY', None)
    S3_SECRET_KEY = getattr(settings, 'DBBACKUP_S3_SECRET_KEY', None)
    S3_DOMAIN = getattr(settings, 'DBBACKUP_S3_DOMAIN', 's3.amazonaws.com')
    S3_IS_SECURE = getattr(settings, 'DBBACKUP_S3_USE_SSL', True)
    S3_DIRECTORY = getattr(settings, 'DBBACKUP_S3_DIRECTORY', "django-dbbackups/")
    if S3_DIRECTORY:
        S3_DIRECTORY = '%s/' % S3_DIRECTORY.strip('/')

    def __init__(self, server_name=None):
        self._check_filesystem_errors()
        self.name = 'AmazonS3'
        self.conn = S3Connection(aws_access_key_id=self.S3_ACCESS_KEY,
            aws_secret_access_key=self.S3_SECRET_KEY, host=self.S3_DOMAIN,
            is_secure=self.S3_IS_SECURE)
        self.bucket = self.conn.get_bucket(self.S3_BUCKET)
        BaseStorage.__init__(self)

    def _check_filesystem_errors(self):
        if not self.S3_BUCKET:
            raise StorageError('Filesystem storage requires DBBACKUP_S3_BUCKET to be defined in settings.')
        if not self.S3_ACCESS_KEY:
            raise StorageError('Filesystem storage requires DBBACKUP_S3_ACCESS_KEY to be defined in settings.')
        if not self.S3_SECRET_KEY:
            raise StorageError('Filesystem storage requires DBBACKUP_S3_SECRET_KEY to be defined in settings.')

    def backup_dir(self):
        return self.S3_DIRECTORY

    def delete_file(self, filepath):
        self.bucket.delete_key(filepath)

    def list_directory(self):
        return [k.name for k in self.bucket.list(prefix=self.S3_DIRECTORY)]

    def write_file(self, filehandle, filename):
        # Use multipart upload because normal upload maximum is 5 GB.
        filepath = os.path.join(self.S3_DIRECTORY, filename)
        filehandle.seek(0)
        handle = self.bucket.initiate_multipart_upload(filepath)
        try:
            chunk = 1
            while True:
                chunkdata = filehandle.read(5 * 1024 * 1024)
                if not chunkdata:
                    break
                tmpfile = BytesIO(chunkdata)
                tmpfile.seek(0)
                handle.upload_part_from_file(tmpfile, chunk)
                tmpfile.close()
                chunk += 1
            handle.complete_upload()
        except Exception:
            handle.cancel_upload()
            raise

    def read_file(self, filepath):
        """ Read the specified file and return it's handle. """
        key = Key(self.bucket)
        key.key = filepath
        filehandle = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
        key.get_contents_to_file(filehandle)
        return filehandle
