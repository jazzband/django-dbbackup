from mock import patch, mock_open
from tempfile import SpooledTemporaryFile

from django.test import TestCase
from django.utils.six import BytesIO

from dbbackup.db.base import get_connector, BaseDBConnector, BaseCommandDBConnector
from dbbackup.db import exceptions
from dbbackup.db.sqlite import SqliteConnector, SqliteCPConnector
from dbbackup.db.mysql import MysqlDumpConnector
from dbbackup.db.postgresql import PgDumpConnector
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
        self.assertFalse(stdout.read())
        # env from self.env
        connector.env = {'foo': 'bar'}
        stdout, stderr = connector.run_command('env')
        self.assertEqual(stdout.read(), b'foo=bar\n')
        # method overide gloabal env
        stdout, stderr = connector.run_command('env', env={'foo': 'ham'})
        self.assertEqual(stdout.read(), b'foo=ham\n')


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


    @patch('dbbackup.db.mysql.MysqlDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump(self, mock_dump_cmd, mock_restore_cmd):
        connector = MysqlDumpConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)
        # Test cmd
        self.assertTrue(mock_restore_cmd.called)


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

    @patch('dbbackup.db.postgresql.PgDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)
        # Test cmd
        self.assertTrue(mock_restore_cmd.called)


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

    @patch('dbbackup.db.mongodb.MongoDumpConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump(self, mock_dump_cmd, mock_restore_cmd):
        connector = MongoDumpConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)
        # Test cmd
        self.assertTrue(mock_restore_cmd.called)
