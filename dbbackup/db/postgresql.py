from urllib.parse import quote
import logging

from dbbackup import utils
from .base import BaseCommandDBConnector
from .exceptions import DumpError

logger = logging.getLogger('dbbackup.command')


def create_postgres_uri(self):
    host = self.settings.get('HOST')
    if not host:
        raise DumpError('A host name is required')

    dbname = self.settings.get('NAME') or ''
    user = quote(self.settings.get('USER') or '')
    password = self.settings.get('PASSWORD') or ''
    password = ':{}'.format(quote(password)) if password else ''
    if not user:
        password = ''
    else:
        host = '@' + host

    port = ':{}'.format(self.settings.get('PORT')) if self.settings.get('PORT') else ''
    dbname = f'--dbname=postgresql://{user}{password}{host}{port}/{dbname}'
    return dbname


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

    def run_command(self, *args, **kwargs):
        if self.settings.get('PASSWORD'):
            env = kwargs.get('env', {})
            env['PGPASSWORD'] = utils.get_escaped_command_arg(self.settings['PASSWORD'])
            kwargs['env'] = env
        return super(PgDumpConnector, self).run_command(*args, **kwargs)

    def _create_dump(self):
        cmd = '{} '.format(self.dump_cmd)
        cmd = cmd + create_postgres_uri(self)

        for table in self.exclude:
            cmd += ' --exclude-table-data={}'.format(table)
        if self.drop:
            cmd += ' --clean'

        cmd = '{} {} {}'.format(self.dump_prefix, cmd, self.dump_suffix)
        stdout, stderr = self.run_command(cmd, env=self.dump_env)
        return stdout

    def _restore_dump(self, dump):
        cmd = '{} '.format(self.restore_cmd)
        cmd = cmd + create_postgres_uri(self)

        # without this, psql terminates with an exit value of 0 regardless of errors
        cmd += ' --set ON_ERROR_STOP=on'
        if self.single_transaction:
            cmd += ' --single-transaction'
        cmd += ' {}'.format(self.settings['NAME'])
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
        cmd += ' --username={}'.format(self.settings['ADMIN_USER'])
        cmd += ' --no-password'
        if self.settings.get('HOST'):
            cmd += ' --host={}'.format(self.settings['HOST'])
        if self.settings.get('PORT'):
            cmd += ' --port={}'.format(self.settings['PORT'])
        return self.run_command(cmd)

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
        cmd = cmd + create_postgres_uri(self)

        cmd += ' --format=custom'
        for table in self.exclude:
            cmd += ' --exclude-table-data={}'.format(table)
        cmd = '{} {} {}'.format(self.dump_prefix, cmd, self.dump_suffix)
        stdout, stderr = self.run_command(cmd, env=self.dump_env)
        return stdout

    def _restore_dump(self, dump):
        dbname = create_postgres_uri(self)
        cmd = '{} {}'.format(self.restore_cmd, dbname)

        if self.single_transaction:
            cmd += ' --single-transaction'
        if self.drop:
            cmd += ' --clean'
        cmd = '{} {} {}'.format(self.restore_prefix, cmd, self.restore_suffix)
        stdout, stderr = self.run_command(cmd, stdin=dump, env=self.restore_env)
        return stdout, stderr
