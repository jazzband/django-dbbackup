import re
from mock import patch, Mock

from django.test import TestCase
from django.utils.six import BytesIO
from django.core.files.base import ContentFile

from dbbackup.storage.dropbox_storage import Storage as DropBoxStorage
from dbbackup.storage.base import StorageError

FILE_FIXTURE = {
    'bytes': 4,
    'client_mtime': 'Mon, 24 Aug 2015 15:06:41 +0000',
    'icon': 'page_white_text',
    'is_dir': False,
    'mime_type': 'text/plain',
    'modified': 'Mon, 24 Aug 2015 15:06:41 +0000',
    'path': '/foo.txt',
    'rev': '23b7cdd80',
    'revision': 2,
    'root': 'app_folder',
    'size': '4 bytes',
    'thumb_exists': False
}
FILES_FIXTURE = {
    'bytes': 0,
    'contents': [
        FILE_FIXTURE,
        {'bytes': 0,
         'icon': 'folder',
         'is_dir': True,
         'modified': 'Mon, 6 Feb 2015 15:06:40 +0000',
         'path': '/bar',
         'rev': '33b7cdd80',
         'revision': 3,
         'root': 'app_folder',
         'size': '0 bytes',
         'thumb_exists': False}
    ],
    'hash': 'aeaa0ed65aa4f88b96dfe3d553280efc',
    'icon': 'folder',
    'is_dir': True,
    'path': '/',
    'root': 'app_folder',
    'size': '0 bytes',
    'thumb_exists': False
}

class MockDropboxOAuth2Session(Mock):
    build_url = None
    API_HOST = 'foo'
    root = 'foo/'

    def build_access_headers(self, *args, **kwargs):
        return {}, {}     


class DropboxStorageTest(TestCase):
    @patch('dropbox.client._OAUTH2_ACCESS_TOKEN_PATTERN',
           re.compile(r'.*'))
    @patch('dropbox.client.DropboxOAuth2Session',
           MockDropboxOAuth2Session)
    def setUp(self, *args):
        self.storage = DropBoxStorage(oauth2_access_token='foo_token')

    @patch('dropbox.client.DropboxClient.file_delete',
           return_value=FILE_FIXTURE)
    def test_delete_file(self, *args):
        self.storage.delete_file('foo')

    @patch('dropbox.client.DropboxClient.metadata', return_value=FILES_FIXTURE)
    def test_list_directory(self, *args):
        files = self.storage.list_directory()
        self.assertGreater(len(files), 0)

    @patch('dropbox.client.DropboxClient.put_file', return_value='foo')
    @patch('storages.backends.dropbox.DropBoxStorage.exists', return_value=False)
    def test_write_file(self, *args):
        self.storage.write_file(BytesIO(b'bar'), 'foo')

    @patch('dropbox.client.DropboxClient.get_file',
           return_value=ContentFile(b'bar'))
    def test_read_file(self, *args):
        read_file = self.storage.read_file('foo')
        self.assertEqual(read_file.read(), b'bar')

    def test_check(self, *args):
        with self.assertRaises(StorageError):
            self.storage._check_settings({})
