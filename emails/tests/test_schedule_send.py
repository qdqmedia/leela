from unittest.mock import patch
import time
import json
import base64
import datetime

from django.test import override_settings
from django.test import TestCase
from django.utils import timezone

from emails.models import EmailKind, EmbeddedImage, EmailEntry, \
    Attachment
from emails.send import send, send_entries
from emails.schedule import schedule
from emails.clean import clean_entries
from emails.tests.utils import create_upload_image, get_jpg_content
from emails.utils import EmailAssertionError


class SendEntriesTest(TestCase):
    def tearDown(self):
        EmailKind.objects.all().delete()
        EmailEntry.objects.all().delete()        

    def test_send_emailkind_no_active(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com',
            active=False
        )
        entry_params = {}
        entry = schedule('my-test-email', 'es', entry_params)
        send_entries()

        entry = EmailEntry.objects.get(id=entry.id)
        self.assertFalse(entry.sent)
        self.assertIsNone(entry.datetime_sent)

    def test_send_emailkind_is_spam(self):
        """TODO"""
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        entry_params = {}
        entry = schedule('my-test-email', 'es', entry_params)
        entry.is_spam = True
        entry.save()
        send_entries()

        entry = EmailEntry.objects.get(id=entry.id)
        self.assertFalse(entry.sent)
        self.assertIsNone(entry.datetime_sent)


class ScheduleAndSendIntegrationTest(TestCase):

    def tearDown(self):
        EmailKind.objects.all().delete()
        EmailEntry.objects.all().delete()

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockSuccess',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_schedule_without_send_at_without_check_url(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )

        schedule('my-test-email', 'es', {})
        sent_count = send_entries()
        self.assertEqual(1, sent_count)

    def test_schedule_with_send_at_future_without_check_url_not_sent(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )

        now_ts = int(time.mktime(timezone.now().timetuple()))
        future_ts = now_ts + 300
        schedule('my-test-email', 'es', {
            'send_at': future_ts
        })
        sent_count = send_entries()
        self.assertEqual(0, sent_count)

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockSuccess',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_schedule_with_send_at_past_without_check_url_sent(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )

        now_ts = int(time.mktime(timezone.now().timetuple()))
        past_ts = now_ts - 300
        schedule('my-test-email', 'es', {
            'send_at': past_ts
        })
        sent_count = send_entries()
        self.assertEqual(1, sent_count)

    @patch('emails.send.requests.models.Response')
    @patch('emails.send.requests')
    def test_schedule_without_send_at_with_check_url_false_not_sent(
            self, mock_requests, mock_Response
    ):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )

        schedule('my-test-email', 'es', {
            'check_url': 'http://service.qdqmedia.com/cansend/34324/blah'
        })

        mock_Response.configure_mock(status_code=200)
        mock_Response.configure_mock(text=json.dumps({'allowed': False}))
        mock_requests.get.return_value = mock_Response

        sent_count = send_entries()
        self.assertEqual(0, sent_count)

    @patch('emails.send.requests.models.Response')
    @patch('emails.send.requests')
    def test_schedule_without_send_at_with_check_url_false_not_sent_delete(
            self, mock_requests, mock_Response
    ):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )

        schedule('my-test-email', 'es', {
            'check_url': 'http://service.qdqmedia.com/cansend/34324/blah'
        })

        mock_Response.configure_mock(status_code=200)
        mock_Response.configure_mock(text=json.dumps({'allowed': False, 'delete': True}))
        mock_requests.get.return_value = mock_Response

        sent_count = send_entries()
        self.assertEqual(0, sent_count)
        entries = EmailEntry.objects.filter(deleted=True)
        self.assertEqual(1, len(entries))

        clean_entries()
        entries = EmailEntry.objects.filter(deleted=True)
        self.assertEqual(0, len(entries))

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockSuccess',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    @patch('emails.send.requests.models.Response')
    @patch('emails.send.requests')
    def test_schedule_without_send_at_with_check_url_true_sent(
            self, mock_requests, mock_Response
    ):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )

        schedule('my-test-email', 'es', {
            'check_url': 'http://service.qdqmedia.com/cansend/34324/blah'
        })

        mock_Response.configure_mock(status_code=200)
        mock_Response.configure_mock(text=json.dumps({'allowed': True}))
        mock_requests.get.return_value = mock_Response

        sent_count = send_entries()
        self.assertEqual(1, sent_count)

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockSuccess',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_send_no_attachs_success(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        entry_params = {}
        entry = schedule('my-test-email', 'es', entry_params)
        email = send(entry)

        entry = EmailEntry.objects.get(id=entry.id)
        self.assertTrue(entry.sent)
        self.assertEqual('348dj38dj28do5jd82', entry.thirdparty_id)
        self.assertEqual('Hello, world!', entry.rendered_template)
        self.assertEqual('Hello, world! soy antiguo',
                         entry.rendered_plain_template)

        self.assertEqual('Hello, world! soy antiguo', email.body)
        self.assertEqual('Hello, world!', email.alternatives[0][0])
        self.assertEqual('text/html', email.alternatives[0][1])
        self.assertEqual('348dj38dj28do5jd82', email.response_content[0]['id'])
        self.assertEqual(entry.recipients.split(','), email.to)
        self.assertEqual(entry.sender, email.from_email)
        self.assertEqual(entry.subject, email.subject)
        self.assertEqual(entry.reply_to.split(','), email.reply_to)
        self.assertIsNotNone(entry.datetime_sent)

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockFailure',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_send_no_attachs_failure(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        entry_params = {}
        entry = schedule('my-test-email', 'es', entry_params)
        send(entry)

        entry = EmailEntry.objects.get(id=entry.id)
        self.assertFalse(entry.sent)
        self.assertEqual('', entry.thirdparty_id)
        self.assertEqual('', entry.rendered_template)
        self.assertEqual('', entry.rendered_plain_template)
        self.assertIsNone(entry.datetime_sent)

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockSuccess',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_send_attachs_success(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        image_content = get_jpg_content()
        entry_params = {
            'attachs': [{
                'filename': 'test.jpg',
                'content_type': 'image/jpeg',
                'content': base64.b64encode(image_content)
            }]
        }

        entry = schedule('my-test-email', 'es', entry_params)
        email = send(entry)

        self.assertTrue(entry.sent)
        self.assertEqual('348dj38dj28do5jd82', entry.thirdparty_id)
        self.assertIsNotNone(entry.datetime_sent)
        self.assertEqual('Hello, world!', entry.rendered_template)
        self.assertEqual('Hello, world! soy antiguo',
                         entry.rendered_plain_template)

        att = Attachment.objects.get(entry=entry)
        self.assertEqual('test.jpg', att.name)
        self.assertEqual('image/jpeg', att.content_type)

        self.assertEqual(email.attachments[0][0], 'test.jpg')
        self.assertEqual(email.attachments[0][1], image_content)
        self.assertEqual(email.attachments[0][2], 'image/jpeg')

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockSuccess',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_send_embedded_images_success(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template=('<h1>Hola, {{ first_name }}</h1>'
                      '<img src="cid:logo-solocal">'
                      '<img src="cid:logo-qdq">'),
            plain_template='Hola, {{ first_name }}',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com',
            default_context={'first_name': 'Luisa'}
        )
        upload_image1 = create_upload_image()
        upload_image2 = create_upload_image()
        EmbeddedImage.objects.create(
            kind=ekind,
            placeholder_name='logo-solocal',
            image=upload_image1
        )
        EmbeddedImage.objects.create(
            kind=ekind,
            placeholder_name='logo-qdq',
            image=upload_image2
        )
        entry_params = {}

        entry = schedule('my-test-email', 'es', entry_params)
        email = send(entry)
        self.assertTrue(entry.sent)
        self.assertIsNotNone(entry.datetime_sent)
        self.assertEqual(2, len(email.attachments))

        image1 = EmbeddedImage.objects.get(kind=ekind, placeholder_name='logo-solocal')
        self.assertEqual(image1.content_id[1:-1], email.attachments[1].get('Content-ID'))
        image2 = EmbeddedImage.objects.get(kind=ekind, placeholder_name='logo-qdq')
        self.assertEqual(image2.content_id[1:-1], email.attachments[0].get('Content-ID'))

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockSuccess',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_send_embedded_images_some_unused(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template=('<h1>Hola, {{ first_name }}</h1>'
                      '<img src="cid:logo-solocal">'),
            plain_template='Hola, {{ first_name }}',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com',
            default_context={'first_name': 'Luisa'}
        )
        upload_image1 = create_upload_image()
        upload_image2 = create_upload_image()
        EmbeddedImage.objects.create(
            kind=ekind,
            placeholder_name='logo-solocal',
            image=upload_image1
        )
        EmbeddedImage.objects.create(
            kind=ekind,
            placeholder_name='logo-qdq',
            image=upload_image2
        )
        entry_params = {}

        entry = schedule('my-test-email', 'es', entry_params)
        email = send(entry)
        self.assertTrue(entry.sent)
        self.assertIsNotNone(entry.datetime_sent)
        self.assertEqual(1, len(email.attachments))

        image1 = EmbeddedImage.objects.get(kind=ekind, placeholder_name='logo-solocal')
        self.assertEqual(image1.content_id[1:-1], email.attachments[0].get('Content-ID'))

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockFailure',
             'emails.tests.utils.ResponseManagerStub'
            ),
            ('mynewbackend',
             'emails.tests.utils.EmailBackendMockSuccess',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_send_with_specific_backend_success(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        schedule('my-test-email', 'es', { 'backend': 'mynewbackend' })
        sent_count = send_entries()
        self.assertEqual(1, sent_count)

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockFailure',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_schedule_with_specific_backend_unknown_fail(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        self.assertRaises(
            EmailAssertionError,
            schedule, 'my-test-email', 'es', { 'backend': 'mynewbackend' }
        )

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('myrejectbackend',
             'emails.tests.utils.EmailBackendMockReject',
             'emails.tests.utils.ResponseManagerRejectStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_send_with_specific_backend_rejected(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        entry = schedule('my-test-email', 'es', { 'backend': 'myrejectbackend' })
        sent_count = send_entries()
        entry = EmailEntry.objects.get(id=entry.id)
        self.assertEqual(0, sent_count)
        self.assertFalse(entry.sent)
        self.assertEqual(entry.thirdparty_reject, 'potato')

    @override_settings(
        CUSTOM_EMAIL_BACKENDS = (
            ('mybackend',
             'emails.tests.utils.EmailBackendMockSuccess',
             'emails.tests.utils.ResponseManagerStub'
            ),
        ),
        CUSTOM_DEFAULT_EMAIL_BACKEND = 'mybackend'
    )
    def test_schedule_with_metadata(self):
        EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )

        meta_fields = {
            'meta1': 'meta1value',
            'meta2': 'meta2value'
        }
        entry = schedule('my-test-email', 'es', {'meta_fields': meta_fields})
        email = send(entry)
        self.assertTrue(entry.sent)
        self.assertEqual(meta_fields, entry.metadata)
        self.assertEqual('meta1value', email.metadata['meta1'])
        self.assertIn('meta2value', email.metadata['meta2'])
