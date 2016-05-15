from mock import patch, mock_open

from django.test import TestCase
from django.utils.six import BytesIO

from dbbackup.db.base import get_connector, BaseDBConnector, BaseCommandDBConnector
from dbbackup.db.sqlite import SqliteConnector, SqliteCPConnector


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
        stdout = connector.run_command('echo 123')
        self.assertEqual(stdout.read(), b'123\n')


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
