#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.core.management import execute_from_command_line


def main(argv=None):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'dbbackup.tests.settings'
    argv = argv or []
    if len(argv) <= 1:
        from django.test.utils import get_runner
        if django.VERSION >= (1, 7):
            django.setup()
        TestRunner = get_runner(settings)
        test_runner = TestRunner()
        result = test_runner.run_tests(["dbbackup.tests"])
        return result
    execute_from_command_line(argv)


if __name__ == '__main__':
    sys.exit(bool(main(sys.argv)))
