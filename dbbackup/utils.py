"""
Utility functions for dbbackup.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import sys
import os
import tempfile
import gzip
import re
from getpass import getpass
from shutil import copyfileobj
from functools import wraps
from datetime import datetime

from django.core.mail import EmailMessage
from django.db import connection
from django.http import HttpRequest
from django.views.debug import ExceptionReporter
from django.utils import six, timezone

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

REG_FILENAME_CLEAN = re.compile(r'-+')


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


def timestamp(value):
    """
    Return the timestamp of a datetime.datetime object.

    :param value: a datetime object
    :type value: datetime.datetime

    :return: the timestamp
    :rtype: str
    """
    value = value if timezone.is_naive(value) else timezone.localtime(value)
    return value.strftime(settings.DATE_FORMAT)


def filename_details(filepath):
    # TODO: What was this function made for ?
    return ''


PATTERN_MATCHNG = (
    ('%a', r'[A-Z][a-z]+'),
    ('%A', r'[A-Z][a-z]+'),
    ('%w', r'\d'),
    ('%d', r'\d{2}'),
    ('%b', r'[A-Z][a-z]+'),
    ('%B', r'[A-Z][a-z]+'),
    ('%m', r'\d{2}'),
    ('%y', r'\d{2}'),
    ('%Y', r'\d{4}'),
    ('%H', r'\d{2}'),
    ('%I', r'\d{2}'),
    # ('%p', r'(?AM|PM|am|pm)'),
    ('%M', r'\d{2}'),
    ('%S', r'\d{2}'),
    ('%f', r'\d{6}'),
    # ('%z', r'\+\d{4}'),
    # ('%Z', r'(?|UTC|EST|CST)'),
    ('%j', r'\d{3}'),
    ('%U', r'\d{2}'),
    ('%W', r'\d{2}'),
    # ('%c', r'[A-Z][a-z]+ [A-Z][a-z]{2} \d{2} \d{2}:\d{2}:\d{2} \d{4}'),
    # ('%x', r'd{2}/d{2}/d{4}'),
    # ('%X', r'd{2}:d{2}:d{2}'),
    # ('%%', r'%'),
)


def datefmt_to_regex(datefmt):
    """
    Convert a strftime format string to a regex.

    :param datefmt: strftime format string
    :type datefmt: ``str``

    :returns: Equivalent regex
    :rtype: ``re.compite``
    """
    new_string = datefmt
    for pat, reg in PATTERN_MATCHNG:
        new_string = new_string.replace(pat, reg)
    return re.compile(r'(%s)' % new_string)


def filename_to_datestring(filename, datefmt=None):
    """
    Return the date part of a file name.

    :param datefmt: strftime format string, ``settings.DATE_FORMAT`` is used
                    if is ``None``
    :type datefmt: ``str`` or ``None``

    :returns: Date part
    :rtype: ``str``
    """
    datefmt = datefmt or settings.DATE_FORMAT 
    regex = datefmt_to_regex(datefmt)
    search = regex.search(filename)
    return search.groups()[0]


def filename_to_date(filename, datefmt=None):
    """
    Return a datetime from a file name.

    :param datefmt: strftime format string, ``settings.DATE_FORMAT`` is used
                    if is ``None``
    :type datefmt: ``str`` or ``None``

    :returns: Date guessed
    :rtype: ``datetime.datetime``
    """
    datefmt = datefmt or settings.DATE_FORMAT 
    datestring = filename_to_datestring(filename, datefmt)
    return datetime.strptime(datestring, datefmt)


def filename_generate(extension, database_name='', servername=None,
                      content_type='db'):
    """
    Create a new backup filename.

    :param extension: Extension of backup file
    :type extension: ``str``

    :param database_name: If it is database backup specify its name
    :type database_name: ``str``

    :param servername: Specify server name or by default ``settings.HOSTNAME``
    :type servername: ``str``

    :param content_type: Content type to backup, ``'media'`` or ``'db'``
    :type content_type: ``str``

    :returns: Computed file name
    :rtype: ``str`
    """
    if content_type == 'db':
        name_format = settings.FILENAME_TEMPLATE
        database_name = database_name.replace("/", "_")
    else:
         name_format = settings.MEDIA_FILENAME_TEMPLATE
    params = {
        'servername': servername or settings.HOSTNAME,
        'datetime': timezone.now().strftime(settings.DATE_FORMAT),
        'databasename': database_name,
        'extension': extension,
        'content_type': content_type
    }
    if callable(settings.FILENAME_TEMPLATE):
        filename = settings.FILENAME_TEMPLATE(**params)
    else:
        filename = settings.FILENAME_TEMPLATE.format(**params)
        filename = REG_FILENAME_CLEAN.sub('-', filename)
        filename = filename[1:] if filename.startswith('-') else filename
    return filename
