import logging
import django
from django.utils.log import AdminEmailHandler

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'dbbackup.console': {
            'formatter': 'base',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'dbbackup.mail_admins': {
            'level': 'ERROR',
            'class': 'dbbackup.log.DbbackupAdminEmailHandler',
            'filters': ['require_dbbackup_mail_enabled'],
            'include_html': True,
        }
    },
    'filters': {
        'require_dbbackup_mail_enabled': {
            '()': 'dbbackup.log.MailEnabledFilter'
        }
    },
    'formatters': {
        'base': {'format': '%(message)s'},
        'simple': {'format': '%(levelname)s %(message)s'}
    },
    'loggers': {
        'dbbackup': {
            'handlers': [
                'dbbackup.mail_admins',
                'dbbackup.console'
            ],
            'level': 'INFO'
        },
    }
}


class DbbackupAdminEmailHandler(AdminEmailHandler):
    def emit(self, record):
        # Monkey patch for old Django versions without send_mail method
        if django.VERSION < (1, 8):
            from . import utils
            django.core.mail.mail_admins = utils.mail_admins
        super(DbbackupAdminEmailHandler, self).emit(record)

    def send_mail(self, subject, message, *args, **kwargs):
        from . import utils
        utils.mail_admins(subject, message, *args, connection=self.connection(), **kwargs)


class MailEnabledFilter(logging.Filter):
    def filter(self, record):
        from .settings import SEND_EMAIL
        return SEND_EMAIL
