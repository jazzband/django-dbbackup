import os
import subprocess
import logging
from django.conf import settings
from django.utils import six
from django.utils.six import StringIO
from dbbackup.storage.base import BaseStorage

BASE_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt')
ENCRYPTED_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt.gpg')
COMPRESSED_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt.gz')
ENCRYPTED_COMPRESSED_FILE = os.path.join(settings.BASE_DIR, 'tests/test.txt.gz.gpg')
TEST_DATABASE = {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '/tmp/foo.db', 'USER': 'foo', 'PASSWORD': 'bar', 'HOST': 'foo', 'PORT': 122}

GPG_PRIVATE_PATH = os.path.join(settings.BASE_DIR, 'tests/gpg/secring.gpg')
GPG_PUBLIC_PATH = os.path.join(settings.BASE_DIR, 'tests/gpg/pubring.gpg')
GPG_FINGERPRINT = '7438 8D4E 02AF C011 4E2F  1E79 F7D1 BBF0 1F63 FDE9'
DEV_NULL = open(os.devnull, 'w')


class handled_files(dict):
    """
    Dict for gather information about fake storage and clean between tests.
    You should use the constant instance ``HANDLED_FILES`` and clean it
    before tests.
    """
    def __init__(self):
        super(handled_files, self).__init__()
        self.clean()

    def clean(self):
        self['written_files'] = []
        self['deleted_files'] = []
HANDLED_FILES = handled_files()


class FakeStorage(BaseStorage):
    name = 'FakeStorage'
    logger = logging.getLogger('dbbackup.storage')

    def __init__(self, *args, **kwargs):
        super(FakeStorage, self).__init__(*args, **kwargs)
        self.deleted_files = []
        self.written_files = []

    def delete_file(self, filepath):
        self.logger.debug("Delete %s", filepath)
        HANDLED_FILES['deleted_files'].append(filepath)
        self.deleted_files.append(filepath)

    def list_directory(self, raw=False):
        return [f[0] for f in HANDLED_FILES['written_files']]

    def write_file(self, filehandle, filename):
        self.logger.debug("Write %s", filename)
        HANDLED_FILES['written_files'].append((filename, filehandle))

    def read_file(self, filepath):
        return [f[1] for f in HANDLED_FILES['written_files'] if f[0] == filepath][0]

Storage = FakeStorage


def clean_gpg_keys():
    try:
        cmd = ("gpg --batch --yes --delete-key '%s'" % GPG_FINGERPRINT)
        subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)
    except:
        pass
    try:
        cmd = ("gpg --batch --yes --delete-secrect-key '%s'" % GPG_FINGERPRINT)
        subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)
    except:
        pass


def add_private_gpg():
    cmd = ('gpg --import %s' % GPG_PRIVATE_PATH).split()
    subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)


def add_public_gpg():
    cmd = ('gpg --import %s' % GPG_PUBLIC_PATH).split()
    subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)


def skip_py3(testcase, reason="Not in Python 3"):
    """Decorator for skip Python 3 tests."""
    if six.PY3:
        setup = lambda s: s.skipTest(reason)
        testcase.setUp = setup
    return testcase


def callable_for_filename_template(datetime, **kwargs):
    return '%s_foo' % datetime
