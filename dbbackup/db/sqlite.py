import warnings
from tempfile import SpooledTemporaryFile
from shutil import copyfileobj
from django.db import IntegrityError, OperationalError
from django.utils.six import BytesIO
from .base import BaseDBConnetor


DUMP_TABLES = """
SELECT "name", "type", "sql"
FROM "sqlite_master"
WHERE "sql" NOT NULL AND "type" == 'table'
ORDER BY "name"
"""
DUMP_ETC = """
SELECT "name", "type", "sql"
FROM "sqlite_master"
WHERE "sql" NOT NULL AND "type" IN ('index', 'trigger', 'view')
"""


class SqliteConnector(BaseDBConnetor):
    """
    Create a dump at SQL layer like could make ``.dumps`` in sqlite3.
    Restore by evaluate the created SQL.
    """
    def _write_dump(self, fileobj, exclude):
        cursor = self.connection.cursor()
        cursor.execute(DUMP_TABLES)
        for table_name, type, sql in cursor.fetchall():
            if table_name.startswith('sqlite_') or table_name in exclude:
                continue
            elif sql.startswith('CREATE TABLE'):
                sql = sql.replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS')
                sql = sql.replace('\n    ', '')
                sql = sql.replace('\n)', ')')
                fileobj.write(("%s;\n" % sql).encode('UTF-8'))
            else:
                fileobj.write("%s;\n" % sql)
            table_name_ident = table_name.replace('"', '""')
            res = cursor.execute('PRAGMA table_info("{0}")'.format(table_name_ident))
            column_names = [str(table_info[1]) for table_info in res.fetchall()]
            q = """SELECT 'INSERT INTO "{0}" VALUES({1})' FROM "{0}";\n""".format(
                table_name_ident,
                ",".join("""'||quote("{0}")||'""".format(col.replace('"', '""'))
                         for col in column_names))
            query_res = cursor.execute(q)
            for row in query_res:
                fileobj.write(("%s;\n" % row[0]).encode('UTF-8'))
            schema_res = cursor.execute(DUMP_ETC)
            for name, type, sql in schema_res.fetchall():
                if sql.startswith("CREATE INDEX"):
                    sql = sql.replace('CREATE INDEX', 'CREATE INDEX IF NOT EXISTS')
                fileobj.write(('%s;\n' % sql).encode('UTF-8'))
        cursor.close()

    def create_dump(self, exclude=None):
        if not self.connection.is_usable():
            self.connection.connect()
        dump_file = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
        self._write_dump(dump_file, exclude or [])
        dump_file.seek(0)
        return dump_file

    def restore_dump(self, dump):
        if not self.connection.is_usable():
            self.connection.connect()
        cursor = self.connection.cursor()
        for line in dump.readlines():
            try:
                cursor.execute(line.decode('UTF-8') )
            except OperationalError as err:
                warnings.warn("Error in db restore: %s" % err)
            except IntegrityError as err:
                warnings.warn("Error in db restore: %s" % err)


class SqliteCPConnector(BaseDBConnetor):
    """
    Create a dump by copy the binary data file.
    Restore by simply copy to the good location.
    """
    def create_dump(self, exclude=None):
        path = self.connection.settings_dict['NAME']
        dump = BytesIO()
        with open(path, 'rb') as db_file:
            copyfileobj(db_file, dump)
        dump.seek(0)
        return dump

    def restore_dump(self, dump):
        path = self.connection.settings_dict['NAME']
        with open(path, 'wb') as db_file:
            copyfileobj(dump, db_file)
