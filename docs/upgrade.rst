Upgrade from 2.5.x
==================

Settings
--------

The following settings are now useless, you can remove them:

- ``DBBACKUP_BACKUP_ENVIRONMENT``: Must be set in ``CONNECTORS['dbname']['env']``
- ``DBBACKUP_RESTORE_ENVIRONMENT``: Same as ``BACKUP_ENVIRONMENT``
- ``DBBACKUP_FORCE_ENGINE``
- ``DBBACKUP_READ_FILE``
- ``DBBACKUP_WRITE_FILE``
- ``DBBACKUP_BACKUP_DIRECTORY``: Was used by Filesystem storage, use
  ``location`` parameter
- ``DBBACKUP_SQLITE_BACKUP_COMMANDS``: Was used by SQLite database, use
  ``CONNECTORS``'s parameters.
- ``DBBACKUP_SQLITE_RESTORE_COMMANDS``: Same as ``SQLITE_BACKUP_COMMANDS``
- ``DBBACKUP_MYSQL_BACKUP_COMMANDS``: Same as ``SQLITE_BACKUP_COMMANDS`` but
  for MySQL
- ``DBBACKUP_MYSQL_RESTORE_COMMANDS``: Same as ``MYSQL_BACKUP_COMMANDS``
- ``DBBACKUP_POSTGRESQL_BACKUP_COMMANDS`` Same as ``MYSQL_BACKUP_COMMANDS``
  but for PostgreSQL
- ``DBBACKUP_POSTGRESQL_RESTORE_COMMANDS``: Same as
  ``DBBACKUP_POSTGRESQL_BACKUP_COMMANDS``: Was used to activate PostGIS, use
  ``PgDumpGisConnector`` connector to enable this option
- ``DBBACKUP_POSTGRESQL_RESTORE_SINGLE_TRANSACTION``: Must be set in
  ``CONNTECTORS['dbname']['single_transaction']``
- ``DBBACKUP_BUILTIN_STORAGE``

Commands
--------

dbrestore
~~~~~~~~~

``--backup-extension`` has been removed, DBBackup should automatically
know the appropriate file.

Listing from this command, ``--list``, has been removed in favor of
``listbackups`` command.

mediabackup
~~~~~~~~~~~

``mediabackup``'s ``--no-compress`` option has been replaced by ``--compress``
to maintain consistency with other commands.

This command can now backup remote storage, not only the local filesystem
``DBBACKUP_BACKUP_DIRECTORY``. 

mediarestore
~~~~~~~~~~~~

You are now able to restore your media files backups. Unfortunately you'll not
be able to restore backup files from previous versions of dbbackup.

Database connector
------------------

We made a total refactoring of DBCommands system. It is now easier to use,
configure and implement a custom connector.

All database configuration for backups are defined in settings
``DBBACKUP_CONNECTORS``. By default, the ``DATABASES``
parameters are used but can be overridden in this new constant.

This dictionary stores configuration about how backups are made,
 the path of the backup command (``/bin/mysqldump``), add a suffix or a prefix
to the command line, environment variable, etc.

The system has been kept pretty simple and can detect alone how to backup your DB.
If it can't just submit to us your Django DB Engine and we'll try to fix
it.

SQLite
~~~~~~

Previously a backup was made by copying the database file.  Now you have the choice
between making a raw snapshot or making a real SQL dump. It can be useful to exclude
tables or to not overwrite data.

If you want to restore your old backups choose
``dbbackup.db.sqlite.SqliteCPConnector``.


Storage engine
--------------

All storage engines has been removed from DBBackup except the basic filesystem storage.
The project now uses Django storages as an intermediary driver.

``settings.DBBACKUP_STORAGE`` must now be a full path to a Django storage, for
example ``'django.core.files.storage.FileSystemStorage'``.
``settings.DBBACKUP_STORAGE_OPTIONS`` maintains its function of containing the options of the storage.

If you were using a storage backend that has been removed, don't worry, we will ensure you
have a solution by testing and writing an equivalent using Django-Storages.
