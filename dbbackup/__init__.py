"""Management commands to help backup and restore a project database and media"""

from pathlib import Path

import django

src_dir = Path(__file__).parent
with (src_dir / "VERSION").open() as f:
    __version__ = f.read().strip()
    """The full version, including alpha/beta/rc tags."""

VERSION = (x, y, z) = __version__.split(".")
VERSION = ".".join(VERSION[:2])
"""The X.Y version. Needed for `docs/conf.py`."""


if django.VERSION < (3, 2):
    default_app_config = "dbbackup.apps.DbbackupConfig"
