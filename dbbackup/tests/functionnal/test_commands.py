import os
import subprocess
from mock import patch
from django.test import TestCase
from django.core.management import execute_from_command_line
from dbbackup.tests.utils import TEST_DATABASE, HANDLED_FILES, clean_gpg_keys
from dbbackup.tests.utils import GPG_PUBLIC_PATH, DEV_NULL


@patch('django.conf.settings.DATABASES', {'default': TEST_DATABASE})
@patch('dbbackup.settings.STORAGE', 'dbbackup.tests.utils.FakeStorage')
class DbBackupCommandTest(TestCase):
    def setUp(self):
        cmd = ('gpg --import %s' % GPG_PUBLIC_PATH).split()
        subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)
        open(TEST_DATABASE['NAME'], 'a').close()

    def tearDown(self):
        HANDLED_FILES.clean()
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
