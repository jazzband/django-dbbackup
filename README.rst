Django Database Backup
======================

.. image:: https://api.travis-ci.org/django-dbbackup/django-dbbackup.svg
        :target: https://travis-ci.org/django-dbbackup/django-dbbackup

.. image:: https://readthedocs.org/projects/django-dbbackup/badge/?version=latest
        :target: http://django-dbbackup.readthedocs.io/
        :alt: Documentation Status

.. image:: https://coveralls.io/repos/django-dbbackup/django-dbbackup/badge.svg?branch=master&service=github
        :target: https://coveralls.io/github/django-dbbackup/django-dbbackup?branch=master

.. image:: https://landscape.io/github/django-dbbackup/django-dbbackup/master/landscape.svg?style=flat
        :target: https://landscape.io/github/django-dbbackup/django-dbbackup/master
        :alt: Code Health


This Django application provides management commands to help backup and
restore your project database and media files with various storages such as
Amazon S3, Dropbox, local file storage or any Django storage.

It is made for:

- Ensure your backup with GPG signature and encryption
- Archive with compression
- Deal easily with remote archiving
- Great to keep your development database up to date.
- Use Crontab or Celery to setup automated backups.

Docs
====

See our offical documentation at `Read The Docs`_.

Why use DBBackup
================

This software doesn't reinvent the wheel, in few words it is a pipe between
your Django project and your backup storage. It tries to use the traditional dump &
restore mechanisms, apply compression and/or encryption and use the storage system you desire.

It gives a simple interface to backup and restore your database or media
files.

Management Commands
===================

dbbackup
--------

Backup your database to the specified storage. By default this will backup all
databases specified in your settings.py file and will not delete any old
backups. You can optionally specify a server name to be included in the backup
filename. ::

  Usage: ./manage.py dbbackup [options]
  
  Options:
    --noinput             Tells Django to NOT prompt the user for input of any
                          kind.
    -q, --quiet           Tells Django to NOT output other text than errors.
    -c, --clean           Clean up old backup files
    -d DATABASE, --database=DATABASE
                          Database to backup (default: everything)
    -s SERVERNAME, --servername=SERVERNAME
                          Specify server name to include in backup filename
    -z, --compress        Compress the backup files
    -e, --encrypt         Encrypt the backup files
    -o OUTPUT_FILENAME, --output-filename=OUTPUT_FILENAME
                          Specify filename on storage
    -O OUTPUT_PATH, --output-path=OUTPUT_PATH
                          Specify where to store on local filesystem

dbrestore
---------

Restore your database from the specified storage. By default this will lookup
the latest backup and restore from that. You may optionally specify a
servername if you you want to backup a database image that was created from a
different server. You may also specify an explicit local file to backup from.

::

  Usage: ./manage.py dbrestore [options]
  
  Options:
    --noinput             Tells Django to NOT prompt the user for input of any
                          kind.
    -d DATABASE, --database=DATABASE
                          Database to restore
    -i INPUT_FILENAME, --input-filename=INPUT_FILENAME
                          Specify filename to backup from
    -I INPUT_PATH, --input-path=INPUT_PATH
                          Specify path on local filesystem to backup from
    -s SERVERNAME, --servername=SERVERNAME
                          Use a different servername backup
    -c, --decrypt         Decrypt data before restoring
    -p PASSPHRASE, --passphrase=PASSPHRASE
                          Passphrase for decrypt file
    -z, --uncompress      Uncompress gzip data before restoring


mediabackup
-----------

Backup media files by get them one by one, include in a TAR file. ::

  Usage: ./manage.py mediabackup [options]
  
  Options:
    --noinput             Tells Django to NOT prompt the user for input of any
                          kind.
    -q, --quiet           Tells Django to NOT output other text than errors.
    -c, --clean           Clean up old backup files
    -s SERVERNAME, --servername=SERVERNAME
                          Specify server name to include in backup filename
    -z, --compress        Compress the archive
    -e, --encrypt         Encrypt the backup files
    -o OUTPUT_FILENAME, --output-filename=OUTPUT_FILENAME
                          Specify filename on storage
    -O OUTPUT_PATH, --output-path=OUTPUT_PATH
                          Specify where to store on local filesystem

mediarestore
------------

Restore media files from storage backup to your media storage. ::

  Usage: ./manage.py mediarestore [options]
  
  Options:
    --noinput             Tells Django to NOT prompt the user for input of any
                          kind.
    -q, --quiet           Tells Django to NOT output other text than errors.
    -i INPUT_FILENAME, --input-filename=INPUT_FILENAME
                          Specify filename to backup from
    -I INPUT_PATH, --input-path=INPUT_PATH
                          Specify path on local filesystem to backup from
    -e, --decrypt         Decrypt data before restoring
    -p PASSPHRASE, --passphrase=PASSPHRASE
                          Passphrase for decrypt file
    -z, --uncompress      Uncompress gzip data before restoring
    -r, --replace         Replace existing files

Contributing
============

All contribution are very welcomed, propositions, problems, bugs and
enhancement are tracked with `GitHub issues`_ system and patch are submitted
via `pull requests`_.

We use `Travis`_ coupled with `Coveralls`_ as continious integration tools.

.. _`Read The Docs`: http://django-dbbackup.readthedocs.org/
.. _`GitHub issues`: https://github.com/django-dbbackup/django-dbbackup/issues
.. _`pull requests`: https://github.com/django-dbbackup/django-dbbackup/pulls
.. _Travis: https://travis-ci.org/django-dbbackup/django-dbbackup
.. _Coveralls: https://coveralls.io/github/django-dbbackup/django-dbbackup


.. image:: https://ga-beacon.appspot.com/UA-87461-7/django-dbbackup/home
        :target: https://github.com/igrigorik/ga-beacon

Tests
=====

Tests are stored in `dbbackup.tests` and for run them you must launch:

::

    python runtests.py

In fact, ``runtests.py`` acts as a ``manage.py`` file and all Django command
are available. So you could launch:

::

    python runtests.py shell

For get a Python shell configured with the test project. Also all test
command options are available and usable for run only some chosen tests.
See `Django test command documentation`_ for more informations about it.

.. _`Django test command documentation`: https://docs.djangoproject.com/en/stable/topics/testing/overview/#running-tests

There are even functional tests: ::

    ./functional.sh

See documentation for details about

To run the tests across all supported versions of Django and Python, you
can use Tox. Firstly install Tox:

::

    pip install tox

To run the tests just use the command ``tox`` in the command line.  If you
want to run the tests against just one specific test environment you can run
``tox -e <testenv>``.  For example, to run the tests with Python3.3 and
Django1.9 you would run:

::

    tox -e py3.3-django1.9

The available test environments can be found in ``tox.ini``.
