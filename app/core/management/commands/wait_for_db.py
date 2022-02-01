from lib2to3.pytree import Base
import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Djando command to pause execution until DB is available"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for db....")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write("DB unavailabl, waiting...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("DB available"))
