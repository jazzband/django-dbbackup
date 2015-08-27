from mock import patch
from django.test import TestCase
from dbbackup.storage.base import get_storage, BaseStorage
from dbbackup.tests.utils import FakeStorage

DEFAULT_STORAGE_PATH = 'dbbackup.storage.filesystem_storage'
STORAGE_OPTIONS = {'location': '/tmp'}


class Get_StorageTest(TestCase):
    @patch('dbbackup.settings.STORAGE', DEFAULT_STORAGE_PATH)
    @patch('dbbackup.settings.STORAGE_OPTIONS', STORAGE_OPTIONS)
    def test_func(self, *args):
        storage = get_storage()
        self.assertEqual(storage.__module__, DEFAULT_STORAGE_PATH)

    def test_set_path(self):
        storage = get_storage(path=FakeStorage.__module__)
        self.assertIsInstance(storage, FakeStorage)

    @patch('dbbackup.settings.STORAGE', DEFAULT_STORAGE_PATH)
    def test_set_options(self, *args):
        storage = get_storage(options=STORAGE_OPTIONS)
        self.assertEqual(storage.__module__, DEFAULT_STORAGE_PATH)


class BaseStorageTest(TestCase):
    def setUp(self):
        self.storageCls = BaseStorage
        self.storageCls.name = 'foo'
        self.storage = BaseStorage()
