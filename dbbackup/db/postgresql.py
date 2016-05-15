from .base import BaseCommandDBConnector


class PgDumpConnector(BaseCommandDBConnector):
    """
    PostgreSQL connector, creates dump with ``pg_dump`` and restore with
    ``pg_restore``.
    """
    dump_cmd = 'pg_dump'
    restore_cmd = 'pg_restore'
    single_transaction = True

    def create_dump(self):
        cmd = '{} {}'.format(self.dump_cmd, self.settings['NAME'])
        if 'HOST' in self.settings:
            cmd += ' --host={}'.format(self.settings['HOST'])
        if 'PORT' in self.settings:
            cmd += ' --port={}'.format(self.settings['PORT'])
        if 'USER' in self.settings:
            cmd += ' --user={}'.format(self.settings['USER'])
        if 'PASSWORD' in self.settings:
            cmd += ' --password={}'.format(self.settings['PASSWORD'])
        for table in self.exclude:
            cmd += ' --exclude-table={}'.format(table)
        cmd = '{} {} {}'.format(self.dump_prefix, cmd, self.dump_suffix)
        return self.run_command(cmd)

    def restore_dump(self, dump):
        cmd = '{} -d {}'.format(self.restore_cmd, self.settings['NAME'])
        if 'HOST' in self.settings:
            cmd += ' --host={}'.format(self.settings['HOST'])
        if 'PORT' in self.settings:
            cmd += ' --port={}'.format(self.settings['PORT'])
        if 'USER' in self.settings:
            cmd += ' --user={}'.format(self.settings['USER'])
        if 'PASSWORD' in self.settings:
            cmd += ' --password={}'.format(self.settings['PASSWORD'])
        if self.single_transaction:
            cmd += ' --single-transaction'
        cmd = '{} {} {}'.format(self.restore_prefix, cmd, self.restore_suffix)
        return self.run_command(cmd, stdin=dump)


class PgDumpGisConnector(BaseCommandDBConnector):
    """
    PostgreGIS connector, same than :class:`PgDumpGisConnector` but enable
    postgis if not made.
    """
    psql_cmd = 'psql'

    def _enable_postgis(self):
        cmd = '{} -c "CREATE EXTENSION IF NOT EXISTS postgis;"'.format(
            self.psql_cmd)
        cmd += ' --user={}'.format(self.settings['ADMIN_USER'])
        if self.settings.get('ADMIN_PASSWORD'):
            cmd += ' --password={}'.format(self.settings['ADMIN_PASSWORD'])
        if 'HOST' in self.settings:
            cmd += ' --host={}'.format(self.settings['HOST'])
        if 'PORT' in self.settings:
            cmd += ' --port={}'.format(self.settings['PORT'])
        return self.run_command(cmd)

    def restore_dump(self, dump):
        if self.settings.get('USE_POSTGIS') and self.settings.get('ADMINUSER'):
            self._enable_postgis()
        return super(PgDumpConnector, self).restore_dump(dump)
