from .base import BaseCommandDBConnector


class PgDumpConnector(BaseCommandDBConnector):
    """
    PostgreSQL connector, creates dump with ``pg_dump`` and restore with
    ``pg_restore``.
    """
    dump_cmd = 'pg_dump'
    restore_cmd = 'pg_restore'
    psql_cmd = 'psql'
    single_transaction = True

    def create_dump(self):
        cmd = '%s %s' % (self.dump_cmd, self.settings['NAME'])
        cmd += ' --host=%s' % self.settings['HOST']
        cmd += ' --port=%i' % self.settings['PORT']
        cmd += ' --user=%s' % self.settings['USER']
        cmd += ' --password=%s' % self.settings['PASSWORD']
        for table in self.exclude:
            cmd += ' --exclude-table=%s' % table
        return self.run_command(cmd)

    def restore_dump(self, dump):
        if self.settings.get('USE_POSTGIS') and self.settings.get('ADMINUSER'):
            self._enable_postgis()
        cmd = '%s -d %s' % (self.restore_cmd, self.settings['NAME'])
        cmd += ' --host=%s' % self.settings.get('HOST', 'localhost')
        cmd += ' --port=%i' % self.settings.get('PORT', 3306)
        cmd += ' --user=%s' % self.settings['USER']
        cmd += ' --password=%s' % self.settings.get('PASSWORD')
        if self.single_transaction:
            cmd += ' --single-transaction'
        return self.run_command(cmd, stdin=dump)

    def _enable_postgis(self):
        cmd = '%s -c "CREATE EXTENSION IF NOT EXISTS postgis;"' % \
            self.psql_cmd
        cmd += ' --user=%s' % self.settings['ADMIN_USER']
        cmd += ' --host=%s' % self.settings.get('HOST', 'localhost')
        cmd += ' --port=%i' % self.settings.get('PORT', 3306)
        if self.settings.get('ADMIN_PASSWORD'):
            cmd += ' --password=%s' % self.settings['ADMIN_PASSWORD']
        return self.run_command(cmd)
