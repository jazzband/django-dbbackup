"""
Tests for mediabackup command.
"""
from mock import patch
from django.test import TestCase
from dbbackup.management.commands.mediabackup import Command as DbbackupCommand
from dbbackup.tests.utils import (FakeStorage, DEV_NULL, HANDLED_FILES,
                                  add_public_gpg)


class MediabackupBackupMediafilesTest(TestCase):
    def setUp(self):
        HANDLED_FILES.clean()
        self.command = DbbackupCommand()
        self.command.servername = 'foo-server'
        self.command.storage = FakeStorage()
        self.command.stdout = DEV_NULL
        self.command.compress = False
        self.command.encrypt = False

    def test_func(self):
        self.command.backup_mediafiles()
        self.assertEqual(1, len(HANDLED_FILES['written_files']))

    def test_compress(self):
        self.command.compress = True
        self.command.backup_mediafiles()
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        self.assertTrue(HANDLED_FILES['written_files'][0][0].endswith('.gz'))

    def test_encrypt(self):
        self.command.encrypt = True
        add_public_gpg()
        self.command.backup_mediafiles()
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        outputfile = HANDLED_FILES['written_files'][0][1]
        outputfile.seek(0)
        self.assertTrue(outputfile.read().startswith(b'-----BEGIN PGP MESSAGE-----'))

    def test_compress_and_encrypt(self):
        self.command.compress = True
        self.command.encrypt = True
        add_public_gpg()
        self.command.backup_mediafiles()
        self.assertEqual(1, len(HANDLED_FILES['written_files']))
        outputfile = HANDLED_FILES['written_files'][0][1]
        outputfile.seek(0)
        self.assertTrue(outputfile.read().startswith(b'-----BEGIN PGP MESSAGE-----'))


class MediabackupGetBackupFileListTest(TestCase):
    def setUp(self):
        self.skipTest("Doesn't work!")
        self.command = DbbackupCommand()
        self.command.servername = 'foo-server'
        self.command.storage = FakeStorage()

    def test_func(self):
        self.command.get_backup_file_list()


class MediabackupCleanUpOldBackupsTest(TestCase):
    def setUp(self):
        HANDLED_FILES.clean()
        self.command = DbbackupCommand()
        self.command.stdout = DEV_NULL
        self.command.encrypt = False
        self.command.compress = False
        self.command.servername = 'foo-server'
        self.command.storage = FakeStorage()
        HANDLED_FILES['written_files'] = [(f, None) for f in [
            '2015-02-06-042810.bak',
            '2015-02-07-042810.bak',
            '2015-02-08-042810.bak',
        ]]

    @patch('dbbackup.settings.CLEANUP_KEEP_MEDIA', 1)
    def test_func(self):
        self.command._cleanup_old_backups()
        self.assertEqual(2, len(HANDLED_FILES['deleted_files']))
