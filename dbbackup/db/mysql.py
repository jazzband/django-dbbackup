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
        if self.settings.get('HOST'):
            cmd += ' --host={}'.format(self.settings['HOST'])
        if self.settings.get('PORT'):
            cmd += ' --port={}'.format(self.settings['PORT'])
        if self.settings.get('USER'):
            cmd += ' --user={}'.format(self.settings['USER'])
        if self.settings.get('PASSWORD'):
            cmd += ' --password={}'.format(self.settings['PASSWORD'])
        for table in self.exclude:
            cmd += ' --ignore-table={}.{}'.format(self.settings['NAME'], table)
        cmd = '{} {} {}'.format(self.dump_prefix, cmd, self.dump_suffix)
        return self.run_command(cmd)

    def restore_dump(self, dump):
        cmd = '{} {}'.format(self.restore_cmd, self.settings['NAME'])
        if self.settings.get('HOST'):
            cmd += ' --host={}'.format(self.settings['HOST'])
        if self.settings.get('PORT'):
            cmd += ' --port={}'.format(self.settings['PORT'])
        if self.settings.get('USER'):
            cmd += ' --user={}'.format(self.settings['USER'])
        if self.settings.get('PASSWORD'):
            cmd += ' --password={}'.format(self.settings['PASSWORD'])
        cmd = '{} {} {}'.format(self.restore_prefix, cmd, self.restore_suffix)
        return self.run_command(cmd, stdin=dump)
