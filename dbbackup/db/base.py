import shlex
from tempfile import SpooledTemporaryFile
from subprocess import Popen
from importlib import import_module
from dbbackup import settings

CONNECTOR_MAPPING = {
    'django.db.backends.sqlite3': 'dbbackup.db.sqlite.SqliteConnector',
    'django.db.backends.mysql': 'dbbackup.db.mysql.MysqldumpConnector',
}


def get_connector(database_name=None):
    """
    Get a connector from its database key in setttings.
    """
    from django.db import connections, DEFAULT_DB_ALIAS
    database_name = database_name or DEFAULT_DB_ALIAS
    connection = connections[database_name]
    engine = connection.settings_dict['ENGINE']
    connector_path = CONNECTOR_MAPPING[engine]
    connector_module_path = '.'.join(connector_path.split('.')[:-1])
    module = import_module(connector_module_path)
    connector_name = connector_path.split('.')[-1]
    connector = getattr(module, connector_name)
    return connector(database_name)


class BaseDBConnetor(object):
    """
    Base class for create database connector. This kind of object creates
    interaction with database and allow backup and restore operations.
    """
    def __init__(self, database_name=None):
        from django.db import connections, DEFAULT_DB_ALIAS
        self.database_name = database_name or DEFAULT_DB_ALIAS
        self.connection = connections[database_name]

    @property
    def settings(self):
        if not hasattr(self, '_settings'):
            sett = self.connection.settings_dict.copy()
            sett.update(settings.CONNECTORS.get(self.database_name, {}))
            self._settings = sett
        return self._settings

    def create_dump(self):
        raise NotImplementedError("create_dump not implemented")

    def restore_dump(self, dump):
        raise NotImplementedError("restore_dump not implemented")


class BaseCommandDBConnetor(BaseDBConnetor):
    """
    Base class for create database connector based on command line tools.
    """
    def run_command(self, command, stdin=None):
        stdout = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
        cmd = shlex.split(command)
        process = Popen(cmd, stdin=stdin, stdout=stdout)
        process.wait()
        if process.poll():
            raise Exception("Error running: %s" % command)
        stdout.seek(0)
        return stdout
