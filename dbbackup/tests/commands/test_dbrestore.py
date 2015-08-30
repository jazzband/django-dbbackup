from mock import patch

from django.test import TestCase
from django.core.management.base import CommandError
from django.conf import settings
from django.utils import six
from django.utils.six import BytesIO

from dbbackup.utils import unencrypt_file, uncompress_file
from dbbackup.management.commands.dbrestore import Command as DbrestoreCommand
from dbbackup.dbcommands import DBCommands
from dbbackup import utils
from dbbackup.tests.utils import (FakeStorage, ENCRYPTED_FILE, TEST_DATABASE,
                                  add_private_gpg, DEV_NULL, COMPRESSED_FILE,
                                  clean_gpg_keys, HANDLED_FILES)


@patch('dbbackup.management.commands.dbrestore.input', return_value='y')
@patch('dbbackup.settings.STORAGE', 'dbbackup.tests.utils.FakeStorage')
class DbrestoreCommandRestoreBackupTest(TestCase):
    def setUp(self):
        self.command = DbrestoreCommand()
        self.command.stdout = DEV_NULL
        self.command.uncompress = False
        self.command.decrypt = False
        self.command.backup_extension = 'bak'
        self.command.filepath = 'foofile'
        self.command.database = TEST_DATABASE
        self.command.dbcommands = DBCommands(TEST_DATABASE)
        self.command.passphrase = None
        self.command.interactive = True
        self.command.storage = FakeStorage()
        HANDLED_FILES.clean()
        add_private_gpg()

    def tearDown(self):
        clean_gpg_keys()

    def test_no_filepath(self, *args):
        # Create backup
        HANDLED_FILES['written_files'].append(
            (utils.filename_generate('foo'), BytesIO(b'bar')))
        # Check
        self.command.filepath = None
        self.command.restore_backup()

    def test_no_backup_found(self, *args):
        self.command.filepath = None
        with self.assertRaises(CommandError):
            self.command.restore_backup()

    def test_uncompress(self, *args):
        self.command.storage.file_read = COMPRESSED_FILE
        self.command.filepath = COMPRESSED_FILE
        HANDLED_FILES['written_files'].append((COMPRESSED_FILE, open(COMPRESSED_FILE, 'rb')))
        self.command.uncompress = True
        self.command.restore_backup()

    @patch('dbbackup.utils.getpass', return_value=None)
    def test_decrypt(self, *args):
        self.command.decrypt = True
        self.command.filepath = ENCRYPTED_FILE
        HANDLED_FILES['written_files'].append((ENCRYPTED_FILE, open(ENCRYPTED_FILE, 'rb')))
        self.command.restore_backup()


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


class DbrestoreCommandGetExtensionTest(TestCase):
    def setUp(self):
        self.command = DbrestoreCommand()

    def test_tar(self):
        ext = self.command.get_extension('foo.tar')
        self.assertEqual(ext, '.tar')

    def test_tar_gz(self):
        ext = self.command.get_extension('foo.tar.gz')
        self.assertEqual(ext, '.gz')

    def test_no_extension(self):
        ext = self.command.get_extension('foo')
        self.assertEqual(ext, '')


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
