.. building docs: cd django-dbbackup/docs && make html

Django Database Backup
======================

This Django application provides management commands to help backup and
restore your project database and media files with various storages such as
Amazon S3, DropBox or local file system.

It is made for:

- Ensure yours backup with GPG signature and encryption
- Archive with compression
- Deal easily with remote archiving
- Use Crontab or Celery to setup automated backups.
- Great to keep your development database up to date.

.. warning::

    Django DBBackup version 3 make great changements see
    `Upgrade documentation`_ to help to up to date.

.. _`Upgrade documentation`: upgrade.html

Contents:

.. toctree::
   :maxdepth: 1

   installation
   configuration
   databases
   storage
   commands
   integration
   upgrade
   contributing
   changelog

Compatibility
-------------

As we want to ensure a lot of platforms will be able to save data before
upgrading, Django-DBBackup supports PyPy, 3.2 to 3.5 and Django
greater than 2.2

Other Resources
===============

* `GitHub repository`_
* `PyPi project`_
* `Read The Docs`_
* `GitHub issues`_
* `GitHub pull requests`_
* `Travis CI`_
* `Coveralls`_

.. _`GitHub repository`: https://github.com/django-dbbackup/django-dbbackup
.. _`PyPi project`: https://pypi.python.org/pypi/django-dbbackup/
.. _`Read The Docs`: http://django-dbbackup.readthedocs.org/
.. _`GitHub issues`: https://github.com/django-dbbackup/django-dbbackup/issues
.. _`GitHub pull requests`: https://github.com/django-dbbackup/django-dbbackup/pulls
.. _`Travis CI`: https://travis-ci.org/django-dbbackup/django-dbbackup
.. _`Coveralls`: https://coveralls.io/github/django-dbbackup/django-dbbackup

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
