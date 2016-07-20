========
Commands
========

The primary usage of DBBackup is made with command line tools. By default,
commands will create backups and upload to your defined storage or download
and restore the latest.

dbbackup
========

dbrestore
=========

mediabackup
===========

Backup media files, gather all in a tarball and encrypt or compress. :: 

    $ ./manage.py mediabackup
    Backup size: 10.0 KiB
    Writing file to zuluvm-2016-07-04-081612.tar

mediarestore
============

Restore media files, extract files from archive and put into media storage. ::

    $ ./manage.py mediarestore
    Restoring backup for media files
    Finding latest backup
    Reading file zuluvm-2016-07-04-082551.tar
    Restoring: zuluvm-2016-07-04-082551.tar
    Backup size: 10.0 KiB
    Are you sure you want to continue? [Y/n]
    2 file(s) restored

listbackups
===========
