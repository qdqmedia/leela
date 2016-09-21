from django.conf import settings


def allowed_language_codes():
    langs = tuple()
    for tup in settings.LANGUAGES:
        langs += (tup[0], )
    return langs


def custom_assert(condition, message):
    if not condition:
        raise EmailAssertionError(message)


class EmailAssertionError(Exception):
    pass
