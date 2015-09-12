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

.. _`GitHub pull requests`: https://github.com/django-dbbackup/django-dbbackup/pulls

Test code
~~~~~~~~~

You can test your code in local machine with the ``runtests.py`` script:

::

    cd tests
    python runtests.py

We advise you to launch it with Python 2 & 3 before push and try it in Travis.

Online CI
---------

We use `Travis`_ for tests Dbbackup with a matrix of components' version: Several version of Django and several versions of Python including 2, 3 and PyPy.

.. image:: https://api.travis-ci.org/django-dbbackup/django-dbbackup.svg
        :target: https://travis-ci.org/django-dbbackup/django-dbbackup

Code coverage is ensured with `Coveralls`_ and has not yet minimum coverage limit.

.. image:: https://coveralls.io/repos/django-dbbackup/django-dbbackup/badge.svg?branch=master&service=github
        :target: https://coveralls.io/github/django-dbbackup/django-dbbackup?branch=master

.. _Travis: https://travis-ci.org/django-dbbackup/django-dbbackup
.. _Coveralls: https://coveralls.io/github/django-dbbackup/django-dbbackup
