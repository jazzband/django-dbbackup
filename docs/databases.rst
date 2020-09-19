Database settings
=================

The following databases are supported by this application:

- SQLite
- MySQL
- PostgreSQL
- MongoDB
- And the ones you will implement

By default, DBBackup will try to use your database settings in ``DATABASES``
for handle database, but some databases require custom options so you could
want to use different parameters for backup. That's why we included a
``DBBACKUP_CONNECTORS`` setting; it acts like the ``DATABASES`` one: ::

    DBBACKUP_CONNECTORS = {
        'default': {
            'USER': 'backupuser',
            'PASSWORD': 'backuppassword',
            'HOST': 'replica-for-backup'
        }
    }

This configuration will allow you to use a replica with a different host and user,
which is a great pratice if you don't want to overload your main database.

DBBackup uses ``Connectors`` for creating and restoring backups; below you'll see
specific parameters for the built-in ones.

Common
------

All connectors have the following parameters:

CONNECTOR
~~~~~~~~~

Absolute path to a connector class by default is:

- :class:`dbbackup.db.sqlite.SqliteConnector` for ``'django.db.backends.sqlite3'``
- :class:`dbbackup.db.mysql.MysqlDumpConnector` for ``django.db.backends.mysql``
- :class:`dbbackup.db.postgresql.PgDumpConnector` for ``django.db.backends.postgresql``
- :class:`dbbackup.db.postgresql.PgDumpGisConnector` for ``django.contrib.gis.db.backends.postgis``
- :class:`dbbackup.db.mongodb.MongoDumpConnector` for ``django_mongodb_engine``

All supported built-in connectors are listed below.

EXCLUDE
~~~~~~~

Tables to exclude from backup as list. This option can be unavailable for
connectors making snapshots.

EXTENSION
~~~~~~~~~

Extension of backup file name, default ``'dump'``.

Command connectors
------------------

Some connectors use command line tools as dump engine, ``mysqldump`` for
example. These kinds of tools have common attributes:

DUMP_CMD
~~~~~~~~

Path to the command used to create a backup; default is the appropriate
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

ENV, DUMP_ENV and RESTORE_ENV
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Environment variables used during command running, default are ``{}``. ``ENV``
is used for every command, ``DUMP_ENV`` and ``RESTORE_ENV``  override the
values defined in ``ENV`` during the dedicated commands.

USE_PARENT_ENV
~~~~~~~~~~~~~~

Specify if the connector will use its parent's environment variables. By
default it is ``True`` to keep ``PATH``.

SQLite
------

SQLite uses by default :class:`dbbackup.db.sqlite.SqliteConnector`.

SqliteConnector
~~~~~~~~~~~~~~~

It is in pure Python and copys the behavior of ``.dump`` command for creating a
SQL dump.

SqliteCPConnector
~~~~~~~~~~~~~~~~~

You can also use :class:`dbbackup.db.sqlite.SqliteCPConnector` for making a 
simple raw copy of your database file, like a snapshot.

In-memory database aren't dumpable with it.

MySQL
-----

MySQL uses by default :class:`dbbackup.db.mysql.MysqlDumpConnector`. It uses
``mysqldump`` and ``mysql`` for its job.

PostgreSQL
----------

Postgres uses by default :class:`dbbackup.db.postgresql.PgDumpConnector`, but
we advise you to use :class:`dbbackup.db.postgresql.PgDumpBinaryConnector`. The
first one uses ``pg_dump`` and ``pqsl`` for its job, creating RAW SQL files.

The second uses ``pg_restore`` with binary dump files.

They can also use ``psql`` for launch administration command.

SINGLE_TRANSACTION
~~~~~~~~~~~~~~~~~~

When doing a restore, wrap everything in a single transaction, so errors
cause a rollback.

This corresponds to ``--single-transaction`` argument of ``psql`` and
``pg_restore``.

Default: ``True``

DROP
~~~~

With ``PgDumpConnector``, it includes tables dropping statements in dump file.
``PgDumpBinaryConnector`` drops at restoring.

This corresponds to ``--clean`` argument of ``pg_dump`` and ``pg_restore``.

Default: ``True``

PostGIS
-------

Set in :class:`dbbackup.db.postgresql.PgDumpGisConnector`, it does the same as
PostgreSQL but launchs ``CREATE EXTENSION IF NOT EXISTS postgis;`` before
restore database.

PSQL_CMD
~~~~~~~~

Path to ``psql`` command used for administration tasks like enable PostGIS
for example, default is ``psql``.


PASSWORD
~~~~~~~~

If you fill this settings ``PGPASSWORD`` environment variable will be used
with every commands. For security reason, we advise to use ``.pgpass`` file.

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

Validate documents before inserting in database (option ``--objcheck`` in command line), default is ``True``.

DROP
~~~~

Replace objects that are already in database, (option ``--drop`` in command line), default is ``True``.

Custom connector
----------------

Creating your connector is easy; create a children class from
:class:`dbbackup.db.base.BaseDBConnector` and create ``_create_dump`` and
``_restore_dump``.  If your connector uses a command line tool, inherit it from
:class:`dbbackup.db.base.BaseCommandDBConnector`

Connecting a Custom connector
-----------------------------

Here is an example, on how to easily connect a custom connector that you have created or even that you simply want to reuse: ::

    DBBACKUP_CONNECTOR_MAPPING = {
        'transaction_hooks.backends.postgis': 'dbbackup.db.postgresql.PgDumpGisConnector',
    }

Obviously instead of :class:`dbbackup.db.postgresql.PgDumpGisConnector` you can
use the custom connector you have created yourself and ``transaction_hooks.backends.postgis``
is simply the database engine name you are using.
