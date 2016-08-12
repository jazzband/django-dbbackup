Upgrade from 2.5.x
==================

Settings
--------

The following settings are now useless, you can remove them:

- ``DBBACKUP_BACKUP_ENVIRONMENT``: Must be set in ``CONNECTORS['dbname']['env']``
- ``DBBACKUP_RESTORE_ENVIRONMENT``: Same than ``BACKUP_ENVIRONMENT``
- ``DBBACKUP_FORCE_ENGINE``
- ``DBBACKUP_READ_FILE``
- ``DBBACKUP_WRITE_FILE``
- ``DBBACKUP_BACKUP_DIRECTORY``: Was used by Filesystem storage, use
  ``location`` parameter
- ``DBBACKUP_SQLITE_BACKUP_COMMANDS``: Was used by SQLite database, use
  ``CONNECTORS``'s parameters.
- ``DBBACKUP_SQLITE_RESTORE_COMMANDS``: Same than ``SQLITE_BACKUP_COMMANDS``
- ``DBBACKUP_MYSQL_BACKUP_COMMANDS``: Same than ``SQLITE_BACKUP_COMMANDS`` but
  for MySQL
- ``DBBACKUP_MYSQL_RESTORE_COMMANDS``: Same than ``MYSQL_BACKUP_COMMANDS``
- ``DBBACKUP_POSTGRESQL_BACKUP_COMMANDS`` Same than ``MYSQL_BACKUP_COMMANDS``
  but for PostgreSQL
- ``DBBACKUP_POSTGRESQL_RESTORE_COMMANDS``: Same than
  ``DBBACKUP_POSTGRESQL_BACKUP_COMMANDS``: Was used for activate PostGIS, use
  ``PgDumpGisConnector`` connector for enable this option
- ``DBBACKUP_POSTGRESQL_RESTORE_SINGLE_TRANSACTION``: Must be set in
  ``CONNTECTORS['dbname']['single_transaction']``
- ``DBBACKUP_BUILTIN_STORAGE``

Commands
--------

dbrestore
~~~~~~~~~

``--backup-extension`` has been removed, DBBackup should automaticaly
know the appropriate file.

Listing from this command, ``--list``, has been removed in favor of
``listbackups`` command.

mediabackup
~~~~~~~~~~~

``mediabackup``'s ``--no-compress`` option has been replaced by ``--compress``
for keep consistency with other commands.

Now this command can backup remote storage, not only filesystem's
``DBBACKUP_BACKUP_DIRECTORY``. 

mediarestore
~~~~~~~~~~~~

You are now able to restore your media files backups. Unfortunately you'll not
be able to restore old backup files.

Database connector
------------------

We made a total refactoring of DBCommands system. It is now easier to use,
configure and implement a custom one.

All database configuration for backups are defined in settings
``DBBACKUP_CONNECTORS``. By default, the ``DATABASES``
parameters are used but can be overrided in this new constant.

This dictionnary stores configuration about how backups are made,
what is the path of backup command (``/bin/mysqldump``), add suffix or prefix
to the command line, environment variable, etc.

The system stay pretty simple and can detect alone how to backup your DB.
If it can't just submit us what is your Django DB Engine and we'll try to fix
it.

SQLite
~~~~~~

Previously backup was made by copy the database file, now you have the choice
between make a raw snaphot or make a real SQL dump. It can be useful to exclude
tables or don't overwrite data.

If you want to restore your old backups choose
``dbbackup.db.sqlite.SqliteCPConnector``.


Storage engine
--------------

All storage engines has been removed from DBBackup except the basic. Now this
object will use Django storages as driver.

``settings.DBBACKUP_STORAGE`` must now be a full path to a Django storage, for
example ``'django.core.files.storage.FileSystemStorage'``.
``settings.DBBACKUP_STORAGE_OPTIONS`` hold its function of gather storage's
options.

If you was using a removed storage backend, don't worry, we ensure you'll
have a solution by test and write equivalent in Django-Storages.
