import os
import tempfile
import shutil
from io import BytesIO
from mock import patch
from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from dbbackup.storage.filesystem_storage import Storage as FileSystemStorage


class FileSystemStorageTest(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FileSystemStorage(location=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_delete_file(self):
        file_path = os.path.join(self.temp_dir, 'foo')
        open(file_path, 'w').close()
        self.storage.delete_file('foo')
        self.assertFalse(os.listdir(self.temp_dir))

    def test_list_directory(self):
        file_path1 = os.path.join(self.temp_dir, 'foo')
        file_path2 = os.path.join(self.temp_dir, 'bar')
        self.assertEqual(0, len(os.listdir(self.temp_dir)))
        open(file_path1, 'w').close()
        self.assertEqual(1, len(os.listdir(self.temp_dir)))
        open(file_path2, 'w').close()
        self.assertEqual(2, len(os.listdir(self.temp_dir)))

    def test_write_file(self):
        file_path = os.path.join(self.temp_dir, 'foo')
        self.storage.write_file(BytesIO(b'bar'), 'foo')
        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(open(file_path).read(), 'bar')

    def test_read_file(self):
        file_path = os.path.join(self.temp_dir, 'foo')
        with open(file_path, 'w') as fd:
            fd.write('bar')
        read_file = self.storage.read_file('foo')
        self.assertEqual(read_file.read(), b'bar')


class FileSystemStorageCheckTest(TestCase):
    def test_fail_location_is_none(self):
        with self.assertRaises(Exception):
            self.storage = FileSystemStorage(location=None)

    def test_fail_location_is_empty_str(self):
        with self.assertRaises(Exception):
            self.storage = FileSystemStorage(location='')

    def test_fail_no_location(self):
        with self.assertRaises(Exception):
            self.storage = FileSystemStorage()

    def test_fail_backup_in_media_file(self):
        with self.assertRaises(ImproperlyConfigured):
            self.storage = FileSystemStorage(location=settings.MEDIA_ROOT)

    @patch('django.conf.settings.DEBUG', True)
    def test_success_backup_in_media_file_debug(self):
        self.storage = FileSystemStorage(location=settings.MEDIA_ROOT)

    def test_success(self):
        self.storage = FileSystemStorage(location='foo')
