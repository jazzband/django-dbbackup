from .base import BaseCommandDBConnetor


class PgDumpConnetor(BaseCommandDBConnetor):
    """
    PostgreSQL connector, creates dump with ``pg_dump`` and restore with
    ``pg_restore``.
    """
    def create_dump(self):
        cmd = 'pg_dump %s' % self.settings['NAME']
        cmd += ' --host=%s' % self.settings['HOST']
        cmd += ' --port=%i' % self.settings['PORT']
        cmd += ' --user=%s' % self.settings['USER']
        cmd += ' --password=%s' % self.settings['PASSWORD']
        return self.run_command(cmd)

    def restore_dump(self, dump):
        cmd = 'pg_restore -d %s' % self.settings['NAME']
        cmd += ' --host=%s' % self.settings.get('HOST', 'localhost')
        cmd += ' --port=%i' % self.settings.get('PORT', 3306)
        cmd += ' --user=%s' % self.settings['USER']
        cmd += ' --password=%s' % self.settings.get('PASSWORD')
        return self.run_command(cmd, stdin=dump)
