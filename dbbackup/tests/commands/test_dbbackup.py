import os
from mock import patch

from django.test import TestCase
from django.utils import six

from dbbackup.management.commands.dbbackup import Command as DbbackupCommand
from dbbackup.dbcommands import DBCommands
from dbbackup.tests.utils import (FakeStorage, TEST_DATABASE,
                                  add_public_gpg, clean_gpg_keys, DEV_NULL)


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
        open(TEST_DATABASE['NAME']).close()

    def tearDown(self):
        clean_gpg_keys()
        os.remove(TEST_DATABASE['NAME'])

    def test_func(self):
        self.command.save_new_backup(TEST_DATABASE)

    def test_compress(self):
        self.command.compress = True
        self.command.save_new_backup(TEST_DATABASE)

    def test_encrypt(self):
        add_public_gpg()
        self.command.encrypt = True
        self.command.save_new_backup(TEST_DATABASE)


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

    def test_cleanup_old_backups(self):
        self.command.cleanup_old_backups(TEST_DATABASE)

    def test_cleanup_empty(self):
        self.command.storage.list_files = []
        self.command.cleanup_old_backups(TEST_DATABASE)
