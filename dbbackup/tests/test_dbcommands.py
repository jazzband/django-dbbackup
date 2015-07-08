from django.test import TestCase
from django.conf import settings
from dbbackup import dbcommands, settings as app_settings


class MySQLSettingsTest(TestCase):
    def setUp(self):
        self.database = settings.DATABASES['default']
        self.dbsettings = dbcommands.MySQLSettings(self.database)

    def test_get_extension(self):
        extension = self.dbsettings.get_extension()
        # TODO: Can't do below
        # self.assertEqual(app_settings.DBBACKUP_MYSQL_EXTENSION, extension)
        self.assertEqual('mysql', extension)

    def test_get_backup_commands(self):
        wanted_commands = [['mysqldump', '--user={adminuser}',
            '--password={password}', '{databasename}', '>']]
        commands = self.dbsettings.get_backup_commands()
        self.assertEqual(commands, wanted_commands)

    def test_get_restore_commands(self):
        wanted_commands = [['mysql', '--user={adminuser}',
            '--password={password}', '{databasename}', '<']]
        commands = self.dbsettings.get_restore_commands()
        self.assertEqual(commands, wanted_commands)


class PostgreSQLSettingsTest(TestCase):
    def setUp(self):
        self.database = settings.DATABASES['default']
        self.dbsettings = dbcommands.PostgreSQLSettings(self.database)

    def test_get_extension(self):
        extension = self.dbsettings.get_extension()
        self.assertEqual('psql', extension)

    def test_get_backup_commands(self):
        wanted_commands = [['pg_dump', '--username={adminuser}',
            '{databasename}', '>']]
        commands = self.dbsettings.get_backup_commands()
        self.assertEqual(commands, wanted_commands)

    def test_get_restore_commands(self):
        wanted_commands = [
            ['dropdb', '--username={adminuser}', '{databasename}'],
            ['createdb', '--username={adminuser}', '--owner={username}', '{databasename}'],
            ['psql', '-d', '{databasename}', '-f', '-', '--username={adminuser}', '--single-transaction', '<']
        ]
        commands = self.dbsettings.get_restore_commands()
        self.assertEqual(commands, wanted_commands)


class PostgisSQLSettingsTest(PostgreSQLSettingsTest):
    def setUp(self):
        self.database = settings.DATABASES['default']
        self.dbsettings = dbcommands.PostgisSQLSettings(self.database)

    def test_get_restore_commands(self):
        wanted_commands = [
            ['dropdb', '--username={adminuser}', '{databasename}'],
            ['createdb', '--username={adminuser}', '--owner={username}', '{databasename}'],
            ['psql', '--username={adminuser}', '-c', 'CREATE EXTENSION postgis;', '{databasename}'],
            ['psql', '-d', '{databasename}', '-f', '-', '--username={adminuser}', '--single-transaction', '<']
        ]
        commands = self.dbsettings.get_restore_commands()
        self.assertEqual(commands, wanted_commands)


class SQLiteSettingsTest(TestCase):
    def setUp(self):
        self.database = settings.DATABASES['default']
        self.dbsettings = dbcommands.SQLiteSettings(self.database)

    def test_get_extension(self):
        extension = self.dbsettings.get_extension()
        self.assertEqual('sqlite', extension)

    def test_get_backup_commands(self):
        wanted_commands = [['<READ_FILE>', '{databasename}']]
        commands = self.dbsettings.get_backup_commands()
        self.assertEqual(commands, wanted_commands)

    def test_get_get_restore_commands(self):
        wanted_commands = [['<WRITE_FILE>', '{databasename}']]
        commands = self.dbsettings.get_restore_commands()
        self.assertEqual(commands, wanted_commands)
