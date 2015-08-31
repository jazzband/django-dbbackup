"""
Utility functions for dbbackup.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import sys
import os
import tempfile
import gzip
from getpass import getpass
from shutil import copyfileobj
from functools import wraps

from django.core.mail import EmailMessage
from django.db import connection
from django.http import HttpRequest
from django.views.debug import ExceptionReporter
from django.utils import six

from . import settings

input = raw_input if six.PY2 else input  # @ReservedAssignment

FAKE_HTTP_REQUEST = HttpRequest()
FAKE_HTTP_REQUEST.META['SERVER_NAME'] = ''
FAKE_HTTP_REQUEST.META['SERVER_PORT'] = ''
FAKE_HTTP_REQUEST.META['HTTP_HOST'] = settings.HOSTNAME
FAKE_HTTP_REQUEST.path = '/DJANGO-DBBACKUP-EXCEPTION'

BYTES = (
    ('PB', 1125899906842624.0),
    ('TB', 1099511627776.0),
    ('GB', 1073741824.0),
    ('MB', 1048576.0),
    ('KB', 1024.0),
    ('B', 1.0)
)


class EncryptionError(Exception):
    pass


class DecryptionError(Exception):
    pass


def bytes_to_str(byteVal, decimals=1):
    """
    Convert bytes to a human readable string.

    :param byteVal: Value to convert in bytes
    :type byteVal: int or float

    :param decimal: Number of decimal to display
    :type decimal: int

    :returns: Number of byte with the best unit of measure
    :rtype: str
    """
    for unit, byte in BYTES:
        if (byteVal >= byte):
            if decimals == 0:
                return '%s %s' % (int(round(byteVal / byte, 0)), unit)
            return '%s %s' % (round(byteVal / byte, decimals), unit)
    return '%s B' % byteVal


def handle_size(filehandle):
    """
    Get file's size to a human readable string.

    :param filehandle: File to handle
    :type filehandle: file

    :returns: File's size with the best unit of measure
    :rtype: str
    """
    filehandle.seek(0, 2)
    return bytes_to_str(filehandle.tell())


def email_uncaught_exception(func):
    """
    Function decorator for send email with uncaught exceptions to admins.
    Email is sent to ``settings.DBBACKUP_FAILURE_RECIPIENTS``
    (``settings.ADMINS`` if not defined). The message contains a traceback
    of error.
    """
    module = func.__module__

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            if settings.SEND_EMAIL:
                excType, excValue, traceback = sys.exc_info()
                reporter = ExceptionReporter(FAKE_HTTP_REQUEST, excType,
                                             excValue, traceback.tb_next)
                subject = 'Cron: Uncaught exception running %s' % module
                body = reporter.get_traceback_html()
                msgFrom = settings.SERVER_EMAIL
                msgTo = [admin[1] for admin in settings.FAILURE_RECIPIENTS]
                message = EmailMessage(subject, body, msgFrom, msgTo)
                message.content_subtype = 'html'
                message.send(fail_silently=False)
            raise
        finally:
            connection.close()
    return wrapper


def encrypt_file(inputfile, filename):
    """
    Encrypt input file using GPG and remove .gpg extension to its name.

    :param inputfile: File to encrypt
    :type inputfile: ``file`` like object

    :param filename: File's name
    :type filename: ``str``

    :returns: Tuple with file and new file's name
    :rtype: :class:`tempfile.SpooledTemporaryFile`, ``str``
    """
    import gnupg
    tempdir = tempfile.mkdtemp(dir=settings.TMP_DIR)
    try:
        filename = '%s.gpg' % filename
        filepath = os.path.join(tempdir, filename)
        try:
            inputfile.seek(0)
            always_trust = settings.GPG_ALWAYS_TRUST
            g = gnupg.GPG()
            result = g.encrypt_file(inputfile, output=filepath,
                                    recipients=settings.GPG_RECIPIENT,
                                    always_trust=always_trust)
            inputfile.close()
            if not result:
                msg = 'Encryption failed; status: %s' % result.status
                raise EncryptionError(msg)
            return create_spooled_temporary_file(filepath), filename
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    finally:
        os.rmdir(tempdir)


def unencrypt_file(inputfile, filename, passphrase=None):
    """
    Unencrypt input file using GPG and remove .gpg extension to its name.

    :param inputfile: File to encrypt
    :type inputfile: ``file`` like object

    :param filename: File's name
    :type filename: ``str``

    :param passphrase: Passphrase of GPG key, if equivalent to False, it will
                       be asked to user. If user answer an empty pass, no
                       passphrase will be used.
    :type passphrase: ``str`` or ``None``

    :returns: Tuple with file and new file's name
    :rtype: :class:`tempfile.SpooledTemporaryFile`, ``str``
    """
    import gnupg

    def get_passphrase(passphrase=passphrase):
        return passphrase or getpass('Input Passphrase: ') or None

    temp_dir = tempfile.mkdtemp(dir=settings.TMP_DIR)
    try:
        new_basename = os.path.basename(filename).replace('.gpg', '')
        temp_filename = os.path.join(temp_dir, new_basename)
        try:
            inputfile.seek(0)
            g = gnupg.GPG()
            result = g.decrypt_file(file=inputfile, passphrase=get_passphrase(),
                                    output=temp_filename)
            if not result:
                raise DecryptionError('Decryption failed; status: %s' % result.status)
            outputfile = tempfile.SpooledTemporaryFile(
                max_size=settings.TMP_FILE_MAX_SIZE, dir=settings.TMP_DIR)
            f = open(temp_filename, 'r+b')
            try:
                outputfile.write(f.read())
            finally:
                f.close()
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    finally:
        os.rmdir(temp_dir)
    return outputfile, new_basename


def compress_file(inputfile, filename):
    """
    Compress input file using gzip and change its name.

    :param inputfile: File to compress
    :type inputfile: ``file`` like object

    :param filename: File's name
    :type filename: ``str``

    :returns: Tuple with compressed file and new file's name
    :rtype: :class:`tempfile.SpooledTemporaryFile`, ``str``
    """
    outputfile = tempfile.SpooledTemporaryFile(
        max_size=settings.TMP_FILE_MAX_SIZE, dir=settings.TMP_DIR)
    new_filename = filename + '.gz'
    zipfile = gzip.GzipFile(filename=filename, fileobj=outputfile, mode="wb")
    # TODO: Why do we have an exception block without handling exceptions?
    try:
        inputfile.seek(0)
        copyfileobj(inputfile, zipfile, settings.TMP_FILE_READ_SIZE)
    finally:
        zipfile.close()
    return outputfile, new_filename


def uncompress_file(inputfile, filename):
    """
    Uncompress this file using gzip and change its name.

    :param inputfile: File to compress
    :type inputfile: ``file`` like object

    :param filename: File's name
    :type filename: ``str``

    :returns: Tuple with file and new file's name
    :rtype: :class:`tempfile.SpooledTemporaryFile`, ``str``
    """
    outputfile = tempfile.SpooledTemporaryFile(
        max_size=settings.TMP_FILE_MAX_SIZE, dir=settings.TMP_DIR)
    zipfile = gzip.GzipFile(fileobj=inputfile, mode="rb")
    try:
        inputfile.seek(0)
        outputfile.write(zipfile.read())
    finally:
        zipfile.close()
    new_basename = os.path.basename(filename).replace('.gz', '')
    return outputfile, new_basename


def create_spooled_temporary_file(filepath):
    """
    Create a spooled temporary file.

    :param filepath: Path of input file
    :type filepath: str

    :returns: file of the spooled temporary file
    :rtype: :class:`tempfile.SpooledTemporaryFile`
    """
    spooled_file = tempfile.SpooledTemporaryFile(
        max_size=settings.TMP_FILE_MAX_SIZE,
        dir=settings.TMP_DIR)
    tmpfile = open(filepath, 'r+b')
    try:
        while True:
            data = tmpfile.read(1024 * 1000)
            if not data:
                break
            spooled_file.write(data)
    finally:
        tmpfile.close()
    return spooled_file


def filename_details(filepath):
    # TODO: What was this function made for ?
    return ''
