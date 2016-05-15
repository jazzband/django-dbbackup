from .base import BaseCommandDBConnector


class MysqlDumpConnector(BaseCommandDBConnector):
    """
    MySQL connector, creates dump with ``mysqldump`` and restore with
    ``mysql``.
    """
    dump_cmd = 'mysqldump'
    restore_cmd = 'mysql'

    def create_dump(self):
        cmd = '{} {} --quick'.format(self.dump_cmd, self.settings['NAME'])
        if 'HOST' in self.settings:
            cmd += ' --host={}'.format(self.settings['HOST'])
        if 'PORT' in self.settings:
            cmd += ' --port={}'.format(self.settings['PORT'])
        if 'USER' in self.settings:
            cmd += ' --user={}'.format(self.settings['USER'])
        if 'PASSWORD' in self.settings:
            cmd += ' --password={}'.format(self.settings['PASSWORD'])
        for table in self.exclude:
            cmd += ' --ignore-table={}.{}'.format(self.settings['NAME'], table)
        return self.run_command(cmd)

    def restore_dump(self, dump):
        cmd = '{} {}'.format(self.restore_cmd, self.settings['NAME'])
        if 'HOST' in self.settings:
            cmd += ' --host={}'.format(self.settings['HOST'])
        if 'PORT' in self.settings:
            cmd += ' --port={}'.format(self.settings['PORT'])
        if 'USER' in self.settings:
            cmd += ' --user={}'.format(self.settings['USER'])
        if 'PASSWORD' in self.settings:
            cmd += ' --password={}'.format(self.settings['PASSWORD'])
        return self.run_command(cmd, stdin=dump)
