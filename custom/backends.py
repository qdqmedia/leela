from django.conf import settings
from emails.backends import BaseResponseManager
from djrill.mail.backends.djrill import DjrillBackend



class MandrillResponseManager(BaseResponseManager):

    def process_response(self, email, entry):
        if email.mandrill_response is not None:
            if '_id' in email.mandrill_response[0]:
                entry.thirdparty_id = email.mandrill_response[0]['_id']
            if email.mandrill_response[0]['status'] == 'rejected' and 'reject_reason' in email.mandrill_response[0]:
                if email.mandrill_response[0]['reject_reason'] == 'spam':
                    entry.is_spam = True
                entry.thirdparty_reject = email.mandrill_response[0]['reject_reason']
                return False
            return email.mandrill_response[0]['status'] in ('sent', 'queued', 'scheduled')

        return False
