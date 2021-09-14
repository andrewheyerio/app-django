from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("waiting for db connection...")

        conn = None

        while not conn:
            try:
                conn = connections['default']
            except OperationalError:
                self.stdout.write("database unavailable, waiting for 1 second...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("database connected"))