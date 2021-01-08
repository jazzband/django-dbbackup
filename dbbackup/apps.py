"""Apps for DBBackup"""

from django.apps import AppConfig
try:
    from django.utils.translation import gettext_lazy as _
except:
    from django.utils.translation import ugettext_lazy as _

from dbbackup import log


class DbbackupConfig(AppConfig):
    """
    Config for DBBackup application.
    """
    name = 'dbbackup'
    label = 'dbbackup'
    verbose_name = gettext_lazy('Backup and restore')

    def ready(self):
        log.load()
