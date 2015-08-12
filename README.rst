Django Database Backup
======================

.. image:: https://api.travis-ci.org/django-dbbackup/django-dbbackup.svg
        :target: https://travis-ci.org/django-dbbackup/ka-lite-gtk

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
