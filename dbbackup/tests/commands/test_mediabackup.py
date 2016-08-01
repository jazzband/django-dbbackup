"""
Tests for mediabackup command.
"""
from django.test import TestCase
from django.core.files.storage import get_storage_class
from dbbackup.management.commands.mediabackup import Command as DbbackupCommand
from dbbackup.storage import get_storage
from dbbackup.tests.utils import DEV_NULL, HANDLED_FILES, add_public_gpg


class MediabackupBackupMediafilesTest(TestCase):
    def setUp(self):
        HANDLED_FILES.clean()
        self.command = DbbackupCommand()
        self.command.servername = 'foo-server'
        self.command.storage = get_storage()
        self.command.stdout = DEV_NULL
        self.command.compress = False
        self.command.encrypt = False
        self.command.path = None
        self.command.media_storage = get_storage_class()()

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
