Contributing guide
==================

Dbbackup is a free license software where all help are welcomed. This
documentation aims to help users or developers to bring their contributions
to this project.

Submit a bug, issue or enhancement
----------------------------------

All communication are made with `GitHub issues`_. Do not hesitate to open a
issue if:

- You have an improvement idea
- You found a bug
- You've got a question
- More generaly something seems wrong for you

.. _`GitHub issues`: https://github.com/django-dbbackup/django-dbbackup/issues

Make a patch
------------

We use `GitHub pull requests`_ for manage all patches. For a better handling
of requests we advise you to:

#. Fork the project and make a new branch
#. Make your changes with tests if possible and documentation if needed
#. Push changes to your fork repository and test it with Travis
#. If succeed, open a pull request
#. Upset us until we give you an answer

.. note::

    We advise you to launch it with Python 2 & 3 before push and try it in
    Travis. DBBackup uses a lot of file operations, so breaks between Python
    versions are easy.

.. _`GitHub pull requests`: https://github.com/django-dbbackup/django-dbbackup/pulls

Test environment
----------------

We provides tools for helps developers to quickly test and dev on DBBackup.
There are 2 majors scripts:

* ``runtests.py``: Unit tests launcher and equivalent of ``manage.py`` in
  the test project.
* ``functional.sh``: Shell script that use ``runtests.py`` to create a
  database backup and restore it, the same with media, and test if they are
  restored.


``runtests.py``
~~~~~~~~~~~~~~~

You can test code in local machine with the ``runtests.py`` script: ::

    python runtests.py

But if argument are provided, it acts as ``manage.py`` so you can simply
launch other command to test deeply, example: ::

    # Enter in Python shell
    python runtests.py shell

    # Launch a particular test module
    python runtests.py test dbbackup.tests.test_utils

All tests are stored in ``dbbackup.tests``.


``functional.sh``
~~~~~~~~~~~~~~~~~

It tests at the higher level if backup/restore mechanism is alright. It
becomes powerful because of the configuration you can give to it. See the next
chapter for explanation about it.

Configuration
~~~~~~~~~~~~~

DBBackup contains a test Django project at ``dbbackup.tests`` and its
``settings`` module. This configuration takes care of the following
environment variables:

**DB_ENGINE** - Default: ``django.db.backends.sqlite3``

Databank-Engine to use. See in django.db.backends for default backends.

**DB_NAME** - Default: ``:memory:``

Database name. Should be set correctly if an other db is used than sqlite3

**DB_USER** - Default: ``None``

DB Username

**DB_PASSWORD** - Default: ``None``

DB Password

**DB_HOST** - Default: ``None``

DB Host

Why is this more complicated than the earlier solution?
For mongodb tests dj-database-url had no ENGINE defined.


**MEDIA_ROOT** - Default= ``tempfile.mkdtemp()``

Django's ``MEDIA_ROOT``, useful if you want test media backup from filesystem

**STORAGE** - Default: ``dbbackup.tests.utils.FakeStorage``

Storage used for backups

**STORAGE_OPTIONS**

Options for instanciate the chosen storage. It must be in format
``"key1=foo,key2=bar"`` and will be convert into a ``dict``.

Online CI
---------

We use `Travis`_ for tests Dbbackup with a matrix of components' version: Several version of Django and several versions of Python including 2, 3 and PyPy.

.. image:: https://api.travis-ci.org/django-dbbackup/django-dbbackup.svg
        :target: https://travis-ci.org/django-dbbackup/django-dbbackup

Code coverage is ensured with `Coveralls`_ and has not yet minimum coverage limit.

.. image:: https://coveralls.io/repos/django-dbbackup/django-dbbackup/badge.svg?branch=master&service=github
        :target: https://coveralls.io/github/django-dbbackup/django-dbbackup?branch=master

Code health is checked with `Landscape`_

.. image:: https://landscape.io/github/django-dbbackup/django-dbbackup/master/landscape.svg?style=flat
        :target: https://landscape.io/github/django-dbbackup/django-dbbackup/master
        :alt: Code Health

.. _Travis: https://travis-ci.org/django-dbbackup/django-dbbackup
.. _Coveralls: https://coveralls.io/github/django-dbbackup/django-dbbackup
.. _`Landscape`: https://landscape.io/github/django-dbbackup/django-dbbackup/
