"""Management commands to help backup and restore a project database and media"""

import django


VERSION = (4, 0, 0)
"""The X.Y.Z version. Needed for `docs/conf.py`."""
VERSION_TAG = "a1"
"""The alpha/beta/rc tag for the version. For example 'b0'."""
__version__ = ".".join(map(str, VERSION)) + VERSION_TAG
"""The full version, including alpha/beta/rc tags."""

if django.VERSION < (3, 2):
    default_app_config = "dbbackup.apps.DbbackupConfig"
