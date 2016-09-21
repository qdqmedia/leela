import logging
from django.conf import settings
from django.utils import timezone

from custom import import_from_module


logger = logging.getLogger('emails')

def send_with_backend(email, entry):
    default = settings.CUSTOM_DEFAULT_EMAIL_BACKEND
    name = entry.backend if entry.backend else default
    settings.EMAIL_BACKEND, rmanager = _get_backend(name)
    email.send()

    sent = rmanager.process_response(email, entry)
    if sent:
        entry.sent = True
        entry.datetime_sent = timezone.now()
        entry.rendered_template = email.alternatives[0][0]
        entry.rendered_plain_template = email.body
    else:
        logger.error("Rejected email {id} by backend {name}"\
                     .format(id=entry.id, name=name))
    entry.save()
    settings.EMAIL_BACKEND = None
    return sent

def _get_backend(name):
    for backend_tuple in settings.CUSTOM_EMAIL_BACKENDS:
        if backend_tuple[0] == name:
            backend_path = backend_tuple[1]
            response_manager_path = backend_tuple[2]
            response_manager = import_from_module(response_manager_path)()
            return (backend_path, response_manager)
    else:
        raise Exception('backend with name: {} not found'.format(name))


class BaseResponseManager(object):

    def process_response(self, email, entry):
        """
        Return True if the email was successfully sent. Does some
        postprocessing after sending the email, specific to its email
        backend, like storing the thirdparty_id in the entry.

        @type email: EmailMultiAlternatives
        @type entry: EmailEntry
        @return boolean if the sending has been successful
        """
        raise NotImplementedError('process_response method not implemented')
