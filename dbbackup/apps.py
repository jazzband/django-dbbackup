"""Apps for DBBackup"""

from django.apps import AppConfig
try:
    from django.utils.translation import gettext_lazy as _ # noqa: F401
except: # noqa: E722
    from django.utils.translation import ugettext_lazy as _ # noqa: F401

from dbbackup import log


class DbbackupConfig(AppConfig):
    """
    Config for DBBackup application.
    """
    name = 'dbbackup'
    label = 'dbbackup'
    verbose_name = _('Backup and restore')

    def ready(self):
        log.load()
