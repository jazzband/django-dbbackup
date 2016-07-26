Storage
=======

django-dbbackup comes with a variety of remote storage options and it can deal
with Django Storage API for extend its possibilities.

You can choose your storage backend by set ``settings.DBBACKUP_STORAGE``,
it must point to module containing the chosen Storage class. For example:
``dbbackup.storage.filesystem_storage`` for use file system storage.
Below, we'll list some of the available solutions and their options.

Storage's option are gathered in ``settings.DBBACKUP_STORAGE_OPTIONS`` which
is a dictionary of keywords representing how to configure it.

.. note::

    A lot of changes has been made for use Django Storage API as primary source of
    backends and due to this task, some settings has been deprecated but always
    functionnal until removing. Please take care of notes and warnings in this
    documentation and at your project's launching.

.. warning::

    Do not configure backup storage with the same configuration than your media
    files, you'll risk to share backups inside public directories.

Local disk
----------

Dbbackup uses `built-in file system storage`_ to manage files on a local
directory.

.. _`built-in file system storage`: https://docs.djangoproject.com/en/1.8/ref/files/storage/#the-filesystemstorage-class

.. note::

    Storing backups to local disk may also be useful for Dropbox if you
    already have the offical Dropbox client installed on your system.

Setup
~~~~~

To store your backups on the local file system, simply setup the
required settings below.

::

    DBBACKUP_STORAGE = 'dbbackup.storage.filesystem_storage'
    DBBACKUP_STORAGE_OPTIONS = {'location': '/my/backup/dir/'}



Available Settings
~~~~~~~~~~~~~~~~~~

**location** - Default: Current working directory (``os.getcwd``)

Absolute path to the directory that will hold the files.

.. warning::

    ``settings.DBBACKUP_BACKUP_DIRECTORY`` was used before but is deprecated.
    Backup location must no be in ``settings.MEDIA_ROOT``, it will raise an
    ``StorageError`` if ``settings.DEBUG`` is ``False`` else a warning.

**file_permissions_mode** - Default: ``settings.FILE_UPLOAD_PERMISSIONS``

The file system permissions that the file will receive when it is saved. 


Amazon S3
---------

Our S3 backend uses Django Storage Redux which uses `boto`_.

.. _`boto`: http://docs.pythonboto.org/en/latest/#

Setup
~~~~~

In order to backup to Amazon S3, you'll first need to create an Amazon
Webservices Account and setup your Amazon S3 bucket. Once that is
complete, you can follow the required setup below.

::

    pip install boto django-storages-redux

Add the following to your project's settings:

::

    DBBACKUP_STORAGE = 'dbbackup.storage.s3_storage'
    DBBACKUP_STORAGE_OPTIONS = {
        'access_key': 'my_id',
        'secret_key': 'my_secret',
        'bucket_name': 'my_bucket_name'
    }

Available Settings
~~~~~~~~~~~~~~~~~~

.. note::

    More settings are available but without clear official documentation about
    it, you can refer to `source code`_ and look at ``S3BotoStorage``'s
    attributes.

.. _`source code`: https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto.py#L204

**access_key** - Required

Your AWS access key as string. This can be found on your `Amazon Account
Security Credentials page`_.

.. _`Amazon Account Security Credentials page`: https://console.aws.amazon.com/iam/home#security_credential

.. note::

    ``settings.DBBACKUP_S3_ACCESS_KEY`` was used before but is deprecated.

**secret_key** - Required

Your Amazon Web Services secret access key, as a string.

.. note::

    ``settings.DBBACKUP_S3_SECRET_KEY`` was used before but is deprecated.

**bucket_name** - Required

Your Amazon Web Services storage bucket name, as a string. This directory must
exist before attempting to create your first backup.

.. note::

    ``settings.DBBACKUP_S3_BUCKET`` was used before but is deprecated.

**host** - Default: ``'s3.amazonaws.com'`` (``boto.s3.connection.S3Connection.DefaultHost``)

Specify the Amazon domain to use when transferring the generated backup files.
For example, this can be set to ``'s3-eu-west-1.amazonaws.com'``.

.. note::

    ``settings.DBBACKUP_S3_DOMAIN`` was used before but is deprecated.

**use_ssl** - Default: ``True``

.. note::

    ``settings.DBBACKUP_S3_IS_SECURE`` was used before but is deprecated.

**default_acl** - Required

If bucket doesn't exist, it will be created with the given ACL.

.. warning::

    The default ACL is `'public-read'`, please take care of this possible
    security issue.

Dropbox
-------

In order to backup to Dropbox, you'll first need to create a Dropbox
Account and set it up to communicate with the Django-DBBackup
application. Don't worry, all instructions are below.

Setup Your Dropbox Account
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Login to Dropbox and navigate to Developers » MyApps.
   https://www.dropbox.com/developers/start/setup#python

2. Click the button to create a new app and name it whatever you like.
   For reference, I named mine 'Website Backups'.

3. After your app is created, note the options button and more
   importantly the 'App Key' and 'App Secret' values inside. You'll need
   those later.

Setup Your Django Project
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install dropbox

...And make sure you have the following required project settings:

::

    DBBACKUP_STORAGE = 'dbbackup.storage.dropbox_storage'


    Then this:

    DBBACKUP_TOKENS_FILEPATH = '<local_tokens_filepath>'
    DBBACKUP_DROPBOX_APP_KEY = '<dropbox_app_key>'
    DBBACKUP_DROPBOX_APP_SECRET = '<dropbox_app_secret>'


    Or:
    DROPBOX_ACCESS_TOKEN = **************

FTP
---

To store your database backups on the remote filesystem via FTP, simply
setup the required settings below.

Setup Your Django Project
~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    This storage will be updated for use Django Storage's one.

.. warning::

    This storage doesn't use private connection for communcation, don't use it
    if you're not sure about the link between client and server.

Using FTP does not require any external libraries to be installed, simply
use the below project settings:

::

    DBBACKUP_STORAGE = 'dbbackup.storage.ftp_storage'
    DBBACKUP_FTP_HOST = 'ftp.host'
    DBBACKUP_FTP_USER = 'user, blank if anonymous'
    DBBACKUP_FTP_PASSWORD = 'password, can be blank'
    DBBACKUP_FTP_PATH = 'path, blank for default'

Available Settings
~~~~~~~~~~~~~~~~~~

**DBBACKUP\_FTP\_HOST** -  Required

Hostname for the server you wish to save your backups.

**DBBACKUP\_FTP\_USER** - Default: ``None``

Authentication login, do not use if anonymous.

**DBBACKUP\_FTP\_PASSWORD** - Default: ``None``

Authentication password, do not use if there's no password.

**DBBACKUP\_FTP\_PATH** - Default: ``'.'``

The directory on remote FTP server you wish to save your backups.

.. note::

    As other updated storages, this settings will be deprecated in favor of
    dictionary ``settings.DBBACKUP_STORAGE_OPTIONS``.

Django built-in storage API
---------------------------

Django has its own storage API for managing media files. Dbbackup allows
you to use (third-part) Django storage backends. The default backend is
``FileSystemStorage``, which is integrated in Django but we invite you
to take a look at `django-storages-redux`_ which has a great collection of
storage backends.

.. _django-storages-redux: https://github.com/jschneier/django-storages

Setup using built-in storage API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use Django's built-in `FileSystemStorage`_, add the following lines to
your ``settings.py``::

    DBBACKUP_STORAGE = 'dbbackup.storage.builtin_django'
    # Default
    # DBBACKUP_DJANGO_STORAGE = 'django.core.file.storages.FileSystemStorage'
    DBBACKUP_STORAGE_OPTIONS = {'location': '/mybackupdir/'}

.. _FileSystemStorage: https://docs.djangoproject.com/en/1.8/ref/files/storage/#the-filesystemstorage-class

``'dbbackup.storage.builtin_django'`` is a wrapper for use the Django storage
defined in ``DBBACKUP_DJANGO_STORAGE`` with the options defined in 
``DBBACKUP_STORAGE_OPTIONS``.

Used settings
~~~~~~~~~~~~~

**DBBACKUP_DJANGO_STORAGE** - Default: ``'django.core.file.storages.FileSystemStorage'``

Path to a Django Storage class (in Python dot style).

.. warning::

    Do not use a Django storage backend without configuring its options,
    otherwise you will risk mixing media files (with public access) and
    backups (strictly private).

**DBBACKUP_STORAGE_OPTIONS** - Default: ``{}``

Dictionary used to instantiate a Django Storage class. For example, the
``location`` key customizes the directory for ``FileSystemStorage``.

Write your custom storage
-------------------------

If you wish to build your own, extend ``dbbackup.storage.base.BaseStorage``
and point your ``settings.DBBACKUP_STORAGE`` to
``'my_storage.backend.ClassName'``.
