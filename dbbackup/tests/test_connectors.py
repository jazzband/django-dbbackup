import os
from mock import patch, mock_open
from tempfile import SpooledTemporaryFile

from django.test import TestCase
from django.utils.six import BytesIO

from dbbackup.db.base import get_connector, BaseDBConnector, BaseCommandDBConnector
from dbbackup.db import exceptions
from dbbackup.db.sqlite import SqliteConnector, SqliteCPConnector
from dbbackup.db.mysql import MysqlDumpConnector
from dbbackup.db.postgresql import PgDumpConnector, PgDumpGisConnector
from dbbackup.db.mongodb import MongoDumpConnector


class GetConnectorTest(TestCase):
    def test_get_connector(self):
        connector = get_connector()
        self.assertIsInstance(connector, BaseDBConnector)


class BaseDBConnectorTest(TestCase):
    def test_init(self):
        connector = BaseDBConnector()

    def test_settings(self):
        connector = BaseDBConnector()
        connector.settings

    def test_generate_filename(self):
        connector = BaseDBConnector()
        filename = connector.generate_filename()


class BaseCommandDBConnectorTest(TestCase):
    def test_run_command(self):
        connector = BaseCommandDBConnector()
        stdout, stderr = connector.run_command('echo 123')
        self.assertEqual(stdout.read(), b'123\n')
        self.assertEqual(stderr.read(), b'')

    def test_run_command_error(self):
        connector = BaseCommandDBConnector()
        with self.assertRaises(exceptions.CommandConnectorError):
            connector.run_command('echa 123')

    def test_run_command_stdin(self):
        connector = BaseCommandDBConnector()
        stdin = SpooledTemporaryFile()
        stdin.write(b'foo')
        stdin.seek(0)
        # Run
        stdout, stderr = connector.run_command('cat', stdin=stdin)
        self.assertEqual(stdout.read(), b'foo')
        self.assertFalse(stderr.read())

    def test_run_command_with_env(self):
        connector = BaseCommandDBConnector()
        # Empty env
        stdout, stderr = connector.run_command('env')
        self.assertTrue(stdout.read())
        # env from self.env
        connector.env = {'foo': 'bar'}
        stdout, stderr = connector.run_command('env')
        self.assertIn(b'foo=bar\n', stdout.read())
        # method overide gloabal env
        stdout, stderr = connector.run_command('env', env={'foo': 'ham'})
        self.assertIn(b'foo=ham\n', stdout.read())
        # get a var from parent env
        os.environ['bar'] = 'foo'
        stdout, stderr = connector.run_command('env')
        self.assertIn(b'bar=foo\n', stdout.read())
        # Conf overides parendt env
        connector.env = {'bar': 'bar'}
        stdout, stderr = connector.run_command('env')
        self.assertIn(b'bar=bar\n', stdout.read())
        # method overides all
        stdout, stderr = connector.run_command('env', env={'bar': 'ham'})
        self.assertIn(b'bar=ham\n', stdout.read())

    def test_run_command_with_parent_env(self):
        connector = BaseCommandDBConnector(use_parent_env=False)
        # Empty env
        stdout, stderr = connector.run_command('env')
        self.assertFalse(stdout.read())
        # env from self.env
        connector.env = {'foo': 'bar'}
        stdout, stderr = connector.run_command('env')
        self.assertEqual(stdout.read(), b'foo=bar\n')
        # method overide gloabal env
        stdout, stderr = connector.run_command('env', env={'foo': 'ham'})
        self.assertEqual(stdout.read(), b'foo=ham\n')
        # no var from parent env
        os.environ['bar'] = 'foo'
        stdout, stderr = connector.run_command('env')
        self.assertNotIn(b'bar=foo\n', stdout.read())


class SqliteConnectorTest(TestCase):
    def test_write_dump(self):

        dump_file = BytesIO()
        connector = SqliteConnector()
        connector._write_dump(dump_file)
        dump_file.seek(0)
        for line in dump_file:
            self.assertTrue(line.strip().endswith(b';'))

    def test_create_dump(self):
        connector = SqliteConnector()
        dump = connector.create_dump()
        self.assertTrue(dump.read())

    def test_restore_dump(self):
        connector = SqliteConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)


@patch('dbbackup.db.sqlite.open', mock_open(read_data=b'foo'), create=True)
class SqliteCPConnectorTest(TestCase):
    def test_create_dump(self):
        connector = SqliteCPConnector()
        dump = connector.create_dump()
        dump_content = dump.read()
        self.assertTrue(dump_content)
        self.assertEqual(dump_content, b'foo')

    def test_restore_dump(self):
        connector = SqliteCPConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)


@patch('dbbackup.db.mysql.MysqlDumpConnector.run_command',
       return_value=(BytesIO(b'foo'), BytesIO()))
class MysqlDumpConnectorTest(TestCase):
    def test_create_dump(self, mock_dump_cmd):
        connector = MysqlDumpConnector()
        dump = connector.create_dump()
        # Test dump
        dump_content = dump.read()
        self.assertTrue(dump_content)
        self.assertEqual(dump_content, b'foo')
        # Test cmd
        self.assertTrue(mock_dump_cmd.called)

    def test_create_dump_host(self, mock_dump_cmd):
        connector = MysqlDumpConnector()
        # Without
        connector.settings.pop('HOST', None)
        connector.create_dump()
        self.assertNotIn(' --host=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['HOST'] = 'foo'
        connector.create_dump()
        self.assertIn(' --host=foo', mock_dump_cmd.call_args[0][0])

    def test_create_dump_port(self, mock_dump_cmd):
        connector = MysqlDumpConnector()
        # Without
        connector.settings.pop('PORT', None)
        connector.create_dump()
        self.assertNotIn(' --port=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['PORT'] = 42
        connector.create_dump()
        self.assertIn(' --port=42', mock_dump_cmd.call_args[0][0])

    def test_create_dump_user(self, mock_dump_cmd):
        connector = MysqlDumpConnector()
        # Without
        connector.settings.pop('USER', None)
        connector.create_dump()
        self.assertNotIn(' --user=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['USER'] = 'foo'
        connector.create_dump()
        self.assertIn(' --user=foo', mock_dump_cmd.call_args[0][0])

    def test_create_dump_password(self, mock_dump_cmd):
        connector = MysqlDumpConnector()
        # Without
        connector.settings.pop('PASSWORD', None)
        connector.create_dump()
        self.assertNotIn(' --password=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['PASSWORD'] = 'foo'
        connector.create_dump()
        self.assertIn(' --password=foo', mock_dump_cmd.call_args[0][0])

    def test_create_dump_exclude(self, mock_dump_cmd):
        connector = MysqlDumpConnector()
        connector.settings['NAME'] = 'db'
        # Without
        connector.create_dump()
        self.assertNotIn(' --ignore-table=', mock_dump_cmd.call_args[0][0])
        # With
        connector.exclude = ('foo',)
        connector.create_dump()
        self.assertIn(' --ignore-table=db.foo', mock_dump_cmd.call_args[0][0])
        # With serveral
        connector.exclude = ('foo', 'bar')
        connector.create_dump()
        self.assertIn(' --ignore-table=db.foo', mock_dump_cmd.call_args[0][0])
        self.assertIn(' --ignore-table=db.bar', mock_dump_cmd.call_args[0][0])

    @patch('dbbackup.db.mysql.MysqlDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump(self, mock_dump_cmd, mock_restore_cmd):
        connector = MysqlDumpConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)
        # Test cmd
        self.assertTrue(mock_restore_cmd.called)

    @patch('dbbackup.db.mysql.MysqlDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_host(self, mock_dump_cmd, mock_restore_cmd):
        connector = MysqlDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('HOST', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --host=foo', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['HOST'] = 'foo'
        connector.restore_dump(dump)
        self.assertIn(' --host=foo', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.mysql.MysqlDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_port(self, mock_dump_cmd, mock_restore_cmd):
        connector = MysqlDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('PORT', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --port=', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['PORT'] = 42
        connector.restore_dump(dump)
        self.assertIn(' --port=42', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.mysql.MysqlDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_user(self, mock_dump_cmd, mock_restore_cmd):
        connector = MysqlDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('USER', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --user=', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['USER'] = 'foo'
        connector.restore_dump(dump)
        self.assertIn(' --user=foo', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.mysql.MysqlDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_password(self, mock_dump_cmd, mock_restore_cmd):
        connector = MysqlDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('PASSWORD', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --password=', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['PASSWORD'] = 'foo'
        connector.restore_dump(dump)
        self.assertIn(' --password=foo', mock_restore_cmd.call_args[0][0])


@patch('dbbackup.db.postgresql.PgDumpConnector.run_command',
       return_value=(BytesIO(b'foo'), BytesIO()))
class PgDumpConnectorTest(TestCase):
    def test_create_dump(self, mock_dump_cmd):
        connector = PgDumpConnector()
        dump = connector.create_dump()
        # Test dump
        dump_content = dump.read()
        self.assertTrue(dump_content)
        self.assertEqual(dump_content, b'foo')
        # Test cmd
        self.assertTrue(mock_dump_cmd.called)

    def test_create_dump_host(self, mock_dump_cmd):
        connector = PgDumpConnector()
        # Without
        connector.settings.pop('HOST', None)
        connector.create_dump()
        self.assertNotIn(' --host=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['HOST'] = 'foo'
        connector.create_dump()
        self.assertIn(' --host=foo', mock_dump_cmd.call_args[0][0])

    def test_create_dump_port(self, mock_dump_cmd):
        connector = PgDumpConnector()
        # Without
        connector.settings.pop('PORT', None)
        connector.create_dump()
        self.assertNotIn(' --port=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['PORT'] = 42
        connector.create_dump()
        self.assertIn(' --port=42', mock_dump_cmd.call_args[0][0])

    def test_create_dump_user(self, mock_dump_cmd):
        connector = PgDumpConnector()
        # Without
        connector.settings.pop('USER', None)
        connector.create_dump()
        self.assertNotIn(' --user=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['USER'] = 'foo'
        connector.create_dump()
        self.assertIn(' --user=foo', mock_dump_cmd.call_args[0][0])

    def test_create_dump_exclude(self, mock_dump_cmd):
        connector = PgDumpConnector()
        # Without
        connector.create_dump()
        self.assertNotIn(' --exclude-table=', mock_dump_cmd.call_args[0][0])
        # With
        connector.exclude = ('foo',)
        connector.create_dump()
        self.assertIn(' --exclude-table=foo', mock_dump_cmd.call_args[0][0])
        # With serveral
        connector.exclude = ('foo', 'bar')
        connector.create_dump()
        self.assertIn(' --exclude-table=foo', mock_dump_cmd.call_args[0][0])
        self.assertIn(' --exclude-table=bar', mock_dump_cmd.call_args[0][0])

    def test_create_dump_drop(self, mock_dump_cmd):
        connector = PgDumpConnector()
        # Without
        connector.drop = False
        connector.create_dump()
        self.assertNotIn(' --clean', mock_dump_cmd.call_args[0][0])
        # With
        connector.drop = True
        connector.create_dump()
        self.assertIn(' --clean', mock_dump_cmd.call_args[0][0])

    @patch('dbbackup.db.postgresql.PgDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)
        # Test cmd
        self.assertTrue(mock_restore_cmd.called)

    @patch('dbbackup.db.postgresql.PgDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_host(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('HOST', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --host=foo', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['HOST'] = 'foo'
        connector.restore_dump(dump)
        self.assertIn(' --host=foo', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.postgresql.PgDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_port(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('PORT', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --port=', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['PORT'] = 42
        connector.restore_dump(dump)
        self.assertIn(' --port=42', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.postgresql.PgDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_user(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('USER', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --user=', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['USER'] = 'foo'
        connector.restore_dump(dump)
        self.assertIn(' --user=foo', mock_restore_cmd.call_args[0][0])


@patch('dbbackup.db.postgresql.PgDumpGisConnector.run_command',
       return_value=(BytesIO(b'foo'), BytesIO()))
class PgDumpGisConnectorTest(TestCase):
    @patch('dbbackup.db.postgresql.PgDumpGisConnector.run_command',
           return_value=(BytesIO(b'foo'), BytesIO()))
    def test_restore_dump(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpGisConnector()
        dump = connector.create_dump()
        # Without ADMINUSER
        connector.settings.pop('ADMIN_USER', None)
        connector.restore_dump(dump)
        self.assertTrue(mock_restore_cmd.called)
        # With
        connector.settings['ADMIN_USER'] = 'foo'
        connector.restore_dump(dump)
        self.assertTrue(mock_restore_cmd.called)

    def test_enable_postgis(self, mock_dump_cmd):
        connector = PgDumpGisConnector()
        connector.settings['ADMIN_USER'] = 'foo'
        connector._enable_postgis()
        self.assertIn('"CREATE EXTENSION IF NOT EXISTS postgis;"', mock_dump_cmd.call_args[0][0])
        self.assertIn('--user=foo', mock_dump_cmd.call_args[0][0])

    def test_enable_postgis_host(self, mock_dump_cmd):
        connector = PgDumpGisConnector()
        connector.settings['ADMIN_USER'] = 'foo'
        # Without
        connector.settings.pop('HOST', None)
        connector._enable_postgis()
        self.assertNotIn(' --host=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['HOST'] = 'foo'
        connector._enable_postgis()
        self.assertIn(' --host=foo', mock_dump_cmd.call_args[0][0])

    def test_enable_postgis_port(self, mock_dump_cmd):
        connector = PgDumpGisConnector()
        connector.settings['ADMIN_USER'] = 'foo'
        # Without
        connector.settings.pop('PORT', None)
        connector._enable_postgis()
        self.assertNotIn(' --port=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['PORT'] = 42
        connector._enable_postgis()
        self.assertIn(' --port=42', mock_dump_cmd.call_args[0][0])


@patch('dbbackup.db.base.Popen', **{
    'return_value.wait.return_value': True,
    'return_value.poll.return_value': False,
})
class PgDumpConnectorRunCommandTest(TestCase):
    def test_run_command(self, mock_popen):
        connector = PgDumpConnector()
        connector.create_dump()
        self.assertEqual(mock_popen.call_args[0][0][0], 'pg_dump')

    def test_run_command_with_password(self, mock_popen):
        connector = PgDumpConnector()
        connector.settings['PASSWORD'] = 'foo'
        connector.create_dump()
        self.assertEqual(mock_popen.call_args[0][0][0], 'pg_dump')
        self.assertIn('PGPASSWORD', mock_popen.call_args[1]['env'])
        self.assertEqual('foo', mock_popen.call_args[1]['env']['PGPASSWORD'])

    def test_run_command_with_password_and_other(self, mock_popen):
        connector = PgDumpConnector(env={'foo': 'bar'})
        connector.settings['PASSWORD'] = 'foo'
        connector.create_dump()
        self.assertEqual(mock_popen.call_args[0][0][0], 'pg_dump')
        self.assertIn('foo', mock_popen.call_args[1]['env'])
        self.assertEqual('bar', mock_popen.call_args[1]['env']['foo'])
        self.assertIn('PGPASSWORD', mock_popen.call_args[1]['env'])
        self.assertEqual('foo', mock_popen.call_args[1]['env']['PGPASSWORD'])


@patch('dbbackup.db.mongodb.MongoDumpConnector.run_command',
       return_value=(BytesIO(b'foo'), BytesIO()))
class MongoDumpConnectorTest(TestCase):
    def test_create_dump(self, mock_dump_cmd):
        connector = MongoDumpConnector()
        dump = connector.create_dump()
        # Test dump
        dump_content = dump.read()
        self.assertTrue(dump_content)
        self.assertEqual(dump_content, b'foo')
        # Test cmd
        self.assertTrue(mock_dump_cmd.called)

    def test_create_dump_user(self, mock_dump_cmd):
        connector = MongoDumpConnector()
        # Without
        connector.settings.pop('USER', None)
        connector.create_dump()
        self.assertNotIn(' --user ', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['USER'] = 'foo'
        connector.create_dump()
        self.assertIn(' --username foo', mock_dump_cmd.call_args[0][0])

    def test_create_dump_password(self, mock_dump_cmd):
        connector = MongoDumpConnector()
        # Without
        connector.settings.pop('PASSWORD', None)
        connector.create_dump()
        self.assertNotIn(' --password ', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['PASSWORD'] = 'foo'
        connector.create_dump()
        self.assertIn(' --password foo', mock_dump_cmd.call_args[0][0])

    @patch('dbbackup.db.mongodb.MongoDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump(self, mock_dump_cmd, mock_restore_cmd):
        connector = MongoDumpConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)
        # Test cmd
        self.assertTrue(mock_restore_cmd.called)

    @patch('dbbackup.db.mongodb.MongoDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_user(self, mock_dump_cmd, mock_restore_cmd):
        connector = MongoDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('USER', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --username ', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['USER'] = 'foo'
        connector.restore_dump(dump)
        self.assertIn(' --username foo', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.mongodb.MongoDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_password(self, mock_dump_cmd, mock_restore_cmd):
        connector = MongoDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('PASSWORD', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --password ', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['PASSWORD'] = 'foo'
        connector.restore_dump(dump)
        self.assertIn(' --password foo', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.mongodb.MongoDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_object_check(self, mock_dump_cmd, mock_restore_cmd):
        connector = MongoDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.object_check = False
        connector.restore_dump(dump)
        self.assertNotIn('--objcheck', mock_restore_cmd.call_args[0][0])
        # With
        connector.object_check = True
        connector.restore_dump(dump)
        self.assertIn(' --objcheck', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.mongodb.MongoDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_drop(self, mock_dump_cmd, mock_restore_cmd):
        connector = MongoDumpConnector()
        dump = connector.create_dump()
        # Without
        connector.drop = False
        connector.restore_dump(dump)
        self.assertNotIn('--drop', mock_restore_cmd.call_args[0][0])
        # With
        connector.drop = True
        connector.restore_dump(dump)
        self.assertIn(' --drop', mock_restore_cmd.call_args[0][0])
