from .base import BaseCommandDBConnetor


class MysqlDumpConnetor(BaseCommandDBConnetor):
    """
    MySQL connector, creates dump with ``mysqldump`` and restore with
    ``mysql``.
    """
    def create_dump(self, exclude=None):
        cmd = 'mysqldump %s' % self.settings['NAME']
        cmd += ' --host=%s' % self.settings['HOST']
        cmd += ' --port=%i' % self.settings['PORT']
        cmd += ' --user=%s' % self.settings['USER']
        cmd += ' --password=%s' % self.settings['PASSWORD']
        for table in exclude or []:
            cmd += ' --ignore-table=%s.%s' % (self.settings['NAME'], table)
        return self.run_command(cmd)

    def restore_dump(self, dump):
        cmd = 'mysql %s' % self.settings['NAME']
        cmd += ' --host=%s' % self.settings.get('HOST', 'localhost')
        cmd += ' --port=%i' % self.settings.get('PORT', 3306)
        cmd += ' --user=%s' % self.settings['USER']
        cmd += ' --password=%s' % self.settings.get('PASSWORD')
        return self.run_command(cmd, stdin=dump)
