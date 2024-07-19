import logging
from typing import List, Optional
from urllib.parse import quote

from .base import BaseCommandDBConnector

logger = logging.getLogger("dbbackup.command")


def create_postgres_uri(self):
    host = self.settings.get("HOST") or "localhost"
    dbname = self.settings.get("NAME") or ""
    user = quote(self.settings.get("USER") or "")
    password = self.settings.get("PASSWORD") or ""
    password = f":{quote(password)}" if password else ""
    if not user:
        password = ""
    else:
        host = "@" + host

    port = ":{}".format(self.settings.get("PORT")) if self.settings.get("PORT") else ""
    dbname = f"--dbname=postgresql://{user}{password}{host}{port}/{dbname}"
    return dbname


class PgDumpConnector(BaseCommandDBConnector):
    """
    PostgreSQL connector, it uses pg_dump`` to create an SQL text file
    and ``psql`` for restore it.
    """

    extension = "psql"
    dump_cmd = "pg_dump"
    restore_cmd = "psql"
    single_transaction = True
    drop = True
    schemas: Optional[List[str]] = []

    def _create_dump(self):
        cmd = f"{self.dump_cmd} "
        cmd = cmd + create_postgres_uri(self)

        for table in self.exclude:
            cmd += f" --exclude-table-data={table}"

        if self.drop:
            cmd += " --clean"

        if self.schemas:
            # First schema is not prefixed with -n
            # when using join function so add it manually.
            cmd += " -n " + " -n ".join(self.schemas)

        cmd = f"{self.dump_prefix} {cmd} {self.dump_suffix}"
        stdout, stderr = self.run_command(cmd, env=self.dump_env)
        return stdout

    def _restore_dump(self, dump):
        cmd = f"{self.restore_cmd} "
        cmd = cmd + create_postgres_uri(self)

        # without this, psql terminates with an exit value of 0 regardless of errors
        cmd += " --set ON_ERROR_STOP=on"

        if self.schemas:
            cmd += " -n " + " -n ".join(self.schemas)

        if self.single_transaction:
            cmd += " --single-transaction"

        cmd += " {}".format(self.settings["NAME"])
        cmd = f"{self.restore_prefix} {cmd} {self.restore_suffix}"
        stdout, stderr = self.run_command(cmd, stdin=dump, env=self.restore_env)
        return stdout, stderr


class PgDumpGisConnector(PgDumpConnector):
    """
    PostgreGIS connector, same than :class:`PgDumpGisConnector` but enable
    postgis if not made.
    """

    psql_cmd = "psql"

    def _enable_postgis(self):
        cmd = f'{self.psql_cmd} -c "CREATE EXTENSION IF NOT EXISTS postgis;"'
        cmd += " --username={}".format(self.settings["ADMIN_USER"])
        cmd += " --no-password"

        if self.settings.get("HOST"):
            cmd += " --host={}".format(self.settings["HOST"])

        if self.settings.get("PORT"):
            cmd += " --port={}".format(self.settings["PORT"])

        return self.run_command(cmd)

    def _restore_dump(self, dump):
        if self.settings.get("ADMIN_USER"):
            self._enable_postgis()
        return super()._restore_dump(dump)


class PgDumpBinaryConnector(PgDumpConnector):
    """
    PostgreSQL connector, it uses pg_dump`` to create an SQL text file
    and ``pg_restore`` for restore it.
    """

    extension = "psql.bin"
    dump_cmd = "pg_dump"
    restore_cmd = "pg_restore"
    single_transaction = True
    drop = True

    def _create_dump(self):
        cmd = f"{self.dump_cmd} "
        cmd = cmd + create_postgres_uri(self)

        cmd += " --format=custom"
        for table in self.exclude:
            cmd += f" --exclude-table-data={table}"

        if self.schemas:
            cmd += " -n " + " -n ".join(self.schemas)

        cmd = f"{self.dump_prefix} {cmd} {self.dump_suffix}"
        stdout, _ = self.run_command(cmd, env=self.dump_env)
        return stdout

    def _restore_dump(self, dump):
        dbname = create_postgres_uri(self)
        cmd = f"{self.restore_cmd} {dbname}"

        if self.single_transaction:
            cmd += " --single-transaction"

        if self.drop:
            cmd += " --clean"

        if self.schemas:
            cmd += " -n " + " -n ".join(self.schemas)

        cmd = f"{self.restore_prefix} {cmd} {self.restore_suffix}"
        stdout, stderr = self.run_command(cmd, stdin=dump, env=self.restore_env)
        return stdout, stderr
