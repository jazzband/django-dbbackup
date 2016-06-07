Configuration
=============

General settings
----------------

DBBACKUP_DATABASES
~~~~~~~~~~~~~~~~~~

List of key entries for ``settings.DATABASES`` which shall be used to
connect and create database backups.

Default: ``list(settings.DATABASES.keys())`` (keys of all entries listed)

DBBACKUP_BACKUP_DIRECTORY
~~~~~~~~~~~~~~~~~~~~~~~~~

Where to store backups. String pointing to django-dbbackup
location module to use when performing a backup.

Default: ``os.getcwd()`` (Current working directory)

DBBACKUP_TMP_DIR
~~~~~~~~~~~~~~~~

Directory to be used for temporary files.

Default: ``tempfile.gettempdir()``

DBBACKUP_TMP_FILE_MAX_SIZE
~~~~~~~~~~~~~~~~~~~~~~~~~~

Maximum size in bytes for file handling in memory before write a temporary
file on ``DBBACKUP_TMP_DIR``.

Default: ``10*1024*1024``


DBBACKUP_CLEANUP_KEEP and DBBACKUP_CLEANUP_KEEP_MEDIA
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When issueing ``dbbackup`` and ``mediabackup``, old backup files are
looked for and removed.

Default: ``10`` (days)

DBBACKUP_MEDIA_PATH
~~~~~~~~~~~~~~~~~~~

Default: settings.MEDIA_ROOT

DBBACKUP_DATE_FORMAT
~~~~~~~~~~~~~~~~~~~~

Date format to use for naming files. It must contain only alphanumerical
characters, ``'_'``, ``'-'`` or ``'%'``.

Default: ``'%Y-%m-%d-%H%M%S'``

DBBACKUP_FILENAME_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~

The template to use when generating the backup filename. By default this is
``'{databasename}-{servername}-{datetime}.{extension}'``. This setting can
also be made a function which takes the following keyword arguments:

::

    def backup_filename(databasename, servername, datetime, extension):
        pass

    DBBACKUP_FILENAME_TEMPLATE = backup_filename

This allows you to modify the entire format of the filename, for example, if
you want to take advantage of Amazon S3's automatic expiry feature, you need
to prefix your backups differently based on when you want them to expire.

``{datetime}`` is rendered with ``DBBACKUP_DATE_FORMAT``.

DBBACKUP_MEDIA_FILENAME_TEMPLATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Same as ``DBBACKUP_FILENAME_TEMPLATE`` but for media files backups.


DBBACKUP_SEND_EMAIL
~~~~~~~~~~~~~~~~~~~

Controls whether or not django-dbbackup sends an error email when an uncaught
exception is received.

Default: ``True``

DBBACKUP_HOSTNAME
~~~~~~~~~~~~~~~~~

Hostname needed by django-dbbackup's uncaught exception email sender for
well described error reporting. If you are using ``ALLOWED_HOSTS`` you should
set ``DBBACKUP_HOSTNAME`` to any host from ``ALLOWED_HOSTS`` setting. Otherwise
django-dbbackup can not send email to the ``SERVER_EMAIL``.

Default: ``socket.gethostname()``

.. note::

    Previously ``DBBACKUP_FAKE_HOST`` was used for this setting.

**DBBACKUP\_CLEANUP\_KEEP (optional)** - The number of backups to keep
when specifying the --clean flag. Defaults to keeping 10 + the first
backup of each month.

Encrypting your backups
=======================

Considering that you might be putting secured data on external servers and
perhaps untrusted servers where it gets forgotten over time, it's always a
good idea to encrypt backups.

Just remember to keep the encryption keys safe, too!


PGP
---

You can encrypt a backup with the ``--encrypt`` option. The backup is done
using gpg.

::

    python manage.py dbbackup --encrypt

...or when restoring from an encrypted backup:

::

    python manage.py dbrestore --decrypt


Requirements:

-  Install the python package python-gnupg:
   ``pip install python-gnupg``.
-  You need gpg key.
-  Set the setting 'DBBACKUP\_GPG\_RECIPIENT' to the name of the gpg
   key.

DBBACKUP_GPG_ALWAYS_TRUST
~~~~~~~~~~~~~~~~~~~~~~~~~

The encryption of the backup file fails if gpg does not trust the public
encryption key. The solution is to set the option 'trust-model' to 'always'.
By default this value is ``False``. Set this to ``True`` to enable this option.

DBBACKUP_GPG_RECIPIENT
~~~~~~~~~~~~~~~~~~~~~~

The name of the key that is used for encryption. This setting is only used
when making a backup with the ``--encrypt`` or ``--decrypt`` option.

Database configuration
======================

By default, DBBackup uses parameters from ``settings.DATABASES`` but you can
make an independant configuration, see `Database settings`_

Storage configuration
=====================

You have to use a storage for your backups, see `Storage settings`_ for more.

.. _`Database settings`: /databases.html
.. _`Storage settings`: /storage.html
