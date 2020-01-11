from __future__ import unicode_literals

from mock import patch, mock_open

from django.test import TestCase
from six import BytesIO

from dbbackup.db.postgresql import (PgDumpConnector, PgDumpGisConnector,
                                    PgDumpBinaryConnector)


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
        self.assertNotIn(' --username=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['USER'] = 'foo'
        connector.create_dump()
        self.assertIn(' --username=foo', mock_dump_cmd.call_args[0][0])

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
        self.assertNotIn(' --username=', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['USER'] = 'foo'
        connector.restore_dump(dump)
        self.assertIn(' --username=foo', mock_restore_cmd.call_args[0][0])


@patch('dbbackup.db.postgresql.PgDumpBinaryConnector.run_command',
       return_value=(BytesIO(b'foo'), BytesIO()))
class PgDumpBinaryConnectorTest(TestCase):
    def test_create_dump(self, mock_dump_cmd):
        connector = PgDumpBinaryConnector()
        dump = connector.create_dump()
        # Test dump
        dump_content = dump.read()
        self.assertTrue(dump_content)
        self.assertEqual(dump_content, b'foo')
        # Test cmd
        self.assertTrue(mock_dump_cmd.called)

    def test_create_dump_host(self, mock_dump_cmd):
        connector = PgDumpBinaryConnector()
        # Without
        connector.settings.pop('HOST', None)
        connector.create_dump()
        self.assertNotIn(' --host=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['HOST'] = 'foo'
        connector.create_dump()
        self.assertIn(' --host=foo', mock_dump_cmd.call_args[0][0])

    def test_create_dump_port(self, mock_dump_cmd):
        connector = PgDumpBinaryConnector()
        # Without
        connector.settings.pop('PORT', None)
        connector.create_dump()
        self.assertNotIn(' --port=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['PORT'] = 42
        connector.create_dump()
        self.assertIn(' --port=42', mock_dump_cmd.call_args[0][0])

    def test_create_dump_user(self, mock_dump_cmd):
        connector = PgDumpBinaryConnector()
        # Without
        connector.settings.pop('USER', None)
        connector.create_dump()
        self.assertNotIn(' --user=', mock_dump_cmd.call_args[0][0])
        # With
        connector.settings['USER'] = 'foo'
        connector.create_dump()
        self.assertIn(' --user=foo', mock_dump_cmd.call_args[0][0])

    def test_create_dump_exclude(self, mock_dump_cmd):
        connector = PgDumpBinaryConnector()
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
        connector = PgDumpBinaryConnector()
        # Without
        connector.drop = False
        connector.create_dump()
        self.assertNotIn(' --clean', mock_dump_cmd.call_args[0][0])
        # Binary drop at restore level
        connector.drop = True
        connector.create_dump()
        self.assertNotIn(' --clean', mock_dump_cmd.call_args[0][0])

    @patch('dbbackup.db.postgresql.PgDumpBinaryConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpBinaryConnector()
        dump = connector.create_dump()
        connector.restore_dump(dump)
        # Test cmd
        self.assertTrue(mock_restore_cmd.called)

    @patch('dbbackup.db.postgresql.PgDumpBinaryConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_host(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpBinaryConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('HOST', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --host=foo', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['HOST'] = 'foo'
        connector.restore_dump(dump)
        self.assertIn(' --host=foo', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.postgresql.PgDumpBinaryConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_port(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpBinaryConnector()
        dump = connector.create_dump()
        # Without
        connector.settings.pop('PORT', None)
        connector.restore_dump(dump)
        self.assertNotIn(' --port=', mock_restore_cmd.call_args[0][0])
        # With
        connector.settings['PORT'] = 42
        connector.restore_dump(dump)
        self.assertIn(' --port=42', mock_restore_cmd.call_args[0][0])

    @patch('dbbackup.db.postgresql.PgDumpBinaryConnector.run_command',
           return_value=(BytesIO(), BytesIO()))
    def test_restore_dump_user(self, mock_dump_cmd, mock_restore_cmd):
        connector = PgDumpBinaryConnector()
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
        self.assertIn('--username=foo', mock_dump_cmd.call_args[0][0])

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
