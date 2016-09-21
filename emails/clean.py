import logging
from django.conf import settings

from emails.models import EmailEntry
from custom.stats import increment


send_logger = logging.getLogger('sender')

def clean_entries():
    """
    Deletes all entries marked as deleted=True
    """
    to_delete = EmailEntry.objects.filter(deleted=True)
    count = to_delete.count()
    to_delete.delete()
    increment(settings.METRIC['CLEAN_OK'], count)
    send_logger.info('[cleaner] Cleaned entries {}'.format(count))
    return count
