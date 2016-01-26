Django Database Backup
======================

.. image:: https://api.travis-ci.org/django-dbbackup/django-dbbackup.svg
        :target: https://travis-ci.org/django-dbbackup/django-dbbackup

.. image:: https://readthedocs.org/projects/django-dbbackup/badge/?version=latest
        :target: https://readthedocs.org/projects/django-dbbackup/?badge=latest
        :alt: Documentation Status

.. image:: https://coveralls.io/repos/django-dbbackup/django-dbbackup/badge.svg?branch=master&service=github
        :target: https://coveralls.io/github/django-dbbackup/django-dbbackup?branch=master


This Django application provides management commands to help backup and
restore your project database and media files with various storages such as
Amazon S3, DropBox or local file storage.

It is made for:

-  Ensure yours backup with GPG signature and encryption
-  Archive with compression
-  Use Crontab or Celery to setup automated backups.
-  Great to keep your development database up to date.

Docs
====

See our offical documentation at `Read The Docs`_.


Management Commands
===================

dbbackup
--------
Backup your database to the specified storage. By default this will backup all databases specified in your settings.py file and will not delete any old backups. You can optionally specify a server name to be included in the backup filename.

    dbbackup [-s <servername>] [-d <database>] [--clean] [--compress] [--encrypt] [--backup-extension <file-extension>]

dbrestore
---------
Restore your database from the specified storage. By default this will lookup the latest backup and restore from that. You may optionally specify a servername if you you want to backup a database image that was created from a different server. You may also specify an explicit local file to backup from.

    dbrestore [-d <database>] [-s <servername>] [-f <localfile>] [--uncompress] [--backup-extension <file-extension>]

mediabackup
-----------
Backup media files. Default this will backup the files in the MEDIA_ROOT. Optionally you can set the DBBACKUP_MEDIA_PATH setting.

   mediabackup [--encrypt] [--clean] [--servername <servername>]


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
