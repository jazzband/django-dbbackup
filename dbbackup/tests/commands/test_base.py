"""
Tests for base command class.
"""
import os
from mock import patch
from django.test import TestCase
from django.utils import six
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

    def test_read_local_file(self):
        # setUp
        self.command.path = '/tmp/foo.bak'
        open(self.command.path, 'w').close()
        # Test
        output_file = self.command.read_local_file(self.command.path)
        # tearDown
        os.remove(self.command.path)

    def test_write_local_file(self):
        fd, path = six.BytesIO(b"foo"), '/tmp/foo.bak'
        self.command.write_local_file(fd, path)
        self.assertTrue(os.path.exists(path))
        # tearDown
        os.remove(path)

    def test_ask_confirmation(self):
        # Yes
        with patch('dbbackup.management.commands._base.input', return_value='y'):
            self.command._ask_confirmation()
        with patch('dbbackup.management.commands._base.input', return_value='Y'):
            self.command._ask_confirmation()
        with patch('dbbackup.management.commands._base.input', return_value=''):
            self.command._ask_confirmation()
        with patch('dbbackup.management.commands._base.input', return_value='foo'):
            self.command._ask_confirmation()
        # No
        with patch('dbbackup.management.commands._base.input', return_value='n'):
            with self.assertRaises(SystemExit):
                self.command._ask_confirmation()
        with patch('dbbackup.management.commands._base.input', return_value='N'):
            with self.assertRaises(SystemExit):
                self.command._ask_confirmation()
        with patch('dbbackup.management.commands._base.input', return_value='No'):
            with self.assertRaises(SystemExit):
                self.command._ask_confirmation()
