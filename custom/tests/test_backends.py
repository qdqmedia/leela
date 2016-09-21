from unittest import TestCase
from django.test import override_settings
from django.conf import settings

from custom.backends import MandrillResponseManager


class MandrillResponseManagerTestCase(TestCase):
    def setUp(self):
        self.response_manager = MandrillResponseManager()

    def test_email_sent_ok(self):
        email = EmailStub(response=[{
            '_id': 'fdfadfdafdafdafasd',
            'status': 'sent'
        }])
        entry = EntryStub()
        sent = self.response_manager.process_response(email, entry)

        self.assertTrue(sent)
        self.assertEqual('fdfadfdafdafdafasd', entry.thirdparty_id)
        self.assertEqual('', entry.thirdparty_reject)

    def test_email_sent_fail(self):
        email = EmailStub(response=[{
            '_id': 'fdfadfdafdafdafasd',
            'status': 'invalid'
        }])
        entry = EntryStub()
        sent = self.response_manager.process_response(email, entry)

        self.assertFalse(sent)
        self.assertEqual('fdfadfdafdafdafasd', entry.thirdparty_id)
        self.assertEqual('', entry.thirdparty_reject)

    def test_email_sent_rejected(self):
        email = EmailStub(response=[{
            '_id': 'fdfadfdafdafdafasd',
            'status': 'rejected',
            'reject_reason': 'hard-bounce'
        }])
        entry = EntryStub()
        sent = self.response_manager.process_response(email, entry)

        self.assertFalse(sent)
        self.assertEqual('fdfadfdafdafdafasd', entry.thirdparty_id)
        self.assertEqual('hard-bounce', entry.thirdparty_reject)

    def test_email_sent_ok_with_rejected_reason(self):
        email = EmailStub(response=[{
            '_id': 'fdfadfdafdafdafasd',
            'status': 'sent',
            'reject_reason': 'fdafadf'
        }])
        entry = EntryStub()
        sent = self.response_manager.process_response(email, entry)

        self.assertTrue(sent)
        self.assertEqual('fdfadfdafdafdafasd', entry.thirdparty_id)
        self.assertEqual('', entry.thirdparty_reject)


class EmailStub(object):
    def __init__(self, response):
        self.mandrill_response = response


class EntryStub(object):
    def __init__(self):
        self.thirdparty_id = None
        self.is_spam = None
        self.thirdparty_reject = ''
