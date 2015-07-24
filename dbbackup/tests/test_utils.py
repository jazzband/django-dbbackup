import os
import subprocess
try:
    from StringIO import StringIO
except ImportError:  # Py3
    from io import StringIO
from django.test import TestCase
from django.core import mail
from django.conf import settings
from mock import patch
from dbbackup import utils

GPG_PUBLIC_PATH = os.path.join(settings.BASE_DIR, 'tests/gpg/pubring.gpg')
DEV_NULL = open(os.devnull, 'w')


class Bytes_To_StrTest(TestCase):
    def test_get_gb(self):
        value = utils.bytes_to_str(byteVal=2**31)
        self.assertEqual(value, "2.0 GB")

    def test_0_decimal(self):
        value = utils.bytes_to_str(byteVal=1.01, decimals=0)
        self.assertEqual(value, "1 B")

    def test_2_decimal(self):
        value = utils.bytes_to_str(byteVal=1.01, decimals=2)
        self.assertEqual(value, "1.01 B")


class Handle_SizeTest(TestCase):
    def test_func(self):
        filehandle = StringIO('Test string')
        value = utils.handle_size(filehandle=filehandle)
        self.assertEqual(value, '11.0 B')


class Email_Uncaught_ExceptionTest(TestCase):
    def test_success(self):
        def func():
            pass
        utils.email_uncaught_exception(func)

    @patch('dbbackup.settings.SEND_EMAIL', False)
    def test_raise(self):
        def func():
            raise Exception('Foo')
        with self.assertRaises(Exception):
            utils.email_uncaught_exception(func)()
        self.assertEqual(len(mail.outbox), 0)

    @patch('dbbackup.settings.SEND_EMAIL', True)
    @patch('dbbackup.settings.FAILURE_RECIPIENTS', ['foo@bar'])
    def test_raise_with_mail(self):
        def func():
            raise Exception('Foo')
        with self.assertRaises(Exception):
            utils.email_uncaught_exception(func)()
        self.assertEqual(len(mail.outbox), 1)


class Encrypt_FileTest(TestCase):
    def setUp(self):
        self.path = '/tmp/foo'
        with open(self.path, 'a') as fd:
            fd.write('foo')
        cmd = ('gpg --import %s' % GPG_PUBLIC_PATH).split()
        subprocess.call(cmd, stdout=DEV_NULL, stderr=DEV_NULL)

    def tearDown(self):
        os.remove(self.path)
        subprocess.call('gpg --batch --yes --delete-key "test@test"'.split(),
                        stdout=DEV_NULL, stderr=DEV_NULL)

    def test_func(self, *args):
        with open(self.path) as fd:
            encrypted_file = utils.encrypt_file(inputfile=fd)
        encrypted_file.seek(0)
        self.assertTrue(encrypted_file.read())


class Create_Spooled_Temporary_FileTest(TestCase):
    def setUp(self):
        self.path = '/tmp/foo'
        with open(self.path, 'a') as fd:
            fd.write('foo')

    def tearDown(self):
        os.remove(self.path)

    def test_func(self, *args):
        utils.create_spooled_temporary_file(filepath=self.path)
