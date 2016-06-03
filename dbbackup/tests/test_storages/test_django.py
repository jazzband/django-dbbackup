import os
import tempfile
import shutil
from io import BytesIO
from django.test import TestCase
from dbbackup.storage.builtin_django import Storage as DjangoStorage


class DjangoStorageTest(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.storage = DjangoStorage(location=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_delete_file(self):
        file_path = os.path.join(self.temp_dir, 'foo')
        open(file_path, 'w').close()
        self.storage.delete_file('foo')
        self.assertFalse(os.path.exists(file_path))

    def test_list_directory(self):
        file_path = os.path.join(self.temp_dir, 'foo')
        open(file_path, 'w').close()
        files = self.storage.list_directory()
        self.assertEqual(len(files), 1)

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
