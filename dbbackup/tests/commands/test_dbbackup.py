"""
Tests for dbbackup command.
"""
import os
from mock import patch

from django.test import TestCase
from django.utils import six

from dbbackup.management.commands.dbbackup import Command as DbbackupCommand
from dbbackup.dbcommands import DBCommands, MongoDBCommands
from dbbackup.tests.utils import (FakeStorage, TEST_DATABASE,
                                  add_public_gpg, clean_gpg_keys, DEV_NULL, TEST_MONGODB)


@patch('dbbackup.settings.GPG_RECIPIENT', 'test@test')
@patch('sys.stdout', DEV_NULL)
class DbbackupCommandSaveNewBackupTest(TestCase):
    def setUp(self):
        open(TEST_DATABASE['NAME'], 'a+b').close()
        self.command = DbbackupCommand()
        self.command.servername = 'foo-server'
        self.command.encrypt = False
        self.command.compress = False
        self.command.database = TEST_DATABASE['NAME']
        self.command.dbcommands = DBCommands(TEST_DATABASE)
        self.command.storage = FakeStorage()
        self.command.stdout = DEV_NULL
        self.command.filename = None
        self.command.path = None
        open(TEST_DATABASE['NAME']).close()

    def tearDown(self):
        clean_gpg_keys()
        os.remove(TEST_DATABASE['NAME'])

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
        self.command.save_new_backup(TEST_DATABASE)
        self.assertTrue(os.path.exists(self.command.path))
        # tearDown
        os.remove(self.command.path)


@patch('dbbackup.settings.GPG_RECIPIENT', 'test@test')
@patch('sys.stdout', DEV_NULL)
@patch('dbbackup.dbcommands.DBCommands.run_commands')
class DbbackupCommandSaveNewMongoBackupTest(TestCase):
    def setUp(self):
        self.command = DbbackupCommand()
        self.command.servername = 'foo-server'
        self.command.encrypt = False
        self.command.compress = False
        self.command.dbcommands = MongoDBCommands(TEST_MONGODB)
        self.command.storage = FakeStorage()
        self.command.stdout = DEV_NULL
        self.command.filename = None
        self.command.path = None

    def tearDown(self):
        clean_gpg_keys()

    def test_func(self, mock_run_commands):
        self.command._save_new_backup(TEST_DATABASE)
        self.assertTrue(mock_run_commands.called)


@patch('sys.stdout', DEV_NULL)
class DbbackupCommandCleanupOldBackupsTest(TestCase):
    def setUp(self):
        self.command = DbbackupCommand()
        self.command.database = TEST_DATABASE['NAME']
        self.command.dbcommands = DBCommands(TEST_DATABASE)
        self.command.storage = FakeStorage()
        self.command.clean = True
        self.command.clean_keep = 1
        self.command.stdout = DEV_NULL
        self.command.filename = None
        self.command.path = None

    def test_cleanup_old_backups(self):
        self.command._cleanup_old_backups(TEST_DATABASE)

    def test_cleanup_empty(self):
        self.command.storage.list_files = []
        self.command._cleanup_old_backups(TEST_DATABASE)


class DbbackupWriteLocallyTest(TestCase):
    def setUp(self):
        self.command = DbbackupCommand()
        self.command.database = TEST_DATABASE['NAME']
        self.command.dbcommands = DBCommands(TEST_DATABASE)
        self.command.storage = FakeStorage()
        self.command.stdout = DEV_NULL
        self.command.filename = None
        self.command.path = None

    def test_write(self):
        fd, path = six.BytesIO(b"foo"), '/tmp/foo.bak'
        self.command.write_local_file(fd, path)
        self.assertTrue(os.path.exists(path))
        # tearDown
        os.remove(path)
