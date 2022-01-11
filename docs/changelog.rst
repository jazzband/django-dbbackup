Changelog
=========

4.0.0b0 (2021-12-19)
--------------------

* Fix RemovedInDjango41Warning related to default_app_config `#413`_
* Add authentication database support for MongoDB `#379`_
* Remove six dependency `#371`_
* Explicitly support Python 3.6+. `#408`_
* Drop support for end of life Django versions. Currently support 2.2, 3.2, 4.0. `#408`_
* Replace ugettext_lazy with gettext_lazy `#342`_
* Changed logging settings from settings.py to late init `#332`_
* Fix authentication error when postgres is password protected `#361`_
* Use exclude-table-data instead of exclude-table `#363`_
* Add support for exclude tables data in the command interface `#375`_
* Move author and version information into setup.py to allow building package in isolated
  environment (e.g. with the ``build`` package). `#414`_
* Documentation fixes `#341`_ `#333`_ `#349`_ `#348`_ `#337`_ `#411`_


3.3.0 (2020-04-14)
------------------

* Documentation fixes `#341`_ `#333`_ `#328`_ `#320`_ `#305`_ `#303`_ `#302`_ `#298`_ `#281`_ `#266`_ `#349`_ `#348`_ `#337`_
* "output-filename" in mediabackup command `#324`_
* Fixes for test infrastructure and mongodb support `#318`_
* sqlite3: don't throw warnings if table already exists `#317`_
* Fixes for django3 and updated travis (and File handling) `#316`_
* Restoring from FTP `#313`_
* Fixes to run dbbackup management command in Postgres for non-latin Windows. `#273`_
* Apply changes from pull request 244; Update to include sftp storage `#280`_
* Quick fix for proper selection of DB name to restore `#260`_

.. _`#342`: https://github.com/django-dbbackup/django-dbbackup/pull/342
.. _`#332`: https://github.com/django-dbbackup/django-dbbackup/pull/332
.. _`#361`: https://github.com/django-dbbackup/django-dbbackup/pull/361
.. _`#363`: https://github.com/django-dbbackup/django-dbbackup/pull/363
.. _`#375`: https://github.com/django-dbbackup/django-dbbackup/pull/375
.. _`#341`: https://github.com/django-dbbackup/django-dbbackup/pull/341
.. _`#333`: https://github.com/django-dbbackup/django-dbbackup/pull/333
.. _`#328`: https://github.com/django-dbbackup/django-dbbackup/pull/328
.. _`#320`: https://github.com/django-dbbackup/django-dbbackup/pull/320
.. _`#305`: https://github.com/django-dbbackup/django-dbbackup/pull/305
.. _`#303`: https://github.com/django-dbbackup/django-dbbackup/pull/303
.. _`#302`: https://github.com/django-dbbackup/django-dbbackup/pull/302
.. _`#298`: https://github.com/django-dbbackup/django-dbbackup/pull/298
.. _`#281`: https://github.com/django-dbbackup/django-dbbackup/pull/281
.. _`#266`: https://github.com/django-dbbackup/django-dbbackup/pull/266
.. _`#324`: https://github.com/django-dbbackup/django-dbbackup/pull/324
.. _`#318`: https://github.com/django-dbbackup/django-dbbackup/pull/318
.. _`#317`: https://github.com/django-dbbackup/django-dbbackup/pull/317
.. _`#316`: https://github.com/django-dbbackup/django-dbbackup/pull/316
.. _`#313`: https://github.com/django-dbbackup/django-dbbackup/pull/313
.. _`#273`: https://github.com/django-dbbackup/django-dbbackup/pull/273
.. _`#280`: https://github.com/django-dbbackup/django-dbbackup/pull/280
.. _`#260`: https://github.com/django-dbbackup/django-dbbackup/pull/260
.. _`#349`: https://github.com/django-dbbackup/django-dbbackup/pull/349
.. _`#348`: https://github.com/django-dbbackup/django-dbbackup/pull/348
.. _`#337`: https://github.com/django-dbbackup/django-dbbackup/pull/337
.. _`#408`: https://github.com/django-dbbackup/django-dbbackup/pull/408
.. _`#371`: https://github.com/django-dbbackup/django-dbbackup/pull/371
.. _`#379`: https://github.com/django-dbbackup/django-dbbackup/pull/379
.. _`#411`: https://github.com/django-dbbackup/django-dbbackup/pull/411
.. _`#413`: https://github.com/django-dbbackup/django-dbbackup/pull/413
.. _`#414`: https://github.com/django-dbbackup/django-dbbackup/pull/414
