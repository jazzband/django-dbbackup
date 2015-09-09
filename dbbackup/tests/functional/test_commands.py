import os
import subprocess
from io import BytesIO
from mock import patch
from django.test import TestCase
from django.core.management import execute_from_command_line
from dbbackup.tests.utils import TEST_DATABASE, HANDLED_FILES, clean_gpg_keys
from dbbackup.tests.utils import GPG_PUBLIC_PATH, DEV_NULL

from dbbackup.utils import six


@patch('django.conf.settings.DATABASES', {'default': TEST_DATABASE})
@patch('dbbackup.settings.STORAGE', 'dbbackup.tests.utils')
class DbBackupCommandTest(TestCase):
    def setUp(self):
        HANDLED_FILES.clean()
        cmd = ('gpg --import %s' % GPG_PUBLIC_PATH).split()
        subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)
        open(TEST_DATABASE['NAME'], 'a').close()

    def tearDown(self):
        os.remove(TEST_DATABASE['NAME'])
        clean_gpg_keys()

    def test_encrypt(self):
        argv = ['', 'dbbackup', '--encrypt']
        execute_from_command_line(argv)
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        filename, outputfile = HANDLED_FILES['written_files'][0]
        self.assertTrue(filename.endswith('.gpg'))

    def test_compress(self):
        argv = ['', 'dbbackup', '--compress']
        execute_from_command_line(argv)
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        filename, outputfile = HANDLED_FILES['written_files'][0]
        self.assertTrue(filename.endswith('.gz'))

    def test_compress_and_encrypt(self):
        argv = ['', 'dbbackup', '--compress', '--encrypt']
        execute_from_command_line(argv)
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        filename, outputfile = HANDLED_FILES['written_files'][0]
        self.assertTrue(filename.endswith('.gz.gpg'))


# TODO: Add fake database to restore
@patch('django.conf.settings.DATABASES', {'default': TEST_DATABASE})
@patch('dbbackup.settings.STORAGE', 'dbbackup.tests.utils')
@patch('dbbackup.management.commands.dbrestore.input', return_value='y')
class DbRestoreCommandTest(TestCase):
    def setUp(self):
        if six.PY3:
            self.skipTest("Compression isn't implemented in Python3")
        HANDLED_FILES.clean()
        cmd = ('gpg --import %s' % GPG_PUBLIC_PATH).split()
        subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)
        open(TEST_DATABASE['NAME'], 'a').close()

    def tearDown(self):
        os.remove(TEST_DATABASE['NAME'])
        clean_gpg_keys()

    def test_restore(self, *args):
        # Create backup
        execute_from_command_line(['', 'dbbackup'])
        # Restore
        execute_from_command_line(['', 'dbrestore'])

    # @patch('dbbackup.utils.getpass', return_value=None)
    # def test_encrypted(self, *args):
    #     # Create backup
    #     execute_from_command_line(['', 'dbbackup', '--encrypt'])
    #     # Restore
    #     execute_from_command_line(['', 'dbrestore', '--decrypt'])

    def test_compressed(self, *args):
        # Create backup
        execute_from_command_line(['', 'dbbackup', '--compress'])
        # Restore
        execute_from_command_line(['', 'dbrestore', '--uncompress'])

    def test_no_backup_available(self, *args):
        with self.assertRaises(SystemExit):
            execute_from_command_line(['', 'dbrestore'])

    # @patch('dbbackup.utils.getpass', return_value=None)
    # def test_available_but_not_encrypted(self, *args):
    #     # Create backup
    #     execute_from_command_line(['', 'dbbackup'])
    #     # Restore
    #     with self.assertRaises(Exception):
    #         execute_from_command_line(['', 'dbrestore', '--decrypt'])

    # def test_available_but_not_compressed(self, *args):
    #     # Create backup
    #     execute_from_command_line(['', 'dbbackup'])
    #     # Restore
    #     with self.assertRaises(Exception):
    #         execute_from_command_line(['', 'dbrestore', '--uncompress'])


@patch('dbbackup.settings.STORAGE', 'dbbackup.tests.utils')
class MediaBackupCommandTest(TestCase):
    def setUp(self):
        HANDLED_FILES.clean()
        cmd = ('gpg --import %s' % GPG_PUBLIC_PATH).split()
        subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)

    def tearDown(self):
        clean_gpg_keys()

    def test_encrypt(self):
        argv = ['', 'mediabackup', '--encrypt']
        execute_from_command_line(argv)
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        filename, outputfile = HANDLED_FILES['written_files'][0]
        # self.assertTrue('.gpg' in filename)

    def test_no_compress(self):
        argv = ['', 'mediabackup', '--no-compress']
        execute_from_command_line(argv)
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        filename, outputfile = HANDLED_FILES['written_files'][0]
        # self.assertFalse('.gz' in filename)

    def test_no_compress_and_encrypt(self):
        argv = ['', 'mediabackup', '--no-compress', '--encrypt']
        execute_from_command_line(argv)
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        filename, outputfile = HANDLED_FILES['written_files'][0]
        # self.assertTrue('.gpg' in filename)
        # self.assertFalse('.gz' in filename)
