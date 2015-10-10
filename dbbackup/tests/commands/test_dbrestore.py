"""
Tests for dbrestore command.
"""
import os
from mock import patch

from django.test import TestCase
from django.core.management.base import CommandError
from django.conf import settings
from django.utils.six import BytesIO

from dbbackup.utils import unencrypt_file, uncompress_file
from dbbackup.management.commands.dbrestore import Command as DbrestoreCommand
from dbbackup.dbcommands import DBCommands, MongoDBCommands
from dbbackup import utils
from dbbackup.tests.utils import (FakeStorage, ENCRYPTED_FILE, TEST_DATABASE,
                                  add_private_gpg, DEV_NULL, COMPRESSED_FILE,
                                  clean_gpg_keys, HANDLED_FILES, TEST_MONGODB, TARED_FILE)


@patch('dbbackup.management.commands.dbrestore.input', return_value='y')
@patch('dbbackup.settings.STORAGE', 'dbbackup.tests.utils.FakeStorage')
class DbrestoreCommandRestoreBackupTest(TestCase):
    def setUp(self):
        self.command = DbrestoreCommand()
        self.command.stdout = DEV_NULL
        self.command.uncompress = False
        self.command.decrypt = False
        self.command.backup_extension = 'bak'
        self.command.filename = 'foofile'
        self.command.database = TEST_DATABASE
        self.command.dbcommands = DBCommands(TEST_DATABASE)
        self.command.passphrase = None
        self.command.interactive = True
        self.command.storage = FakeStorage()
        HANDLED_FILES.clean()
        add_private_gpg()

    def tearDown(self):
        clean_gpg_keys()

    def test_no_filename(self, *args):
        # Prepare backup
        HANDLED_FILES['written_files'].append(
            (utils.filename_generate('foo'), BytesIO(b'bar')))
        # Check
        self.command.path = None
        self.command.filename = None
        self.command._restore_backup()

    def test_no_backup_found(self, *args):
        self.command.path = None
        self.command.filename = None
        with self.assertRaises(CommandError):
            self.command._restore_backup()

    def test_uncompress(self, *args):
        self.command.storage.file_read = COMPRESSED_FILE
        self.command.path = None
        self.command.filename = COMPRESSED_FILE
        HANDLED_FILES['written_files'].append((COMPRESSED_FILE, open(COMPRESSED_FILE, 'rb')))
        self.command.uncompress = True
        self.command._restore_backup()

    @patch('dbbackup.utils.getpass', return_value=None)
    def test_decrypt(self, *args):
        self.command.path = None
        self.command.decrypt = True
        self.command.filename = ENCRYPTED_FILE
        HANDLED_FILES['written_files'].append((ENCRYPTED_FILE, open(ENCRYPTED_FILE, 'rb')))
        self.command._restore_backup()


class DbrestoreCommandGetDatabaseTest(TestCase):
    def setUp(self):
        self.command = DbrestoreCommand()

    def test_give_db_name(self):
        db = self.command._get_database({'database': 'default'})
        self.assertEqual(db, settings.DATABASES['default'])

    def test_no_given_db(self):
        db = self.command._get_database({})
        self.assertEqual(db, settings.DATABASES['default'])

    @patch('django.conf.settings.DATABASES', {'db1': {}, 'db2': {}})
    def test_no_given_db_multidb(self):
        with self.assertRaises(CommandError):
            self.command._get_database({})


@patch('dbbackup.management.commands.dbrestore.input', return_value='y')
@patch('dbbackup.settings.STORAGE', 'dbbackup.tests.utils.FakeStorage')
@patch('dbbackup.dbcommands.DBCommands.run_commands')
class DbMongoRestoreCommandRestoreBackupTest(TestCase):
    def setUp(self):
        self.command = DbrestoreCommand()
        self.command.stdout = DEV_NULL
        self.command.uncompress = False
        self.command.decrypt = False
        self.command.backup_extension = 'bak'
        self.command.path = None
        self.command.filename = 'foofile'
        self.command.database = TEST_MONGODB
        self.command.dbcommands = MongoDBCommands(TEST_MONGODB)
        self.command.passphrase = None
        self.command.interactive = True
        self.command.storage = FakeStorage()
        HANDLED_FILES.clean()
        add_private_gpg()

    def test_mongo_settings_backup_command(self, mock_runcommands, *args):
        self.command.storage.file_read = TARED_FILE
        self.command.filename = TARED_FILE
        HANDLED_FILES['written_files'].append((TARED_FILE, open(TARED_FILE, 'rb')))
        self.command._restore_backup()
        self.assertTrue(mock_runcommands.called)


class DbrestoreCommandUncompressTest(TestCase):
    def setUp(self):
        self.command = DbrestoreCommand()

    def test_uncompress(self):
        inputfile = open(COMPRESSED_FILE, 'rb')
        fd, basename = uncompress_file(inputfile, "whatever")
        fd.seek(0)
        self.assertEqual(fd.read(), b'foo\n')


class DbrestoreCommandDecryptTest(TestCase):
    def setUp(self):
        self.command = DbrestoreCommand()
        self.command.passphrase = None
        add_private_gpg()

    def tearDown(self):
        clean_gpg_keys()

    @patch('dbbackup.management.commands.dbrestore.input', return_value=None)
    @patch('dbbackup.utils.getpass', return_value=None)
    def test_decrypt(self, *args):
        inputfile = open(ENCRYPTED_FILE, 'r+b')
        uncryptfile, filename = unencrypt_file(inputfile, 'foofile.gpg')
        uncryptfile.seek(0)
        self.assertEqual(b'foo\n', uncryptfile.read())


class DbbackupReadLocalFileTest(TestCase):
    def setUp(self):
        self.command = DbrestoreCommand()
        self.command.path = '/tmp/foo.bak'

    def test_read(self):
        # setUp
        open(self.command.path, 'w').close()
        # Test
        output_file = self.command.read_local_file(self.command.path)
        # tearDown
        os.remove(self.command.path)
