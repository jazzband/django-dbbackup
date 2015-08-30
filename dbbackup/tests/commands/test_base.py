from django.test import TestCase
from django.utils.six import StringIO
from dbbackup.management.commands._base import BaseDbBackupCommand


class BaseDbBackupCommandLogTest(TestCase):
    def setUp(self):
        self.command = BaseDbBackupCommand()
        self.command.stdout = StringIO()

    def test_less_level(self):
        self.command.verbosity = 1
        self.command.log("foo", 2)
        self.command.stdout.seek(0)
        self.assertFalse(self.command.stdout.read())

    def test_more_level(self):
        self.command.verbosity = 1
        self.command.log("foo", 0)
        self.command.stdout.seek(0)
        self.assertEqual('foo', self.command.stdout.read())

    def test_quiet(self):
        self.command.quiet = True
        self.command.verbosity = 1
        self.command.log("foo", 0)
        self.command.stdout.seek(0)
        self.assertFalse(self.command.stdout.read())
