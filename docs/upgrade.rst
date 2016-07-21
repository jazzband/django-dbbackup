Settings
========

The following settings are now useless, you can remove them:

- ``DBBACKUP_BACKUP_ENVIRONMENT``: Must be set in ``CONNECTORS['dbname']['env']``
- ``DBBACKUP_RESTORE_ENVIRONMENT``: Same than ``BACKUP_ENVIRONMENT``
- ``DBBACKUP_FORCE_ENGINE``
- ``DBBACKUP_READ_FILE``
- ``DBBACKUP_WRITE_FILE``
- ``DBBACKUP_BACKUP_DIRECTORY``

Commands
========

mediabackup
-----------

``mediabackup``'s ``--no-compress`` option has been replaced by ``--compress``
for keep consistency with other commands.o

Backups created with ``django-dbbackup<3`` can not be restored.

Database connector
==================

Total refactoring of DBCommands system. It is now easier to use, configurate
and implement a custom one.

All database configuration for backups are defined in settings
``DBBACKUP_CONNECTORS``. By default, the ``DATABASES``
parameters are used but can be overrided in this new constant.

This dictionnary stores configuration about how backups are made,
what is the path of backup command (``/bin/mysqldump``), add suffix or prefix
to the command line, environment variable, etc.

The system stay pretty simple and can detect alone how to backup your DB,
if it can't just submit us what is your Django DB Engine and we'll fix it.

SQLite
------

Previously backup was made by copy the database file, now you have the choice
between make a raw snaphot or make a real SQL dump. It can be useful.

Media backup and restore
========================

You are now able to restore your media files backups. Unfortunately you'll not
be able to restore old backup files.

Storage engine
==============


