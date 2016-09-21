from django.conf import settings
from custom import import_from_module

def is_spam(entry):
    """Given an EmailEntry, checks if considered spam depending on the
    SPAM_CHECK settings."""
    checks = settings.SPAM_CHECK.get(entry.kind.name, ())
    for checkpath in checks:
        check = import_from_module(checkpath)
        if check(entry):
            return True
    return False
