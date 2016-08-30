Integration tutorials
=====================

.. note::

    If you have a custom and/or interesting way of use DBBackup, do not
    hesitate to make us a pull request.

Django-cron
-----------

Example of cron job with `django-cron`_  with file system storage: ::

  import os
  from django.core import management
  from django.conf import settings
  from django_cron import CronJobBase, Schedule


  class Backup(CronJobBase):
      RUN_AT_TIMES = ['6:00', '18:00']
      schedule = Schedule(run_at_times=RUN_AT_TIMES)
      code = 'my_app.Backup'
 
      def do(self):
          management.call_command('dbbackup')

.. _`django-cron`: https://github.com/Tivix/django-cron
