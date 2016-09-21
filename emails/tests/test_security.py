from django.test import TestCase
from django.test import override_settings

from emails.models import EmailKind
from ..security import is_spam


def yes_spam_stub(entry):
    return True
    
def not_spam_stub(entry):
    return False


class SpamTest(TestCase):
    def setUp(self):
        self.ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        self.entry_params = {
            'customer_id': '08838234',
            'reply_to': ['noreply@qdqmedia.com']
        }

    @override_settings(
        SPAM_CHECK={'my-test-email': ('emails.tests.test_security.yes_spam_stub',)}
    )
    def test_is_spam_returns_positive(self):
        self.entry_params['context'] = {
            'body_msg': 'Hello, visit <a href="viagramaximum.com">chemicals</a>'
        }
        eentry = self.ekind.generate_entry(self.entry_params)
        self.assertTrue(is_spam(eentry))

    @override_settings(
        SPAM_CHECK={'my-test-email': ('emails.tests.test_security.not_spam_stub',)}
    )
    def test_is_spam_returns_negative(self):
        self.entry_params['context'] = {
            'body_msg': 'Hello, visit viagramaximum.com'
        }
        eentry = self.ekind.generate_entry(self.entry_params)
        self.assertFalse(is_spam(eentry))

    @override_settings(
        SPAM_CHECK={'my-test-email': ('emails.tests.test_security.yes_spam_stub',
                                      'emails.tests.test_security.not_spam_stub')}
    )
    def test_is_spam_returns_positive_with_contradictory_checks(self):
        self.entry_params['context'] = {
            'body_msg': 'Hello, visit <a href="viagramaximum.com">chemicals</a>'
        }
        eentry = self.ekind.generate_entry(self.entry_params)
        self.assertTrue(is_spam(eentry))
