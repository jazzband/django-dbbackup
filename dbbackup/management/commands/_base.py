"""
Abstract Command.
"""
import sys
from logging import getLogger
from optparse import make_option
from shutil import copyfileobj

from django.core.management.base import BaseCommand, LabelCommand, CommandError
from django.utils import six

from ...storage.base import StorageError

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
        answer = input("Are you sure you want to continue? [Y/n] ")
        if answer.lower().startswith('n'):
            self.logger.info("Quitting")
            sys.exit(0)

    def read_from_storage(self, path):
        return self.storage.read_file(path)

    def write_to_storage(self, file, path):
        self.logger.info("Writing file to %s: %s, filename: %s",
                         self.storage.name, self.storage.backup_dir,
                         path)
        self.storage.write_file(file, path)

    def read_local_file(self, path):
        """Open file in read mode on local filesystem."""
        return open(path, 'rb')

    def write_local_file(self, outputfile, path):
        """Write file to the desired path."""
        self.logger.info("Writing file to %s", path)
        outputfile.seek(0)
        with open(path, 'wb') as fd:
            copyfileobj(outputfile, fd)

    def _get_backup_file(self):
        if self.path:
            input_filename = self.path
            input_file = self.read_local_file(self.path)
        else:
            if self.filename:
                input_filename = self.filename
            # Fetch the latest backup if filepath not specified
            else:
                self.logger.info("Finding latest backup")
                # database = self.database['NAME'] if self.content_type == 'db' else None
                try:
                    input_filename = self.storage.get_latest_backup(
                        encrypted=self.decrypt,
                        compressed=self.uncompress,
                        content_type=self.content_type)
                        # TODO: Make better filter
                        # database=database)
                except StorageError as err:
                    raise CommandError(err.args[0])
            input_file = self.read_from_storage(input_filename)
        return input_filename, input_file

    def _cleanup_old_backups(self):
        """
        Cleanup old backups, keeping the number of backups specified by
        DBBACKUP_CLEANUP_KEEP and any backups that occur on first of the month.
        """
        # database = self.database if self.content_type == 'db' else None
        file_list = self.storage.clean_old_backups(encrypted=self.encrypt,
                                                   compressed=self.compress,
                                                   content_type=self.content_type)
                                                   # TODO: Make better filter
                                                   # database=database)
