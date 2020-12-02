"""Apps for DBBackup"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy

from dbbackup import log


class DbbackupConfig(AppConfig):
    """
    Config for DBBackup application.
    """
    name = 'dbbackup'
    label = 'dbbackup'
    verbose_name = gettext_lazy('Backup and restore')

    def ready(self):
        from .checks import check_settings  # noqa: F401
        log.load()
