Database settings
=================

The following databases are supported by this application:

- SQLite
- MySQL
- PostgreSQL
- MongoDB
- And the ones you will implement

By default, DBBackup will try to use your database settings in ``DATABASES``
for handle database, but some databases required custom options and you could
want to use different parameters for backup. That why we included a
``DBBACKUP_CONNECTORS`` setting, it act like the ``DATABASES`` one: ::

    DBBACKUP_CONNECTORS = {
        'default': {
            'USER': 'backupuser',
            'PASSWORD': 'backuppassword',
            'HOST': 'replica-for-backup'
        }
    }

This configuration will allow to use a replica with different host and user,
which is a great pratice if you don't want to overload your main database.

DBBackup uses ``Connectors`` for create and restore backups, below you'll see
specific parameters for the built-in ones.

Common
------

All connectors have the following parameters:

CONNECTOR
~~~~~~~~~

Absolute path to a connector class by default it is:

- :class:`dbbackup.db.sqlite.SqliteConnector` for ``'django.db.backends.sqlite3'``
- :class:`dbbackup.db.mysql.MysqlDumpConnector` for ``django.db.backends.mysql``
- :class:`dbbackup.db.postgresql.PgDumpConnector` for ``django.db.backends.postgresql``
- :class:`dbbackup.db.mongodb.MongoDumpConnector` for ``django_mongodb_engine``

All built-in connectors are listed below.

EXCLUDE
~~~~~~~

Tables to exclude from backup as list. This option can be unavailable for
connectors making snapshots.

EXTENSION
~~~~~~~~~

Extension of backup file name, default ``'dump'``.

Command connectors
~~~~~~~~~~~~~~~~~~

Some connectors use command line tools as dump engine, ``mysqldump`` for
example. This kind of tools has common attributes:

DUMP_CMD
~~~~~~~~

Path to the command used for create a backup, default is the appropriate
command supposed to be in your PATH, for example: ``'mysqldump'`` for MySQL.

This setting is useful only for connectors using command line tools (children
of :class:`dbbackup.db.base.BaseCommandDBConnector`)

RESTORE_CMD
~~~~~~~~~~~

Same as ``DUMP_CMD`` but for restoring action.

DUMP_PREFIX and RESTORE_PREFIX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

String to include as prefix of dump or restore command. It will be add with
a space between launched command and its prefix.

DUMP_SUFFIX and RESTORE_PREFIX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

String to include as suffix of dump or restore command. It will be add with
a space between launched command and its suffix.

SQLite
------

SQLite uses by default :class:`dbbackup.db.sqlite.SqliteConnector`.

SqliteConnector
~~~~~~~~~~~~~~~

It is in pure Python and copy the behavior of ``.dump`` command for create a
SQL dump.

SqliteCPConnector
~~~~~~~~~~~~~~~~~

You can also use :class:`dbbackup.db.sqlite.SqliteCPConnector` for make simple
raw copy of your database file, like a snapshot.

In-memory database aren't dumpable with it.

MySQL
-----

MySQL uses by default :class:`dbbackup.db.mysql.MysqlDumpConnector`. It uses
``mysqldump`` and ``mysql`` for its job.

PostgreSQL
----------

Postgres uses by default :class:`dbbackup.db.postgres.PgDumpConnector`. It
allows PostGIS usage, and uses ``pg_dump`` and ``pg_restore`` for its job.
It can also uses ``psql`` for launch administration command.

SINGLE_TRANSACTION
~~~~~~~~~~~~~~~~~~

When doing a restore, wrap everything in a single transaction, so that errors
cause a rollback.

Default: ``True``

PostGis
-------

Same than PostgreSQL but launch ``CREATE EXTENSION IF NOT EXISTS postgis;``
before restore database.

PSQL_CMD
~~~~~~~~

Path to ``psql`` command used for administration tasks like enable PostGIS
for example, default is ``psql``.


ADMIN_USER
~~~~~~~~~~

Username used for launch action with privileges, extension creation for
example.

ADMIN_PASSWORD
~~~~~~~~~~~~~~

Password used for launch action with privileges, extension creation for
example.

MongoDB
-------

MongoDB uses by default :class:`dbbackup.db.mongodb.MongoDumpConnector`. it
uses ``mongodump`` and ``mongorestore`` for its job.

OBJECT_CHECK
~~~~~~~~~~~~

Validate documents before insert in database (option ``--objcheck`` in command line), default is ``True``.

DROP
~~~~

Replace objects that are already in database, (option ``--drop`` in command line), default is ``True``.

Custom connector
----------------

Create your connector is easy, create a children class from
:class:`dbbackup.db.base.BaseDBConnector` and create ``create_dump`` and
``restore_dump``.  If your connector uses a command line tool heritate from
:class:`dbbackup.db.base.BaseCommandDBConnector`
