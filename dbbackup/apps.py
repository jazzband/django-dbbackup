"""Apps for DBBackup"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class DbbackupConfig(AppConfig):
    """
    Config for DBBackup application.
    """
    name = 'dbbackup'
    label = 'dbbackup'
    verbose_name = gettext_lazy('Backup and restore')

    def ready(self):
        from dbbackup import checks
