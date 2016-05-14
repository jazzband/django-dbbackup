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


SQLite
------

SQLite uses by default :class:`dbbackup.db.sqlite.SqliteConnector`. It is in
pure Python and copy the behavior of ``.dump`` command for create a SQL dump.

You can also use :class:`dbbackup.db.sqlite.SqliteCPConnector` for make simple
raw copy of your database file.

MySQL
-----

MySQL uses by default :class:`dbbackup.db.mysql.MysqlDumpConnector`. It uses
``mysqldump`` and ``mysql`` for its job.

PostgreSQL
----------

Postgres uses by default :class:`dbbackup.db.postgres.PgDumpConnector`. It
allows PostGIS usage, and uses ``pg_dump`` and ``pg_restore`` for its job.

SINGLE_TRANSACTION
~~~~~~~~~~~~~~~~~~

When doing a restore, wrap everything in a single transaction, so that errors
cause a rollback.

Default: ``True``

USE_POSTGIS
~~~~~~~~~~~

When on PostGIS, set this setting to True enable add a 
``CREATE EXTENSION IF NOT EXISTS postgis;`` Postgres command.

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

Custom connector
----------------

Create your connector is easy, create a children class from
:class:`dbbackup.db.base.BaseDBConnector` and create ``create_dump`` and
``restore_dump``.  If your connector uses a command line tool heritate from
:class:`dbbackup.db.base.BaseCommandDBConnector`
