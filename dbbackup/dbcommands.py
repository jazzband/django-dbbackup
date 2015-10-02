"""
Process the Backup or Restore commands.
"""
from __future__ import (absolute_import, division,
                        unicode_literals)
import copy
import os
import re
import six
import shlex
import logging
from shutil import copyfileobj
from subprocess import Popen
from django.core.management.base import CommandError
from django.utils import timezone
from dbbackup import (settings, utils)

from .utils import filename_generate


class BaseEngineSettings:
    """Base settings for a database engine"""

    def __init__(self, database):
        self.database = database
        self.database_adminuser = self.database.get('ADMINUSER', self.database['USER'])
        self.database_user = self.database['USER']
        self.database_password = self.database['PASSWORD']
        self.database_name = self.database['NAME']
        self.database_host = self.database.get('HOST', '')
        self.database_port = str(self.database.get('PORT', ''))
        self.extension = self.get_extension()
        self.BACKUP_COMMANDS = self.get_backup_commands()
        self.RESTORE_COMMANDS = self.get_restore_commands()

    def get_extension(self):
        raise NotImplementedError("Subclasses must implement get_extension")

    def get_backup_commands(self):
        raise NotImplementedError("Subclasses must implement get_backup_commands")

    def get_restore_commands(self):
        raise NotImplementedError("Subclasses must implement get_restore_commands")

    def get_env(self):
        """Extra environment variables to be passed to shell execution"""
        return {}


class MySQLSettings(BaseEngineSettings):
    """Settings for the MySQL database engine"""

    def get_extension(self):
        return getattr(settings, 'DBBACKUP_MYSQL_EXTENSION', 'mysql')

    def get_backup_commands(self):
        backup_commands = settings.MYSQL_BACKUP_COMMANDS
        if not backup_commands:
            command = 'mysqldump --user={adminuser} --password={password}'
            if self.database_host:
                command = '%s --host={host}' % command
            if self.database_port:
                command = '%s --port={port}' % command
            command = '%s {databasename} >' % command
            backup_commands = [shlex.split(command)]
        return backup_commands

    def get_restore_commands(self):
        restore_commands = settings.MYSQL_RESTORE_COMMANDS
        if not restore_commands:
            command = 'mysql --user={adminuser} --password={password}'
            if self.database_host:
                command = '%s --host={host}' % command
            if self.database_port:
                command = '%s --port={port}' % command
            command = '%s {databasename} <' % command
            restore_commands = [shlex.split(command)]
        return restore_commands


class PostgreSQLSettings(BaseEngineSettings):
    """Settings for the PostgreSQL database engine"""

    def get_extension(self):
        return getattr(settings, 'DBBACKUP_POSTGRESQL_EXTENSION', 'psql')

    def get_backup_commands(self):
        backup_commands = settings.POSTGRESQL_BACKUP_COMMANDS
        if not backup_commands:
            command = 'pg_dump --username={adminuser}'
            if self.database_host:
                command = '%s --host={host}' % command
            if self.database_port:
                command = '%s --port={port}' % command
            command = '%s {databasename} >' % command
            backup_commands = [shlex.split(command)]
        return backup_commands

    def get_restore_commands(self):
        restore_commands = settings.POSTGRESQL_RESTORE_COMMANDS
        if not restore_commands:
            restore_commands = [
                shlex.split(self.dropdb_command()),
                shlex.split(self.createdb_command()),
            ]
            prepare_db_command = self.prepare_db_command()
            if prepare_db_command:
                restore_commands.append(shlex.split(prepare_db_command))
            restore_commands.append(
                shlex.split(self.import_command())
            )
        return restore_commands

    def dropdb_command(self):
        """Constructs the PostgreSQL dropdb command"""
        command = 'dropdb --username={adminuser}'
        if self.database_host:
            command = '%s --host={host}' % command
        if self.database_port:
            command = '%s --port={port}' % command
        return '%s {databasename}' % command

    def createdb_command(self):
        """Constructs the PostgreSQL createdb command"""
        command = 'createdb --username={adminuser} --owner={username}'
        if self.database_host:
            command = '%s --host={host}' % command
        if self.database_port:
            command = '%s --port={port}' % command
        return '%s {databasename}' % command

    def prepare_db_command(self):
        """Use this to run a command after createdb"""
        return None

    def import_command(self):
        """Constructs the PostgreSQL db import command"""
        command = 'psql -d {databasename} -f - --username={adminuser}'
        if self.database_host:
            command = '%s --host={host}' % command
        if self.database_port:
            command = '%s --port={port}' % command
        if settings.POSTGRESQL_RESTORE_SINGLE_TRANSACTION:
            command += ' --single-transaction '
        return '%s <' % command

    def get_env(self):
        """Extra environment variables to be passed to shell execution"""
        return {'PGPASSWORD': '{password}'}


class PostgisSQLSettings(PostgreSQLSettings):
    """Settings for the PostgreSQL database engine"""

    def prepare_db_command(self):
        if settings.POSTGIS_SPATIAL_REF:
            return None
        command = 'psql --username={adminuser} -c "CREATE EXTENSION postgis;"'
        if self.database_host:
            command = '%s --host={host}' % command
        if self.database_port:
            command = '%s --port={port}' % command
        return '%s {databasename}' % command


class SQLiteSettings(BaseEngineSettings):
    """Settings for the SQLite database engine"""

    def get_extension(self):
        return getattr(settings, 'DBBACKUP_SQLITE_EXTENSION', 'sqlite')

    def get_backup_commands(self):
        return settings.SQLITE_BACKUP_COMMANDS

    def get_restore_commands(self):
        return settings.SQLITE_RESTORE_COMMANDS


class DBCommands:
    """ Process the Backup or Restore commands. """

    def __init__(self, database):
        self.database = database
        self.engine = settings.FORCE_ENGINE or self.database['ENGINE'].split('.')[-1]
        self.settings = self._get_settings()
        self.logger = logging.getLogger('dbbackup.dbbcommands')

    def _get_settings(self):
        """ Returns the proper settings dictionary. """
        if any(e in self.engine for e in ['mysql']):
            return MySQLSettings(self.database)
        elif any(e in self.engine for e in ['postgis']):
            return PostgisSQLSettings(self.database)
        elif any(e in self.engine for e in ['postgres']):
            return PostgreSQLSettings(self.database)
        elif any(e in self.engine for e in ['sqlite']):
            return SQLiteSettings(self.database)

    def _clean_passwd(self, instr):
        return instr.replace(self.database['PASSWORD'], '******')

    def translate_command(self, command):
        """ Translate the specified command or string. """
        def replace(s):
            s = (
                s.replace('{username}', self.database['USER'])
                 .replace('{adminuser}', self.database.get('ADMINUSER', self.database['USER']))
                 .replace('{password}', self.database['PASSWORD'])
                 .replace('{databasename}', self.database['NAME'])
                 .replace('{host}', self.database['HOST'])
                 .replace('{port}', str(self.database['PORT']))
             )
            return s
        if isinstance(command, six.string_types):
            return replace(command)
        command = copy.copy(command)
        for i in range(len(command)):
            command[i] = replace(command[i])
        return command

    # TODO: Clean wildcard
    def filename(self, servername=None, wildcard=None):
        extension = self.settings.extension
        return filename_generate(extension, self.settings.database['NAME'],
                                 servername)

    def filename_match(self, servername=None, wildcard='*'):
        """ Return the prefix for backup filenames. """
        return self.filename(servername, wildcard)

    def filter_filepaths(self, filepaths, servername=None):
        """ Returns a list of backups file paths from the dropbox entries. """
        regex = r'[\^\%s]%s' % (os.sep, self.filename_match(servername, '.*?'))
        filepaths = [path for path in filepaths if re.search(regex, path)]
        return filepaths

    def run_backup_commands(self, stdout):
        """ Translate and run the backup commands. """
        return self.run_commands(self.settings.BACKUP_COMMANDS, stdout=stdout)

    def run_restore_commands(self, stdin):
        """ Translate and run the backup commands. """
        stdin.seek(0)
        return self.run_commands(self.settings.RESTORE_COMMANDS, stdin=stdin)

    def run_commands(self, commands, stdin=None, stdout=None):
        """ Translate and run the specified commands. """
        for command in commands:
            command = self.translate_command(command)
            if (command[0] == settings.READ_FILE):
                self.read_file(command[1], stdout)
            elif (command[0] == settings.WRITE_FILE):
                self.write_file(command[1], stdin)
            else:
                self.run_command(command, stdin, stdout)

    def run_command(self, command, stdin=None, stdout=None):
        """ Run the specified command. """
        devnull = open(os.devnull, 'w')
        pstdin = stdin if command[-1] == '<' else None
        pstdout = stdout if command[-1] == '>' else devnull
        command = [arg for arg in command if arg not in ['<', '>']]
        self.logger.info(self._clean_passwd("Running: %s" % ' '.join(command)))
        env = self.settings.get_env()
        env.update(settings.BACKUP_ENVIRONMENT)
        for k, v in env.items():
            env[k] = self.translate_command(v)
        updated_osenv = os.environ.copy()
        updated_osenv.update(env)
        process = Popen(command, stdin=pstdin, stdout=pstdout, env=updated_osenv)
        process.wait()
        devnull.close()
        if process.poll():
            raise CommandError("Error running: %s" % command)

    def read_file(self, filepath, stdout):
        """ Read the specified file to stdout. """
        self.logger.info("Reading: %s", filepath)
        with open(filepath, "rb") as fd:
            copyfileobj(fd, stdout)

    def write_file(self, filepath, stdin):
        """ Write the specified file from stdin. """
        self.logger.info("Writing: %s", filepath)
        with open(filepath, 'wb') as fd:
            copyfileobj(stdin, fd)
