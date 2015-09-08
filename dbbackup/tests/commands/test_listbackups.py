from mock import patch
from django.test import TestCase
from django.core.management import execute_from_command_line
from django.utils.six import StringIO
from dbbackup.management.commands.listbackups import Command as ListbackupsCommand
from dbbackup.tests.utils import HANDLED_FILES, FakeStorage, TEST_DATABASE


class ListbackupsCommandTest(TestCase):
    def setUp(self):
        self.command = ListbackupsCommand()
        self.command.storage = FakeStorage()
        HANDLED_FILES['written_files'] = [(f, None) for f in [
            '2015-02-06-042810.bak',
            '2015-02-07-042810.bak',
            '2015-02-08-042810.bak',
        ]]

    def test_get_backup_attrs(self):
        options = {}
        attrs = self.command.get_backup_attrs(options)
        self.assertEqual(len(HANDLED_FILES['written_files']), len(attrs))


@patch('django.conf.settings.DATABASES', {'default': TEST_DATABASE})
@patch('dbbackup.settings.STORAGE', 'dbbackup.tests.utils')
class ListbackupsCommandArgComputingTest(TestCase):
    def setUp(self):
        HANDLED_FILES['written_files'] = [(f, None) for f in [
            '2015-02-06-042810_foo.db', '2015-02-06-042810_foo.db.gz',
            '2015-02-06-042810_foo.db.gpg', '2015-02-06-042810_foo.db.gz.gpg',
            '2015-02-06-042810_foo.media', '2015-02-06-042810_foo.media.gz',
            '2015-02-06-042810_foo.media.gpg', '2015-02-06-042810_foo.media.gz.gpg',
            '2015-02-06-042810_bar.db', '2015-02-06-042810_bar.db.gz',
            '2015-02-06-042810_bar.db.gpg', '2015-02-06-042810_bar.db.gz.gpg',
            '2015-02-06-042810_bar.media', '2015-02-06-042810_bar.media.gz',
            '2015-02-06-042810_bar.media.gpg', '2015-02-06-042810_bar.media.gz.gpg',
        ]]

    def test_list(self):
        execute_from_command_line(['', 'listbackups'])

    def test_filter_encrypted(self):
        stdout = StringIO()
        with patch('sys.stdout', stdout):
            execute_from_command_line(['', 'listbackups', '--encrypted', '-q'])
        stdout.seek(0)
        stdout.readline()
        for line in stdout.readlines():
            self.assertIn('.gpg', line)

    def test_filter_not_encrypted(self):
        stdout = StringIO()
        with patch('sys.stdout', stdout):
            execute_from_command_line(['', 'listbackups', '--not-encrypted', '-q'])
        stdout.seek(0)
        stdout.readline()
        for line in stdout.readlines():
            self.assertNotIn('.gpg', line)

    def test_filter_compressed(self):
        stdout = StringIO()
        with patch('sys.stdout', stdout):
            execute_from_command_line(['', 'listbackups', '--compressed', '-q'])
        stdout.seek(0)
        stdout.readline()
        for line in stdout.readlines():
            self.assertIn('.gz', line)

    def test_filter_not_compressed(self):
        stdout = StringIO()
        with patch('sys.stdout', stdout):
            execute_from_command_line(['', 'listbackups', '--not-compressed', '-q'])
        stdout.seek(0)
        stdout.readline()
        for line in stdout.readlines():
            self.assertNotIn('.gz', line)

    def test_filter_db(self):
        stdout = StringIO()
        with patch('sys.stdout', stdout):
            execute_from_command_line(['', 'listbackups', '--content-type', 'db', '-q'])
        stdout.seek(0)
        stdout.readline()
        for line in stdout.readlines():
            self.assertIn('.db', line)

    def test_filter_media(self):
        stdout = StringIO()
        with patch('sys.stdout', stdout):
            execute_from_command_line(['', 'listbackups', '--content-type', 'media', '-q'])
        stdout.seek(0)
        stdout.readline()
        for line in stdout.readlines():
            self.assertIn('.media', line)
