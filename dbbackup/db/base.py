from importlib import import_module

CONNECTOR_MAPPING = {
    'django.db.backends.sqlite3': 'dbbackup.db.sqlite.SqliteConnector',
}


def get_connector(database_name=None):
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
    def __init__(self, database_name=None):
        from django.db import connections, DEFAULT_DB_ALIAS
        database_name = database_name or DEFAULT_DB_ALIAS
        self.connection = connections[database_name]

    def create_dump(self):
        raise NotImplementedError("create_dump not implemented")

    def restore_dump(self, backup_file):
        raise NotImplementedError("restore_dump not implemented")
