.. building docs: cd django-dbbackup/docs && make html

Django Database Backup
======================

This Django application provides management commands to help backup and
restore your project database to AmazonS3, Dropbox or Local Disk.

-  Keep your important data secure and offsite.
-  Use Crontab or Celery to setup automated backups.
-  Great to keep your development database up to date.

Contents:

.. toctree::
   :maxdepth: 1

   installation
   configuration
   storage
   contributing

.. warning::
   django-dbbackup is currently under heavy refactoring, stay tuned for
   new versions and a final 2.0 release.

Compatibility
-------------

Django Database Backup supports PyPy, Python 2.7, 3.2 to 3.4 and Django greater than
1.6.
   
Management Commands
-------------------

dbbackup
~~~~~~~~
Backup your database to the specified storage. By default this
will backup all databases specified in your settings.py file and will not
delete any old backups. You can optionally specify a server name to be included
in the backup filename.

::

    dbbackup [-s <servername>] [-d <database>] [--clean] [--compress] [--encrypt] [--backup-extension <file-extension>]

dbrestore
~~~~~~~~~

Restore your database from the specified storage. By default
this will lookup the latest backup and restore from that. You may optionally
specify a servername if you you want to backup a database image that was
created from a different server. You may also specify an explicit local file to
backup from.

::

    dbrestore [-d <database>] [-s <servername>] [-f <localfile>] [--uncompress] [--backup-extension <file-extension>]

mediabackup
~~~~~~~~~~~~
Backup media files. Default this will backup the files in
the MEDIA_ROOT. Optionally you can set the DBBACKUP_MEDIA_PATH setting.

::

    mediabackup [--encrypt] [--clean] [--servername <servername>]

Examples
--------

If you run dbbackup out of the box, it will be able to create and restore from a
local file dump of your database as configured in your Django project's setup.

Here's how we create a simple dump of the database:

::

    $ python manage.py dbbackup
    
    Backing Up Database: /home/user/django-project/db.sqlite3
      Reading: /home/user/django-project/db.sqlite3
      Backup tempfile created: 38.0 KB
      Writing file to Filesystem: /home/user/django-project/, filename: default.backup


...and here's how we load that dump again (WARNING! Doing that of course overwrites the
entire existing database)

::

    $ python manage.py dbrestore 
    
    Restoring backup for database: /home/user/django-project/db.sqlite3
      Finding latest backup
      Restoring: /home/user/django-project/default.backup
      Restore tempfile created: 38.0 KB
    Are you sure you want to continue? [Y/n]y
      Writing: /home/user/django-project/db.sqlite3


Now, databases are not the only thing you should remember to backup. Your
``settings.MEDIA_ROOT`` is where user contributed uploads reside, and it
should also be backed up.

::

    $ python manage.py mediabackup
    
    Backing up media files
      Backup tempfile created: None (233.0 B)
      Writing file to Filesystem: /home/user/django-project/


MongoDB backup example (BETA)
-----------------------------

You can backup a mongodb database defined in your DATABASES settings.
::

    DATABASES['my_mongo'] = {
        'USER': 'dumper_user',
        'PASSWORD': '******',
        'ENGINE': 'django_mongodb_engine',
        'NAME': 'db_to_dump',
        'HOST': 'localhost',
        'PORT': '27017',
    }


::

    $ python manage.py dbbackup -d my_mongo

    Backing Up Database: db_to_dump
     Running: mongodump --username=dumper_user --password=****** --host=localhost --port=27017 -db db_to_dump -o /tmp/tmpxf8P7M
     Running: tar -C /tmp/tmpxf8P7M -cf - .
     Backup tempfile created: 10.0 KB
     Writing file to  Filesystem: /home/user/django-project/, filename: db_to_dump-2015-07-05-150629.tar


You can then restore the backup using the opposite command. (backup_extension currently have to be given)

::

    $ python manage.py dbrestore -d my_mongo

    Restoring backup for database: db_to_dump
      Finding latest backup
      Restoring: /home/user/django-project/db_to_dump-2015-07-05-150629.tar
      Restore tempfile created: 10.0 KB
    Are you sure you want to continue? [Y/n]Y
      Running: tar -C /tmp/tmpiaeb0O -x
      Running: mongorestore --username=dumper_user --password=****** --authenticationDatabase db_to_dump --host=localhost --port=27017 --objcheck --drop /tmp/tmpiaeb0O


Other Resources
===============

Source code here:

https://github.com/django-dbbackup/django-dbbackup

PyPi project:

https://pypi.python.org/pypi/django-dbbackup/



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
