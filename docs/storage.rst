Remote storage
==============

django-dbbackup comes with a variety of remote storage options. If you wish
to build your own, extend ``dbbackup.storage.base.BaseStorage`` and point 
your ``settings.DBBACKUP_STORAGE`` to ``'my_storage.backend.ClassName'``.

Local disk
----------

To store your database backups on the local filesystem, simply setup the
required settings below. Storing backups to local disk may also be
useful for Dropbox if you already have the offical Dropbox client
installed on your system.


Available Settings
~~~~~~~~~~~~~~~~~~

**DBBACKUP\_BACKUP\_DIRECTORY (optional)** - The directory on your local
system you wish to save your backups. Default: Current working
directory.


Amazon S3
---------

In order to backup to Amazon S3, you'll first need to create an Amazon
Webservices Account and setup your Amazon S3 bucket. Once that is
complete, you can follow the required setup below.

Setup Your Django Project
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install boto

Add the following to your project's settings:

::

    DBBACKUP_STORAGE = 'dbbackup.storage.s3_storage'
    DBBACKUP_S3_BUCKET = '<amazon_bucket_name>'
    DBBACKUP_S3_ACCESS_KEY = '<amazon_access_key>'
    DBBACKUP_S3_SECRET_KEY = '<amazon_secret_key>'


Available Settings
~~~~~~~~~~~~~~~~~~

**DBBACKUP\_S3\_BUCKET (required)** - The name of the Amazon S3 bucket
to store your backups. This directory must exist before attempting to
create your first backup.

**DBBACKUP\_S3\_ACCESS\_KEY (required)** - Your Amazon Account Access
Key. This can be found on your Amazon Account Security Credentials page.
Note: Do not share this key with anyone you do not trust with access to
your Amazon files.

**DBBACKUP\_S3\_SECRET\_KEY (required)** - Your Amazon Account Secret
Key. This can be found in the same location as your Access Key above.

**DBBACKUP\_S3\_DIRECTORY (optional)** - The directory in your Amazon S3
bucket you wish to save your backups. By default this is set to
'django-dbbackups/'.

**DBBACKUP\_S3\_DOMAIN (optional)** - Specify the Amazon domain to use
when transferring the generated backup files. For example, this can be
set to 's3-eu-west-1.amazonaws.com'. By default, this is
's3.amazonaws.com'.

**DBBACKUP\_S3\_IS\_SECURE (optional)** - Set False to disable using
SSL. Default is True.

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
    DBBACKUP_TOKENS_FILEPATH = '<local_tokens_filepath>'
    DBBACKUP_DROPBOX_APP_KEY = '<dropbox_app_key>'
    DBBACKUP_DROPBOX_APP_SECRET = '<dropbox_app_secret>'


FTP
---

To store your database backups on the remote filesystem via FTP, simply
setup the required settings below.

Setup Your Django Project
~~~~~~~~~~~~~~~~~~~~~~~~~

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

**DBBACKUP\_FTP\_HOST (required)** - Hostname for the server you wish to
save your backups.

**DBBACKUP\_FTP\_USER, DBBACKUP\_FTP\_PASSWORD** - FTP authorization
credentionals. Skip for anonymous FTP.

**DBBACKUP\_FTP\_PATH** - The directory on remote FTP server you wish to
save your backups.
