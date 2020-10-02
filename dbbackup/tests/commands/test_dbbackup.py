"""
Tests for dbbackup command.
"""
import os

from django.core.exceptions import ImproperlyConfigured
from six import StringIO
from django.core.management import execute_from_command_line

from mock import patch

from django.test import TestCase

from dbbackup.management.commands.dbbackup import Command as DbbackupCommand
from dbbackup.db.base import get_connector
from dbbackup.storage import get_storage
from dbbackup.tests.utils import (TEST_DATABASE, add_public_gpg, clean_gpg_keys,
                                  DEV_NULL)


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
