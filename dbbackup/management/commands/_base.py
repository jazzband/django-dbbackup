"""
Abstract Command.
"""
import sys
from logging import getLogger
from optparse import make_option
from shutil import copyfileobj

from django.core.management.base import BaseCommand, LabelCommand
from django.utils import six

input = raw_input if six.PY2 else input  # @ReservedAssignment


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

    def _ask_confirmation(self):
        answer = input("Are you sure you want to continue? [Y/n]")
        if answer.lower().startswith('n'):
            self.logger.info("Quitting")
            sys.exit(0)

    def read_local_file(self, path):
        """Open file in read mode on local filesystem."""
        return open(path, 'rb')

    # TODO: Define chunk size
    def write_local_file(self, outputfile, path):
        """Write file to the desired path."""
        outputfile.seek(0)
        with open(path, 'wb') as fd:
            copyfileobj(outputfile, fd)
