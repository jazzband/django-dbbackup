from mock import patch
from django.test import TestCase
from dbbackup.storage.base import get_storage, BaseStorage
from dbbackup.tests.utils import HANDLED_FILES, FakeStorage

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


class StorageListBackupsTest(TestCase):
    def setUp(self):
        self.storage = FakeStorage()
        HANDLED_FILES['written_files'] = [(f, None) for f in [
            'foo.txt',
            'foo.db', 'foo.db.gz', 'foo.db.gpg', 'foo.db.gz.gpg',
            'foo.media', 'foo.media.gz', 'foo.media.gpg', 'foo.media.gz.gpg',
            'bar.db', 'bar.db.gz', 'bar.db.gpg', 'bar.db.gz.gpg',
            'bar.media', 'bar.media.gz', 'bar.media.gpg', 'bar.media.gz.gpg',
        ]]

    def tearDown(self):
        HANDLED_FILES.clean()

    def test_nofilter(self):
        files = self.storage.list_backups()
        self.assertEqual(len(HANDLED_FILES['written_files']), len(files))

    def test_encrypted(self):
        files = self.storage.list_backups(encrypted=True)
        self.assertEqual(8, len(files))
        for file in files:
            self.assertIn('.gpg', file)

    def test_compressed(self):
        files = self.storage.list_backups(compressed=True)
        self.assertEqual(8, len(files))
        for file in files:
            self.assertIn('.gz', file)

    def test_dbbackup(self):
        files = self.storage.list_backups(content_type='db')
        self.assertEqual(8, len(files))
        for file in files:
            self.assertIn('.db', file)

    def test_database(self):
        files = self.storage.list_backups(database='foo')
        self.assertEqual(9, len(files))
        for file in files:
            self.assertIn('foo', file)

    def test_mediabackup(self):
        files = self.storage.list_backups(content_type='media')
        self.assertEqual(8, len(files))
        for file in files:
            self.assertIn('.media', file)


class StorageGetLatestTest(TestCase):
    def setUp(self):
        self.storage = FakeStorage()
        HANDLED_FILES['written_files'] = [(f, None) for f in [
            '2015-02-06-042810.bak',
            '2015-02-07-042810.bak',
            '2015-02-08-042810.bak',
        ]]

    def tearDown(self):
        HANDLED_FILES.clean()

    def test_func(self):
        filename = self.storage.get_latest_backup()
        self.assertEqual(filename, '2015-02-08-042810.bak')


class StorageGetMostRecentTest(TestCase):
    def setUp(self):
        self.storage = FakeStorage()
        HANDLED_FILES['written_files'] = [(f, None) for f in [
            '2015-02-06-042810.bak',
            '2015-02-07-042810.bak',
            '2015-02-08-042810.bak',
        ]]

    def tearDown(self):
        HANDLED_FILES.clean()

    def test_func(self):
        filename = self.storage.get_older_backup()
        self.assertEqual(filename, '2015-02-06-042810.bak')


class StorageCleanOldBackupsTest(TestCase):
    def setUp(self):
        self.storage = FakeStorage()
        HANDLED_FILES['written_files'] = [(f, None) for f in [
            '2015-02-06-042810.bak',
            '2015-02-07-042810.bak',
            '2015-02-08-042810.bak',
        ]]

    def tearDown(self):
        HANDLED_FILES.clean()

    def test_func(self):
        self.storage.clean_old_backups(keep_number=1)
        self.assertEqual(2, len(HANDLED_FILES['deleted_files']))
