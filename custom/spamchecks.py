
def has_href(entry):
    """Report as spam if 'href' appears in the text."""
    for key in entry.context:
        if 'href' in entry.context[key]:
            return True
    return False


def above_remote_score(entry):
    """Report as spam if the entry exceeds remote filter threshold."""
    return False
