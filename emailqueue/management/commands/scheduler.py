from django.core.management.base import BaseCommand

from emailqueue.consumer import send_email_consumer


class Command(BaseCommand):
    args = '<None ...>'
    help = 'Listens to the queue system waiting for emails to enqueue'

    def handle(self, *args, **kwargs):
        send_email_consumer()
