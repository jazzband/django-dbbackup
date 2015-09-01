from io import BytesIO
from django.test import TestCase
import boto
try:
    from moto import mock_s3
except SyntaxError:
    mock_s3 = None
from dbbackup.storage.s3_storage import Storage as S3Storage
from dbbackup.storage.base import StorageError
from dbbackup.tests.utils import skip_py3


# Python 3.2 fix
if mock_s3 is None:
    def mock_s3(obj):
        return obj


@mock_s3
@skip_py3
class S3StorageTest(TestCase):
    def setUp(self):
        self.storage = S3Storage(bucket_name='foo_bucket',
                                 access_key='foo_id',
                                 secret_key='foo_secret')
        # Create fixtures
        self.conn = boto.connect_s3()
        self.bucket = self.conn.create_bucket('foo_bucket')
        key = boto.s3.key.Key(self.bucket)
        key.key = 'foo_file'
        key.set_contents_from_string('bar')

    def test_delete_file(self):
        self.storage.delete_file('foo_file')
        self.assertEqual(0, len(self.bucket.get_all_keys()))

    def test_list_directory(self):
        files = self.storage.list_directory()
        self.assertEqual(len(files), 1)

    def test_write_file(self):
        self.storage.write_file(BytesIO(b'bar'), 'foo')
        self.assertEqual(2, len(self.bucket.get_all_keys()))
        key = self.bucket.get_key('foo')
        self.assertEqual('bar', key.get_contents_as_string())

    def test_read_file(self):
        read_file = self.storage.read_file('foo_file')
        self.assertEqual(read_file.read(), b'bar')

    def test_check(self):
        with self.assertRaises(StorageError):
            self.storage._check_filesystem_errors({
                'bucket_name': '', 'access_key': ''})
        with self.assertRaises(StorageError):
            self.storage._check_filesystem_errors({
                'bucket_name': '', 'secret_key': ''})
        with self.assertRaises(StorageError):
            self.storage._check_filesystem_errors({
                'access_key': '', 'secret_key': ''})
        self.storage._check_filesystem_errors({
            'bucket_name': '', 'access_key': '', 'secret_key': ''})
