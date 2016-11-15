import logging
from mock import patch
import django
from django.test import TestCase
from django.core import mail
from dbbackup import log
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


class DBbackupAdminEmailHandlerTest(TestCase):
    logger = logging.getLogger('dbbackup')

    def get_admin_email_handler(self, logger):
        admin_email_handler = [
            h for h in logger.handlers
            if h.__class__.__name__ == "DbbackupAdminEmailHandler"
        ][0]
        return admin_email_handler

    def test_send_mail(self):
        msg = "Super msg"
        admin_email_handler = self.get_admin_email_handler(self.logger)
        orig_filters = admin_email_handler.filters  # Backup filters
        try:
            admin_email_handler.filters = []
            # Test mail error
            self.logger.error(msg)
            self.assertEqual(mail.outbox[0].subject, '[dbbackup] ERROR: Super msg')
            # Test don't mail below
            self.logger.warning(msg)
            self.assertEqual(len(mail.outbox), 1)
        finally:
            admin_email_handler.filters = orig_filters

    @patch('dbbackup.settings.SEND_EMAIL', False)
    def test_send_mail_is_false(self):
        msg = "Super msg"
        self.logger.error(msg)
        self.assertEqual(len(mail.outbox), 0)


class MailEnabledFilterTest(TestCase):
    @patch('dbbackup.settings.SEND_EMAIL', True)
    def test_filter_is_true(self):
        filter_ = log.MailEnabledFilter()
        self.assertTrue(filter_.filter('foo'))

    @patch('dbbackup.settings.SEND_EMAIL', False)
    def test_filter_is_false(self):
        filter_ = log.MailEnabledFilter()
        self.assertFalse(filter_.filter('foo'))
