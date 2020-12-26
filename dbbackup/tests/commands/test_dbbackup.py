"""
Tests for dbbackup command.
"""
import os

from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import FileSystemStorage
from six import StringIO
from django.core.management import execute_from_command_line

from mock import patch

from django.test import TestCase
from storages.backends.s3boto3 import S3Boto3Storage

from dbbackup.management.commands.dbbackup import Command as DbbackupCommand
from dbbackup.db.base import get_connector
from dbbackup.storage import get_storage, get_backup_storage
from dbbackup.tests.utils import (TEST_DATABASE, add_public_gpg, clean_gpg_keys,
                                  DEV_NULL, FakeStorage)


@patch('dbbackup.settings.GPG_RECIPIENT', 'test@test')
@patch('sys.stdout', DEV_NULL)
class DbbackupCommandSaveNewBackupTest(TestCase):
    def setUp(self):
        self.command = DbbackupCommand()
        self.command.servername = 'foo-server'
        self.command.encrypt = False
        self.command.compress = False
        self.command.database = TEST_DATABASE['NAME']
        self.command.storage = get_storage()
        self.command.connector = get_connector()
        self.command.stdout = DEV_NULL
        self.command.filename = None
        self.command.path = None

    def tearDown(self):
        clean_gpg_keys()

    def test_func(self):
        self.command._save_new_backup(TEST_DATABASE)

    def test_compress(self):
        self.command.compress = True
        self.command._save_new_backup(TEST_DATABASE)

    def test_encrypt(self):
        add_public_gpg()
        self.command.encrypt = True
        self.command._save_new_backup(TEST_DATABASE)

    def test_path(self):
        self.command.path = '/tmp/foo.bak'
        self.command._save_new_backup(TEST_DATABASE)
        self.assertTrue(os.path.exists(self.command.path))
        # tearDown
        os.remove(self.command.path)

    def test_fallback(self):
        stdout = StringIO()
        with self.assertRaises(ImproperlyConfigured) as ic:
            with patch('sys.stdout', stdout):
                execute_from_command_line(['', 'dbbackup', '--storage=s3'])
        self.assertEqual(str(ic.exception),
                         'You must specify a storage class using DBBACKUP_STORAGES settings.')

        # TODO: Update DBBACKUP_FALLBACK_STORAGE and verify successful backup.


@patch('dbbackup.settings.GPG_RECIPIENT', 'test@test')
@patch('sys.stdout', DEV_NULL)
@patch('dbbackup.db.sqlite.SqliteConnector.create_dump')
@patch('dbbackup.utils.handle_size', returned_value=4.2)
class DbbackupCommandSaveNewMongoBackupTest(TestCase):
    def setUp(self):
        self.command = DbbackupCommand()
        self.command.servername = 'foo-server'
        self.command.encrypt = False
        self.command.compress = False
        self.command.storage = get_storage()
        self.command.stdout = DEV_NULL
        self.command.filename = None
        self.command.path = None
        self.command.connector = get_connector('default')

    def tearDown(self):
        clean_gpg_keys()

    def test_func(self, mock_run_commands, mock_handle_size):
        self.command._save_new_backup(TEST_DATABASE)
        self.assertTrue(mock_run_commands.called)


class DbbackupCommandSaveMultipleStorages(TestCase):
    def setUp(self):
        self.command = DbbackupCommand()
        self.command.servername = 'foo-server'
        self.command.encrypt = False
        self.command.compress = False
        self.command.connector = get_connector()
        self.command.stdout = DEV_NULL
        self.command.filename = None
        self.command.path = None

    def test_default_func(self):
        self.command.database = TEST_DATABASE['NAME']
        self.command.storage = get_backup_storage('default')
        self.command._save_new_backup(TEST_DATABASE)

    def test_fake_func(self):
        self.command.database = TEST_DATABASE['NAME']
        self.command.storage = get_backup_storage('fake_storage')
        self.command._save_new_backup(TEST_DATABASE)

    def test_default(self):
        self.storage = get_backup_storage('default')
        self.assertIsInstance(self.storage.storage, FileSystemStorage)
        
    
class DbbackupCommandMultipleStorages(TestCase):
    def setUp(self):
        self.command = DbbackupCommand()
        self.command.stdout = DEV_NULL
        self.command.uncompress = False
        self.command.decrypt = False
        self.command.backup_extension = 'bak'
        self.command.filename = 'foofile'
        self.command.database = TEST_DATABASE
        self.command.passphrase = None
        self.command.interactive = True
        self.command.database_name = 'default'
        self.command.connector = get_connector('default')

    @staticmethod
    def fake_backup():
        return True

    def test_default(self):
        self.command.handle(storage='default', verbosity=1)
        self.assertIsInstance(self.command.storage.storage, FileSystemStorage)

    @patch.object(DbbackupCommand, '_save_new_backup')
    def test_fake(self, fake_backup):
        self.command.handle(storage='fake_storage', verbosity=1)
        self.assertIsInstance(self.command.storage.storage, FakeStorage)

    @patch.object(DbbackupCommand, '_save_new_backup')
    def test_S3(self, fake_backup):
        self.command.handle(storage='s3_storage', verbosity=1)
        self.assertIsInstance(self.command.storage.storage, S3Boto3Storage)
        self.assertEqual(vars(self.command.storage.storage)['_constructor_args'][1],
                         {'access_key': 'my_id',
                          'secret_key': 'my_secret',
                          'bucket_name': 'my_bucket_name',
                          'default_acl': 'private'})
