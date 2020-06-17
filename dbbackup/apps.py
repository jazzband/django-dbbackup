"""Apps for DBBackup"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

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
