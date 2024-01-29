Changelog
=========

Unreleased
----------

* Nothing (yet)!

4.1.0 (2024-01-14)
------------------

* Fix restore fail after editing filename by @stan-levend in https://github.com/jazzband/django-dbbackup/pull/465
* Drop python 3.6 by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/472
* update links by @Arhell in https://github.com/jazzband/django-dbbackup/pull/471
* Update doc for backup directory consistency by @jej in https://github.com/jazzband/django-dbbackup/pull/473
* RESTORE_PREFIX for RESTORE_SUFFIX by @mativs in https://github.com/jazzband/django-dbbackup/pull/469
* Support Django 4.1, 4.2 and Python 3.11 by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/485
* Support Python 3.12 and Django 5.0 by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/499
* v4.1.0 by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/500

4.0.2 (2022-09-27)
------------------

* Docs: Fix removed host option, explain new options by @bittner in https://github.com/jazzband/django-dbbackup/pull/333
* dbbackup.db.postgres typo fix by @LeeHanYeong in https://github.com/jazzband/django-dbbackup/pull/341
* Replace ugettext_lazy with gettext_lazy by @sumanthratna in https://github.com/jazzband/django-dbbackup/pull/342
* Fix broken link by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/349
* Remove base_url in docs as it's not used by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/348
* Update commands.rst to add missing command by @sumit4613 in https://github.com/jazzband/django-dbbackup/pull/337
* Add changelog by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/351
* Add documentation for django-storage by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/352
* Fix headings for changelog by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/354
* Changed logging settings from settings.py to late init by @asaf-kali in https://github.com/jazzband/django-dbbackup/pull/332
* Drop django 1.11 and python 2.7 by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/353
* Fix authentication error when postgres is password protected by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/361
* using exclude-table-data instead by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/363
* Add some issue templates by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/366
* Replace travis with github actions by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/368
* 'six' package dependency removed by @jerinpetergeorge in https://github.com/jazzband/django-dbbackup/pull/371
* Add support for exclude tables data in the command interface by @KessoumML in https://github.com/jazzband/django-dbbackup/pull/375
* Make the binary connector the default by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/339
* Env password is no longer used since #361 by @jonathan-s in https://github.com/jazzband/django-dbbackup/pull/362
* auth source added in mongodb. authentication issue fixed with mongodb… by @Ajaysainisd in https://github.com/jazzband/django-dbbackup/pull/379
* Add support for Python 3.9-3.10 and Django 3.2 by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/401
* Update CHANGELOG by @sumanthratna in https://github.com/jazzband/django-dbbackup/pull/376
* Clean up README by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/407
* Add support for Django 4.0 by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/408
* Update changelog for PRs merged since 3.3.0 release by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/410
* Include long description in package metadata by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/411
* Add build environment by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/412
* Fix RemovedInDjango41Warning related to default_app_config by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/413
* Release 4.0.0b0 by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/414
* Fix GitHub Actions configuration by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/419
* Enable functional tests in CI by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/420
* Update settings.py comment by @aaronvarghese in https://github.com/jazzband/django-dbbackup/pull/427
* Jazzband transfer tasks by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/418
* Add Jazzband contributing guidelines by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/435
* Create release CI by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/436
* Fix docs build and URLs by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/437
* Refactoring and tooling by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/438
* Include package data to fix docs and pypi by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/440
* Set package as not zip_safe by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/441
* Fix manifest warning by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/442
* Move VERSION source directory by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/443
* Correct spelling mistakes by @EdwardBetts in https://github.com/jazzband/django-dbbackup/pull/447
* Correct grammar in Docs and ReadMe by @millerthegorilla in https://github.com/jazzband/django-dbbackup/pull/448
* fix GPG manual anchor and typo by @millerthegorilla in https://github.com/jazzband/django-dbbackup/pull/449
* v4.0.1 by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/453
* support for prometheus wrapped dbs by @tsundokum in https://github.com/jazzband/django-dbbackup/pull/455
* Backup of SQLite fail if there are Virtual Tables (e.g. FTS tables). by @xbello in https://github.com/jazzband/django-dbbackup/pull/458
* Closes #460: python-gnupg version increase breaks unencrypt_file func… by @chambersh1129 in https://github.com/jazzband/django-dbbackup/pull/461
* v4.0.2 by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/462

4.0.1 (2022-07-09)
---------------------

* As of this version, dbbackup is now within Jazzband! This version tests our Jazzband release CI, and adds miscellaneous refactoring/cleanup.
* Fix GitHub Actions configuration by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/419
* Enable functional tests in CI by @johnthagen in https://github.com/jazzband/django-dbbackup/pull/420
* Update settings.py comment by @aaronvarghese in https://github.com/jazzband/django-dbbackup/pull/427
* Jazzband transfer tasks by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/418
* Refactoring and tooling by @Archmonger in https://github.com/jazzband/django-dbbackup/pull/438

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

.. _`#342`: https://github.com/jazzband/django-dbbackup/pull/342
.. _`#332`: https://github.com/jazzband/django-dbbackup/pull/332
.. _`#361`: https://github.com/jazzband/django-dbbackup/pull/361
.. _`#363`: https://github.com/jazzband/django-dbbackup/pull/363
.. _`#375`: https://github.com/jazzband/django-dbbackup/pull/375
.. _`#341`: https://github.com/jazzband/django-dbbackup/pull/341
.. _`#333`: https://github.com/jazzband/django-dbbackup/pull/333
.. _`#328`: https://github.com/jazzband/django-dbbackup/pull/328
.. _`#320`: https://github.com/jazzband/django-dbbackup/pull/320
.. _`#305`: https://github.com/jazzband/django-dbbackup/pull/305
.. _`#303`: https://github.com/jazzband/django-dbbackup/pull/303
.. _`#302`: https://github.com/jazzband/django-dbbackup/pull/302
.. _`#298`: https://github.com/jazzband/django-dbbackup/pull/298
.. _`#281`: https://github.com/jazzband/django-dbbackup/pull/281
.. _`#266`: https://github.com/jazzband/django-dbbackup/pull/266
.. _`#324`: https://github.com/jazzband/django-dbbackup/pull/324
.. _`#318`: https://github.com/jazzband/django-dbbackup/pull/318
.. _`#317`: https://github.com/jazzband/django-dbbackup/pull/317
.. _`#316`: https://github.com/jazzband/django-dbbackup/pull/316
.. _`#313`: https://github.com/jazzband/django-dbbackup/pull/313
.. _`#273`: https://github.com/jazzband/django-dbbackup/pull/273
.. _`#280`: https://github.com/jazzband/django-dbbackup/pull/280
.. _`#260`: https://github.com/jazzband/django-dbbackup/pull/260
.. _`#349`: https://github.com/jazzband/django-dbbackup/pull/349
.. _`#348`: https://github.com/jazzband/django-dbbackup/pull/348
.. _`#337`: https://github.com/jazzband/django-dbbackup/pull/337
.. _`#408`: https://github.com/jazzband/django-dbbackup/pull/408
.. _`#371`: https://github.com/jazzband/django-dbbackup/pull/371
.. _`#379`: https://github.com/jazzband/django-dbbackup/pull/379
.. _`#411`: https://github.com/jazzband/django-dbbackup/pull/411
.. _`#413`: https://github.com/jazzband/django-dbbackup/pull/413
.. _`#414`: https://github.com/jazzband/django-dbbackup/pull/414
