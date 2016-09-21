import time
from django.core.management.base import BaseCommand
from django.conf import settings

from emails.send import send_entries


class Command(BaseCommand):
    args = '<None ...>'
    help = 'Processes the email entries, sending them if proceed'

    def handle(self, *args, **options):
        while True:
            send_entries()
            time.sleep(settings.SENDER_ELLAPSED_SECONDS)
