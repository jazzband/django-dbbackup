from django.test import TestCase
from dbbackup.management.commands._base import BaseDbBackupCommand


class BaseDbBackupCommandSetLoggerLevelTest(TestCase):
    def setUp(self):
        self.command = BaseDbBackupCommand()

    def test_debug_level(self):
        self.command.verbosity = 0
        self.command._set_logger_level()
        self.assertEqual(self.command.logger.level, 10)

    def test_info_level(self):
        self.command.verbosity = 1
        self.command._set_logger_level()
        self.assertEqual(self.command.logger.level, 20)

    def test_quiet(self):
        self.command.quiet = True
        self.command._set_logger_level()
        self.assertGreater(self.command.logger.level, 50)
