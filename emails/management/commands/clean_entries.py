import time
from django.core.management.base import BaseCommand
from django.conf import settings

from emails.clean import clean_entries


class Command(BaseCommand):
    args = '<None ...>'
    help = 'Clean the email entries marked for deletion'

    def handle(self, *args, **options):
        while True:
            clean_entries()
            time.sleep(settings.CLEANER_ELLAPSED_SECONDS)
