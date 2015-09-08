"""
Save database.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from optparse import make_option
from ... import utils
from ._base import BaseDbBackupCommand
from ...storage.base import BaseStorage, StorageError

ROW_TEMPLATE = '{name:40} {datetime:20}'
FILTER_KEYS = ('encrypted', 'compressed', 'content_type', 'database')


class Command(BaseDbBackupCommand):
    option_list = BaseDbBackupCommand.option_list + (
        make_option("-d", "--database", help="Filter by database name"),
        make_option("-z", "--compressed", help="Exclude non-compressed", action="store_true", default=None, dest="compressed"),
        make_option("-Z", "--not-compressed", help="Exclude compressed", action="store_false", default=None, dest="compressed"),
        make_option("-e", "--encrypted", help="Exclude non-encrypted", action="store_true", default=None, dest="encrypted"),
        make_option("-E", "--not-encrypted", help="Exclude encrypted", action="store_false", default=None, dest="encrypted"),
        make_option("-c", "--content-type", help="Filter by content type 'db' or 'media'"),
    )

    def handle(self, **options):
        self.quiet = options.get('quiet')
        self.storage = BaseStorage.storage_factory()
        files_attr = self.get_backup_attrs(options)
        if not self.quiet:
            title = ROW_TEMPLATE.format(name='Name', datetime='Datetime')
            self.stdout.write(title)
        for file_attr in files_attr:
            row = ROW_TEMPLATE.format(**file_attr)
            self.stdout.write(row)

    def get_backup_attrs(self, options):
        filters = dict([(k, v) for k, v in options.items()
                        if k in FILTER_KEYS])
        filenames = self.storage.list_backups(**filters)
        files_attr = [
            {'datetime': utils.filename_to_date(filename).strftime('%x %X'),
             'name': filename}
            for filename in filenames]
        return files_attr
