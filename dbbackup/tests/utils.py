import os
from django.conf import settings
from dbbackup.storage.base import BaseStorage

BASE_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt')
ENCRYPTED_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt.gpg')
COMPRESSED_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt.gz')
ENCRYPTED_COMPRESSED_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt.gz.gpg')
TEST_DATABASE = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/tmp/foo.db', 'USER': 'foo', 'PASSWORD': 'bar', 'HOST': 'foo', 'PORT': 122}

GPG_PRIVATE_PATH = os.path.join(settings.BASE_DIR, 'tests/gpg/secring.gpg')
GPG_PUBLIC_PATH = os.path.join(settings.BASE_DIR, 'tests/gpg/pubring.gpg')
DEV_NULL = open(os.devnull, 'w')


class FakeStorage(BaseStorage):
    name = 'FakeStorage'
    list_files = ['foo', 'bar']
    deleted_files = []
    file_read = ENCRYPTED_FILE

    def delete_file(self, filepath):
        self.deleted_files.append(filepath)

    def list_directory(self, raw=False):
        return self.list_files

    def write_file(self, filehandle, filename):
        pass

    def read_file(self, filepath):
        return open(self.file_read, 'rb')
