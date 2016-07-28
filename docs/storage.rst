Storage
=======

One of the most helpful feature of django-dbbackup is the avaibility to store
and retrieve backups from a local or remote storage. This functionality is
mainly based on Django Storage API and extend its possibilities.

You can choose your backup storage backend by set ``settings.DBBACKUP_STORAGE``,
it must be a full path of a storage class. For example:
``django.core.files.storage.FileSystemStorage`` for use file system storage.
Below, we'll list some of the available solutions and their options.

Storage's option are gathered in ``settings.DBBACKUP_STORAGE_OPTIONS`` which
is a dictionary of keywords representing how to configure it.

.. warning::

    Do not configure backup storage with the same configuration than your media
    files, you'll risk to share backups inside public directories.

DBBackup uses by default the `built-in file system storage`_ to manage files on
a local directory. Feel free to use any Django storage, you can find a variety
of them at `Django Packages`_.

.. _`built-in file system storage`: https://docs.djangoproject.com/en/1.8/ref/files/storage/#the-filesystemstorage-class
.. _`Django Packages`: https://djangopackages.org/grids/g/storage-backends/

.. note::

    Storing backups to local disk may also be useful for Dropbox if you
    already have the offical Dropbox client installed on your system.

File system storage
-------------------

Setup
~~~~~

To store your backups on the local file system, simply setup the required
settings below. ::

    DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
    DBBACKUP_STORAGE_OPTIONS = {'location': '/my/backup/dir/'}


Available settings
~~~~~~~~~~~~~~~~~~

**location** 

Absolute path to the directory that will hold the files.

**base_url** 

URL that serves the files stored at this location.

**file_permissions_mode**

The file system permissions that the file will receive when it is saved.

**directory_permissions_mode**

The file system permissions that the directory will receive when it is saved.

See `FileSystemStorage's documentation`_ for a full list of available settings.

.. _`FileSystemStorage's documentation`: https://docs.djangoproject.com/en/1.9/ref/files/storage/#the-filesystemstorage-class

Amazon S3
---------

Our S3 backend uses Django Storages which uses `boto`_.

.. _`boto`: http://docs.pythonboto.org/en/latest/#

Setup
~~~~~

In order to backup to Amazon S3, you'll first need to create an Amazon
Webservices Account and setup your Amazon S3 bucket. Once that is
complete, you can follow the required setup below. ::

    pip install boto django-storages

Add the following to your project's settings: ::

    DBBACKUP_STORAGE = 'storages.backends.s3boto.S3BotoStorageFile'
    DBBACKUP_STORAGE_OPTIONS = {
        'access_key': 'my_id',
        'secret_key': 'my_secret',
        'bucket_name': 'my_bucket_name'
    }

Available settings
~~~~~~~~~~~~~~~~~~

.. note::

    More settings are available see `official documentation`_ for get more about.

.. _`official documentation`: https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html

**access_key** - Required

Your AWS access key as string. This can be found on your `Amazon Account
Security Credentials page`_.

.. _`Amazon Account Security Credentials page`: https://console.aws.amazon.com/iam/home#security_credential

**secret_key** - Required

Your Amazon Web Services secret access key, as a string.

**bucket_name** - Required

Your Amazon Web Services storage bucket name, as a string. This directory must
exist before attempting to create your first backup.

**host** - Default: ``'s3.amazonaws.com'`` (``boto.s3.connection.S3Connection.DefaultHost``)

Specify the Amazon domain to use when transferring the generated backup files.
For example, this can be set to ``'s3-eu-west-1.amazonaws.com'``.

**use_ssl** - Default: ``True``


**default_acl** - Required

See `Django Storage S3 storage official documentation`_ for more informations
about available settings.

.. _`Django Storage S3 storage official documentation`: http://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html


Dropbox
-------

In order to backup to Dropbox, you'll first need to create a Dropbox account
and set it up to communicate with the Django-DBBackup application. Don't
worry, all instructions are below.

Setup your Dropbox account
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Login to Dropbox and navigate to Developers » MyApps.
   https://www.dropbox.com/developers/start/setup#python

2. Click the button to create a new app and name it whatever you like.
   For reference, I named mine 'Website Backups'.

3. After your app is created, note the options button and more
   importantly the 'App Key' and 'App Secret' values inside. You'll need
   those later.

Setup your Django project
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install dropbox django-storages

...And make sure you have the following required project settings: ::


    DBBACKUP_STORAGE = 'storages.backends.dropbox.DropBoxStorage
    DBBACKUP_STORAGE_OPTIONS = {
        'oauth2_access_token': 'my_token',
    }

Available settings
~~~~~~~~~~~~~~~~~~

.. note::

    See `django-storages dropbox official documentation`_ for get more details about.

.. _`django-storages dropbox official documentation`: https://django-storages.readthedocs.io/en/latest/backends/dropbox.html

**oauth2_access_token** - Required

Your OAuth access token

**root_path**

Jail storage to this directory

FTP
---

To store your database backups on a remote filesystem via [a]FTP, simply
setup the required settings below.

Setup
~~~~~
::

    pip install django-storages


.. warning::

    This storage doesn't use private connection for communcation, don't use it
    if you're not sure about the link between client and server.

::

    DBBACKUP_STORAGE = 'storages.backends.ftp.FTPStorage
    DBBACKUP_STORAGE_OPTIONS = {
        'location': 'ftp://user:pass@server:21'
    }

Settings
~~~~~~~~

**location** -  Required

A FTP URI with optional user, password and port. example: ``'ftp://anonymous@myftp.net'``

**base_url**

URL that serves with HTTP(S) the files stored at this location.

Setup
~~~~~

We use FTP backend from Django-Storages (again). ::

    pip install django-storages

Here a simple configuration: ::

    DBBACKUP_STORAGE = 'storages.backends.ftp.FTPStorage'
    DBBACKUP_STORAGE_OPTIONS = {'location': ftp://myftpserver>/}

SFTP
----

To store your database backups on a remote filesystem via SFTP, simply
setup the required settings below.

Setup
~~~~~

This backend is from Django-Storages with `paramiko`_ under. ::

    pip install paramiko django-storages

.. _`paramiko`: http://www.paramiko.org/ 

The next configuration admit SSH server grant a the local user: ::

    DBBACKUP_STORAGE = 'storages.backends.sftpstorage.SFTPStorage'
    DBBACKUP_STORAGE_OPTIONS = {'host': 'myserver'}


.. _`paramiko SSHClient.connect() documentation`: http://docs.paramiko.org/en/latest/api/client.html#paramiko.client.SSHClient.connect

Available settings
~~~~~~~~~~~~~~~~~~

**host** - Required

Hostname or adress of the SSH server

**root_path** - Default ``~/``

Jail storage to this directory

**params** - Default ``{}``

Arugment used by meth:`paramikor.SSHClient.connect()`.
See `paramiko SSHClient.connect() documentation`_ for details.

**interactive** - Default ``False``

A boolean indicating whether to prompt for a password if the connection cannot
be made using keys, and there is not already a password in ``params``.

**file_mode**

UID of the account that should be set as owner of the files on the remote.

**dir_mode**

GID of the group that should be set on the files on the remote host.

**known_host_file**

Absolute path of know host file, if it isn't set ``"~/.ssh/known_hosts"`` will be used.
