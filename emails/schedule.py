import logging
from django.conf import settings
from emails.models import EmailKind
from custom.stats import increment

sched_logger = logging.getLogger('scheduler')


def schedule(name, language, params):
    """
    Generates an EmailEntry given the EmailKind and params, and stores it
    for asynchronous send.
    @type name: string
    @type language: string
    @type params dict
    @param params Dictionary containing data to build the EmailEntry from
    the current EmailKind. Check README.md for details.
    """
    try:
        emailkind = EmailKind.objects.get(name=name, language=language)
    except EmailKind.DoesNotExist:
        emailkind = EmailKind.objects.get(
            name=name,
            language=settings.DEFAULT_LANGUAGE_CODE
        )
        increment(settings.METRIC['SCHEDULE_WRONG_LANG'])
        sched_logger.warning(
            'EmailKind {} with language {} not defined. Taking default.'\
            .format(name, language)
        )
    entry = emailkind.generate_entry(params)
    return entry
