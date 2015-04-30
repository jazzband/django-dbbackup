Installation
============

Installing on your system
-------------------------

Getting the latest stable release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    pip install django-dbbackup

Getting the latest release from trunk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general, you should not be downloading and installing stuff
directly off repositories -- especially not if you are backing
up sensitive data.

Security is important, bypassing PyPi repositories is a bad habbit,
because it will bypass the fragile key signatures authentication
that are at least present when using PyPi repositories.

::

    pip install -e git+https://github.com/mjs7231/django-dbbackup.git#egg=django-dbbackup


Adding in your project
----------------------

In your ``settings.INSTALLED_APPS``, make sure you have the following:

    INSTALLED_APPS = (
        ...
        'dbbackup',  # django-dbbackup
    )

Testing that everything worked
------------------------------

Now, you should be able to create your first backup by running:

::

    $ python manage.py dbbackup

If your database was called ``default`` which is the normal Django behaviour
of a single-database project, you should now see a new file ``default.backup``.

