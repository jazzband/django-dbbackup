import os
import subprocess
from django.conf import settings
from django.test import TestCase
from mock import patch
from dbbackup.management.commands.dbbackup import Command as DbbackupCommand
from dbbackup.dbcommands import DBCommands
from dbbackup.tests.utils import FakeStorage

TEST_DATABASE = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/tmp/foo.db', 'USER': 'foo', 'PASSWORD': 'bar', 'HOST': 'foo', 'PORT': 122}
GPG_PRIVATE_PATH = os.path.join(settings.BASE_DIR, 'tests/gpg/pubring.gpg')
DEV_NULL = open(os.devnull, 'w')


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

    def test_func(self):
        self.command.save_new_backup(TEST_DATABASE)

    def test_compress(self):
        self.command.compress = True
        self.command.save_new_backup(TEST_DATABASE)

    def test_encrypt(self):
        cmd = ('gpg --import %s' % GPG_PRIVATE_PATH).split()
        subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)
        self.command.encrypt = True
        self.command.save_new_backup(TEST_DATABASE)


@patch('sys.stdout', DEV_NULL)
class DbbackupCommandCleanupOldPassword(TestCase):
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


class DbbackupCommandCompressFile(TestCase):
    def setUp(self):
        open(TEST_DATABASE['NAME'], 'a+b').close()
        self.command = DbbackupCommand()
        self.command.database = TEST_DATABASE['NAME']
        self.command.dbcommands = DBCommands(TEST_DATABASE)
        self.command.storage = FakeStorage()
        self.command.stdout = DEV_NULL

    def test_compress_file(self):
        inputfile = open(TEST_DATABASE['NAME'])
        self.command.compress_file(inputfile)
