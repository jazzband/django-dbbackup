from tempfile import mkstemp
import logging
import os

from .base import BaseCommandDBConnector

logger = logging.getLogger('dbbackup.command')


class PgEnvWrapper:
    """
    Context manager that updates the OS environment with the libpq variables
    derived from settings, and if necessary a temporary .pgpass file.
    """
    def __init__(self, settings):
        self.settings = settings
        self.pgpass_path = None

    def __enter__(self):
        # Get all settings, with empty defaults to detect later
        pghost = self.settings.get('HOST', None)
        pgport = self.settings.get('PORT', None)
        pguser = self.settings.get('USER', None)
        pgdatabase = self.settings.get('NAME', None)
        pgpassword = self.settings.get('PASSWORD', None)

        # Set PG* environment variables for everything we got
        # All defaults are thus left to libpq
        env = os.environ.copy()
        if pghost:
            env['PGHOST'] = pghost
        if pgport:
            env['PGPORT'] = pgport
        if pguser:
            env['PGUSER'] = pguser
        if pgdatabase:
            env['PGDATABASE'] = pgdatabase

        if pgpassword:
            # Open a temporary file (safe name, mode 600) as .pgpass file
            fd, self.pgpass_path = mkstemp(text=True)
            os.close(fd)
            with open(self.pgpass_path, 'w') as pgpass_file:
                # Write a catch-all entry, as this .pgass is only used once and by us
                pgpass_file.write(f'*:*:*:*:{pgpassword}\n')
            env['PGPASSFILE'] = self.pgpass_path

        return env

    def __exit__(self, *args):
        if self.pgpass_path:
            os.unlink(self.pgpass_path)


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
        cmd = '{} '.format(self.dump_cmd)

        for table in self.exclude:
            cmd += ' --exclude-table-data={}'.format(table)
        if self.drop:
            cmd += ' --clean'

        cmd = '{} {} {}'.format(self.dump_prefix, cmd, self.dump_suffix)
        with PgEnvWrapper(self.settings) as env:
            stdout, stderr = self.run_command(cmd, env={**self.dump_env, **env})
        return stdout

    def _restore_dump(self, dump):
        cmd = '{} '.format(self.restore_cmd)

        # without this, psql terminates with an exit value of 0 regardless of errors
        cmd += ' --set ON_ERROR_STOP=on'
        if self.single_transaction:
            cmd += ' --single-transaction'
        cmd = '{} {} {}'.format(self.restore_prefix, cmd, self.restore_suffix)
        with PgEnvWrapper(self.settings) as env:
            stdout, stderr = self.run_command(cmd, stdin=dump, env={**self.restore_env, **env})
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
        cmd += ' --username={}'.format(self.settings['ADMIN_USER'])
        cmd += ' --no-password'
        with PgEnvWrapper(self.settings) as env:
            return self.run_command(cmd, env=env)

    def _restore_dump(self, dump):
        if self.settings.get('ADMIN_USER'):
            self._enable_postgis()
        return super(PgDumpGisConnector, self)._restore_dump(dump)


class PgDumpBinaryConnector(PgDumpConnector):
    """
    PostgreSQL connector, it uses pg_dump`` to create an SQL text file
    and ``pg_restore`` for restore it.
    """
    extension = 'psql.bin'
    dump_cmd = 'pg_dump'
    restore_cmd = 'pg_restore'
    single_transaction = True
    drop = True

    def _create_dump(self):
        cmd = '{} '.format(self.dump_cmd)

        cmd += ' --format=custom'
        for table in self.exclude:
            cmd += ' --exclude-table-data={}'.format(table)
        cmd = '{} {} {}'.format(self.dump_prefix, cmd, self.dump_suffix)
        with PgEnvWrapper(self.settings) as env:
            stdout, stderr = self.run_command(cmd, env={**self.dump_env, **env})
        return stdout

    def _restore_dump(self, dump):
        cmd = '{} '.format(self.restore_cmd)

        if self.single_transaction:
            cmd += ' --single-transaction'
        if self.drop:
            cmd += ' --clean'
        cmd += '-d {}'.format(self.settings.get('NAME'))
        cmd = '{} {} {}'.format(self.restore_prefix, cmd, self.restore_suffix)
        with PgEnvWrapper(self.settings) as env:
            stdout, stderr = self.run_command(cmd, stdin=dump, env={**self.restore_env, **env})
        return stdout, stderr
