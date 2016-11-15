import logging
import django
from django.test import TestCase
from testfixtures import log_capture


class LoggerDefaultTestCase(TestCase):
    @log_capture()
    def test_root(self, captures):
        logger = logging.getLogger()
        logger.debug('a noise')
        logger.info('a message')
        logger.warning('a warning')
        logger.error('an error')
        logger.critical('a critical error')
        captures.check(
            ('root', 'DEBUG', 'a noise'),
            ('root', 'INFO', 'a message'),
            ('root', 'WARNING', 'a warning'),
            ('root', 'ERROR', 'an error'),
            ('root', 'CRITICAL', 'a critical error'),
        )

    @log_capture()
    def test_django(self, captures):
        logger = logging.getLogger('django')
        logger.debug('a noise')
        logger.info('a message')
        logger.warning('a warning')
        logger.error('an error')
        logger.critical('a critical error')
        if django.VERSION < (1, 9):
            captures.check(
                ('django', 'DEBUG', 'a noise'),
                ('django', 'INFO', 'a message'),
                ('django', 'WARNING', 'a warning'),
                ('django', 'ERROR', 'an error'),
                ('django', 'CRITICAL', 'a critical error'),
            )
        else:
            captures.check(
                ('django', 'INFO', 'a message'),
                ('django', 'WARNING', 'a warning'),
                ('django', 'ERROR', 'an error'),
                ('django', 'CRITICAL', 'a critical error'),
            )

    @log_capture()
    def test_dbbackup_command(self, captures):
        logger = logging.getLogger('dbbackup.command')
        logger.debug('a noise')
        logger.info('a message')
        logger.warning('a warning')
        logger.error('an error')
        logger.critical('a critical error')
        captures.check(
            ('dbbackup.command', 'INFO', 'a message'),
            ('dbbackup.command', 'WARNING', 'a warning'),
            ('dbbackup.command', 'ERROR', 'an error'),
            ('dbbackup.command', 'CRITICAL', 'a critical error'),
        )

    @log_capture()
    def test_dbbackup_storage(self, captures):
        logger = logging.getLogger('dbbackup.storage')
        logger.debug('a noise')
        logger.info('a message')
        logger.warning('a warning')
        logger.error('an error')
        logger.critical('a critical error')
        captures.check(
            ('dbbackup.storage', 'INFO', 'a message'),
            ('dbbackup.storage', 'WARNING', 'a warning'),
            ('dbbackup.storage', 'ERROR', 'an error'),
            ('dbbackup.storage', 'CRITICAL', 'a critical error'),
        )

    @log_capture()
    def test_other_module(self, captures):
        logger = logging.getLogger('os.path')
        logger.debug('a noise')
        logger.info('a message')
        logger.warning('a warning')
        logger.error('an error')
        logger.critical('a critical error')
        captures.check(
            ('os.path', 'DEBUG', 'a noise'),
            ('os.path', 'INFO', 'a message'),
            ('os.path', 'WARNING', 'a warning'),
            ('os.path', 'ERROR', 'an error'),
            ('os.path', 'CRITICAL', 'a critical error'),
        )
