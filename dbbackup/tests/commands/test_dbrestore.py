"""
Tests for dbrestore command.
"""
from mock import patch
from tempfile import mktemp
from shutil import copyfileobj

from django.test import TestCase
from django.core.management.base import CommandError
from django.conf import settings

from dbbackup import utils
from dbbackup.db.base import get_connector
from dbbackup.db.mongodb import MongoDumpConnector
from dbbackup.management.commands.dbrestore import Command as DbrestoreCommand
from dbbackup.tests.utils import (FakeStorage, TEST_DATABASE,
                                  add_private_gpg, DEV_NULL,
                                  clean_gpg_keys, HANDLED_FILES, TEST_MONGODB, TARED_FILE,
                                  get_dump, get_dump_name)


@patch('django.conf.settings.DATABASES', {'default': TEST_DATABASE})
@patch('dbbackup.management.commands._base.input', return_value='y')
class DbrestoreCommandRestoreBackupTest(TestCase):
    def setUp(self):
        self.command = DbrestoreCommand()
        self.command.stdout = DEV_NULL
        self.command.uncompress = False
        self.command.decrypt = False
        self.command.backup_extension = 'bak'
        self.command.filename = 'foofile'
        self.command.database = TEST_DATABASE
        self.command.passphrase = None
        self.command.interactive = True
        self.command.storage = FakeStorage()
        self.command.connector = get_connector()
        HANDLED_FILES.clean()

    def tearDown(self):
        clean_gpg_keys()

    def test_no_filename(self, *args):
        # Prepare backup
        HANDLED_FILES['written_files'].append(
            (utils.filename_generate('foo'), get_dump()))
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
        self.command.path = None
        compressed_file, self.command.filename = utils.compress_file(get_dump(), get_dump_name())
        HANDLED_FILES['written_files'].append(
            (self.command.filename, compressed_file)
        )
        self.command.uncompress = True
        self.command._restore_backup()

    @patch('dbbackup.utils.getpass', return_value=None)
    def test_decrypt(self, *args):
        self.command.path = None
        self.command.decrypt = True
        encrypted_file, self.command.filename = utils.encrypt_file(get_dump(), get_dump_name())
        HANDLED_FILES['written_files'].append(
            (self.command.filename, encrypted_file)
        )
        self.command._restore_backup()

    def test_path(self, *args):
        temp_dump = get_dump()
        dump_path = mktemp()
        with open(dump_path, 'wb') as dump:
            copyfileobj(temp_dump, dump)
        self.command.path = dump.name
        self.command._restore_backup()
        self.command.decrypt = False
        self.command.filepath = get_dump_name()
        HANDLED_FILES['written_files'].append(
            (self.command.filepath, get_dump())
        )
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


@patch('dbbackup.management.commands._base.input', return_value='y')
@patch('dbbackup.db.mongodb.MongoDumpConnector.restore_dump')
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
        self.command.passphrase = None
        self.command.interactive = True
        self.command.storage = FakeStorage()
        self.command.connector = MongoDumpConnector()
        HANDLED_FILES.clean()
        add_private_gpg()

    def test_mongo_settings_backup_command(self, mock_runcommands, *args):
        self.command.storage.file_read = TARED_FILE
        self.command.filename = TARED_FILE
        HANDLED_FILES['written_files'].append((TARED_FILE, open(TARED_FILE, 'rb')))
        self.command._restore_backup()
        self.assertTrue(mock_runcommands.called)
