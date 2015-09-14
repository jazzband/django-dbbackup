from logging import getLogger
from optparse import make_option
from django.core.management.base import BaseCommand, LabelCommand


class BaseDbBackupCommand(LabelCommand):
    """
    Base command class used for create all dbbackup command.
    """
    option_list = BaseCommand.option_list + (
        make_option("--noinput", action='store_false', dest='interactive', default=True,
                    help='Tells Django to NOT prompt the user for input of any kind.'),
        make_option('-q', "--quiet", action='store_true', default=False,
                    help='Tells Django to NOT output other text than errors.')
    )

    verbosity = 1
    quiet = False
    logger = getLogger('dbbackup.command')

    def _set_logger_level(self):
        level = 60 if self.quiet else (self.verbosity + 1) * 10
        self.logger.setLevel(level)
