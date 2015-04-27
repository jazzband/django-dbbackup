"""
Util functions for dropbox application.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import sys
import os
import tempfile
from django.core.mail import EmailMessage
from django.db import connection
from django.http import HttpRequest
from django.views.debug import ExceptionReporter
from functools import wraps

from dbbackup import settings

FAKE_HTTP_REQUEST = HttpRequest()
FAKE_HTTP_REQUEST.META['SERVER_NAME'] = ''
FAKE_HTTP_REQUEST.META['SERVER_PORT'] = ''
FAKE_HTTP_REQUEST.META['HTTP_HOST'] = 'django-dbbackup'

BYTES = (
    ('PB', 1125899906842624.0),
    ('TB', 1099511627776.0),
    ('GB', 1073741824.0),
    ('MB', 1048576.0),
    ('KB', 1024.0),
    ('B', 1.0)
)


def bytes_to_str(byteVal, decimals=1):
    """ Convert bytes to a human readable string. """
    for unit, byte in BYTES:
        if (byteVal >= byte):
            if decimals == 0:
                return '%s %s' % (int(round(byteVal / byte, 0)), unit)
            return '%s %s' % (round(byteVal / byte, decimals), unit)
    return '%s B' % byteVal


def handle_size(filehandle):
    """ Given a filehandle return the filesize. """
    filehandle.seek(0, 2)
    return bytes_to_str(filehandle.tell())


def email_uncaught_exception(func):
    """ Decorator: Email uncaught exceptions to the SERVER_EMAIL. """
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
                message.send(fail_silently=True)
            raise
        finally:
            connection.close()
    return wrapper


def encrypt_file(inputfile):
    """ Encrypt the file using gpg. The input and the output are filelike objects. """
    import gnupg
    tempdir = tempfile.mkdtemp()
    try:
        filename = '%s.gpg' % inputfile.name
        filepath = os.path.join(tempdir, filename)
        try:
            inputfile.seek(0)
            always_trust = settings.GPG_ALWAYS_TRUST
            g = gnupg.GPG()
            result = g.encrypt_file(inputfile, output=filepath,
                recipients=settings.GPG_RECIPIENT, always_trust=always_trust)
            inputfile.close()
            if not result:
                raise Exception('Encryption failed; status: %s' % result.status)
            return create_spooled_temporary_file(filepath)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    finally:
        os.rmdir(tempdir)


def create_spooled_temporary_file(filepath):
    """ Create a spooled temporary file.
        - filepath: path of input file
        - filename: file of the spooled temporary file
    """
    spooled_file = tempfile.SpooledTemporaryFile(max_size=500 * 1024 * 1024)
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
