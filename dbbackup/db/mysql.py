from .base import BaseCommandDBConnector


class MysqlDumpConnector(BaseCommandDBConnector):
    """
    MySQL connector, creates dump with ``mysqldump`` and restore with
    ``mysql``.
    """
    dump_cmd = 'mysqldump'
    restore_cmd = 'mysql'

    def create_dump(self):
        cmd = '%s %s --quick' % (self.dump_cmd, self.settings['NAME'])
        if 'HOST' in self.settings:
            cmd += ' --host=%s' % self.settings['HOST']
        if 'PORT' in self.settings:
            cmd += ' --port=%i' % self.settings['PORT']
        if 'USER' in self.settings:
            cmd += ' --user=%s' % self.settings['USER']
        if 'PASSWORD' in self.settings:
            cmd += ' --password=%s' % self.settings['PASSWORD']
        for table in self.exclude:
            cmd += ' --ignore-table=%s.%s' % (self.settings['NAME'], table)
        return self.run_command(cmd)

    def restore_dump(self, dump):
        cmd = '%s %s' % (self.restore_cmd, self.settings['NAME'])
        if 'HOST' in self.settings:
            cmd += ' --host=%s' % self.settings['HOST']
        if 'PORT' in self.settings:
            cmd += ' --port=%i' % self.settings['PORT']
        if 'USER' in self.settings:
            cmd += ' --user=%s' % self.settings['USER']
        if 'PASSWORD' in self.settings:
            cmd += ' --password=%s' % self.settings['PASSWORD']
        return self.run_command(cmd, stdin=dump)
