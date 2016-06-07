from .base import BaseCommandDBConnector


class PgDumpConnector(BaseCommandDBConnector):
    """
    PostgreSQL connector, it uses pg_dump`` to create an SQL text file
    and ``psql`` for restore it.
    """
    extension = 'psql'
    dump_cmd = 'pg_dump'
    restore_cmd = 'psql'
    single_transaction = True
    drop = True

    def _create_dump(self):
        cmd = '{} {}'.format(self.dump_cmd, self.settings['NAME'])
        if self.settings.get('HOST'):
            cmd += ' --host={}'.format(self.settings['HOST'])
        if self.settings.get('PORT'):
            cmd += ' --port={}'.format(self.settings['PORT'])
        if self.settings.get('USER'):
            cmd += ' --user={}'.format(self.settings['USER'])
        if self.settings.get('PASSWORD'):
            cmd += ' --password={}'.format(self.settings['PASSWORD'])
        else:
            cmd += ' --no-password'
        for table in self.exclude:
            cmd += ' --exclude-table={}'.format(table)
        if self.drop:
            cmd += ' --clean'
        cmd = '{} {} {}'.format(self.dump_prefix, cmd, self.dump_suffix)
        stdout, stderr = self.run_command(cmd, env=self.dump_env)
        return stdout

    def _restore_dump(self, dump):
        cmd = '{} {}'.format(self.restore_cmd, self.settings['NAME'])
        if self.settings.get('HOST'):
            cmd += ' --host={}'.format(self.settings['HOST'])
        if self.settings.get('PORT'):
            cmd += ' --port={}'.format(self.settings['PORT'])
        if self.settings.get('USER'):
            cmd += ' --user={}'.format(self.settings['USER'])
        if self.settings.get('PASSWORD'):
            cmd += ' --password={}'.format(self.settings['PASSWORD'])
        else:
            cmd += ' --no-password'
        if self.single_transaction:
            cmd += ' --single-transaction'
        cmd = '{} {} {}'.format(self.restore_prefix, cmd, self.restore_suffix)
        stdout, stderr = self.run_command(cmd, stdin=dump, env=self.restore_env)
        return stdout, stderr


class PgDumpGisConnector(PgDumpConnector):
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
        else:
            cmd += ' --no-password'
        if self.settings.get('HOST'):
            cmd += ' --host={}'.format(self.settings['HOST'])
        if self.settings.get('PORT'):
            cmd += ' --port={}'.format(self.settings['PORT'])
        return self.run_command(cmd)

    def _restore_dump(self, dump):
        if self.settings.get('ADMINUSER'):
            self._enable_postgis()
        return super(PgDumpGisConnector, self)._restore_dump(dump)
