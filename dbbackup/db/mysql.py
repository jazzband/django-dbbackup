from .base import BaseCommandDBConnector


class MysqlDumpConnector(BaseCommandDBConnector):
    """
    MySQL connector, creates dump with ``mysqldump`` and restore with
    ``mysql``.
    """
    dump_cmd = 'mysqldump'
    restore_cmd = 'mysql'

    def create_dump(self):
        cmd = '%s %s' % (self.dump_cmd, self.settings['NAME'])
        cmd += ' --host=%s' % self.settings['HOST']
        cmd += ' --port=%i' % self.settings['PORT']
        cmd += ' --user=%s' % self.settings['USER']
        cmd += ' --password=%s' % self.settings['PASSWORD']
        for table in self.exclude:
            cmd += ' --ignore-table=%s.%s' % (self.settings['NAME'], table)
        return self.run_command(cmd)

    def restore_dump(self, dump):
        cmd = '%s %s' % (self.restore_cmd, self.settings['NAME'])
        cmd += ' --host=%s' % self.settings.get('HOST', 'localhost')
        cmd += ' --port=%i' % self.settings.get('PORT', 3306)
        cmd += ' --user=%s' % self.settings['USER']
        cmd += ' --password=%s' % self.settings.get('PASSWORD')
        return self.run_command(cmd, stdin=dump)
