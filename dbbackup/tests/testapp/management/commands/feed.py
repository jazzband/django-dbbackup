from django.core.management.base import BaseCommand
from dbbackup.tests.testapp.models import CharModel
from dbbackup.tests.utils import FakeStorage


class Command(BaseCommand):
    help = "Count things"

    def handle(self, **options):
        for st in 'abcde':
            CharModel.objects.create(field=st)
