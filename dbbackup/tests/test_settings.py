from imp import reload
from django.test import TestCase
from django.test.utils import override_settings
from django.core.exceptions import ImproperlyConfigured
from dbbackup import settings


def test_func(*args, **kwargs):
    return 'foo'


class SettingsTestCase(TestCase):
    @override_settings(DBBACKUP_FILENAME_TEMPLATE=test_func)
    def test_filename_template_is_callable(self):
        reload(settings)

    @override_settings(DBBACKUP_FILENAME_TEMPLATE='{datetime}.bak')
    def test_filename_template_is_string(self):
        reload(settings)

    @override_settings(DBBACKUP_FILENAME_TEMPLATE='foo.bak')
    def test_filename_template_no_date(self):
        with self.assertRaises(ImproperlyConfigured):
            reload(settings)

    def tearDown(self):
        reload(settings)
