import warnings
from io import BytesIO
from shutil import copyfileobj
from tempfile import SpooledTemporaryFile

from django.db import IntegrityError, OperationalError

from .base import BaseDBConnector

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


class SqliteConnector(BaseDBConnector):
    """
    Create a dump at SQL layer like could make ``.dumps`` in sqlite3.
    Restore by evaluate the created SQL.
    """

    def _write_dump(self, fileobj):
        cursor = self.connection.cursor()
        cursor.execute(DUMP_TABLES)
        for table_name, _, sql in cursor.fetchall():
            if table_name.startswith("sqlite_") or table_name in self.exclude:
                continue
            if sql.startswith("CREATE TABLE"):
                sql = sql.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
                # Make SQL commands in 1 line
                sql = sql.replace("\n    ", "")
                sql = sql.replace("\n)", ")")
            fileobj.write(f"{sql};\n".encode())

            table_name_ident = table_name.replace('"', '""')
            res = cursor.execute(f'PRAGMA table_info("{table_name_ident}")')
            column_names = [str(table_info[1]) for table_info in res.fetchall()]
            q = """SELECT 'INSERT INTO "{0}" VALUES({1})' FROM "{0}";\n""".format(
                table_name_ident,
                ",".join(
                    """'||quote("{}")||'""".format(col.replace('"', '""'))
                    for col in column_names
                ),
            )
            query_res = cursor.execute(q)
            for row in query_res:
                fileobj.write(f"{row[0]};\n".encode())
            schema_res = cursor.execute(DUMP_ETC)
            for name, _, sql in schema_res.fetchall():
                if sql.startswith("CREATE INDEX"):
                    sql = sql.replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS")
                fileobj.write(f"{sql};\n".encode())
        cursor.close()

    def create_dump(self):
        if not self.connection.is_usable():
            self.connection.connect()
        dump_file = SpooledTemporaryFile(max_size=10 * 1024 * 1024)
        self._write_dump(dump_file)
        dump_file.seek(0)
        return dump_file

    def restore_dump(self, dump):
        if not self.connection.is_usable():
            self.connection.connect()
        cursor = self.connection.cursor()
        sql_command = b""
        sql_is_complete = True
        for line in dump.readlines():
            sql_command = sql_command + line
            line_str = line.decode("UTF-8")
            if line_str.startswith("INSERT") and not line_str.endswith(");\n"):
                sql_is_complete = False
                continue
            if not sql_is_complete and line_str.endswith(");\n"):
                sql_is_complete = True

            if sql_is_complete:
                try:
                    cursor.execute(sql_command.decode("UTF-8"))
                except (OperationalError, IntegrityError) as err:
                    warnings.warn(f"Error in db restore: {err}")
                sql_command = b""


class SqliteCPConnector(BaseDBConnector):
    """
    Create a dump by copy the binary data file.
    Restore by simply copy to the good location.
    """

    def create_dump(self):
        path = self.connection.settings_dict["NAME"]
        dump = BytesIO()
        with open(path, "rb") as db_file:
            copyfileobj(db_file, dump)
        dump.seek(0)
        return dump

    def restore_dump(self, dump):
        path = self.connection.settings_dict["NAME"]
        with open(path, "wb") as db_file:
            copyfileobj(dump, db_file)
