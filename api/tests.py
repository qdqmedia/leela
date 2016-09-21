import json
import base64
from unittest import mock
from django.test import TestCase
from django.core.urlresolvers import reverse

from emails.models import EmailKind, EmailEntry, Attachment
from emails.tests.utils import get_jpg_content


class LeelaApiTestCase(TestCase):
    def parse_response_content(self, response):
        return json.loads(response.content.decode('utf8'))

class EntriesTest(LeelaApiTestCase):

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

    def tearDown(self):
        EmailKind.objects.all().delete()
        EmailEntry.objects.all().delete()

    def test_entries_list_empty(self):
        response = self.client.get(reverse('emailentry-list'))
        content = self.parse_response_content(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, content['count'])
        self.assertIsNone(content['next'])
        self.assertIsNone(content['previous'])
        self.assertEqual([], content['results'])

    def test_entries_list_some(self):
        entry_params = {}
        self.ekind.generate_entry(entry_params)
        self.ekind.generate_entry(entry_params)
        self.ekind.generate_entry(entry_params)

        response = self.client.get(reverse('emailentry-list'))
        content = self.parse_response_content(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual(3, content['count'])
        self.assertIsNone(content['next'])
        self.assertIsNone(content['previous'])
        self.assertEqual(3, len(content['results']))

    def test_entries_detail_not_found(self):
        response = self.client.get(reverse('emailentry-detail', args=[3]))
        content = self.parse_response_content(response)
        self.assertEqual(404, response.status_code)
        self.assertEqual('Not found.', content['detail'])

    def test_entries_detail_exists(self):
        entry_params = {}
        entry = self.ekind.generate_entry(entry_params)

        response = self.client.get(reverse('emailentry-detail', args=[entry.pk]))
        content = self.parse_response_content(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual(content['id'], entry.pk)

    def test_entries_detail_with_attachments(self):
        image_content = get_jpg_content()
        text_content = b'Some text\nHere in the carabanchel\nthugh life.'
        entry_params = {
            'attachs': [
                {
                    'filename': 'test.jpg',
                    'content_type': 'image/jpeg',
                    'content': base64.b64encode(image_content)
                },
                {
                    'filename': 'sss.txt',
                    'content_type': 'text/plain',
                    'content': base64.b64encode(text_content)
                }
            ]
        }
        entry = self.ekind.generate_entry(entry_params)
        response = self.client.get(reverse('emailentry-detail', args=[entry.pk]))
        content = self.parse_response_content(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(content['attachments']))

    def test_filter_include_kinds(self):
        ekind1 = EmailKind.objects.create(
            name='my-first-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        entry_params1 = {'customer_id': '11111111'}
        ekind1.generate_entry(entry_params1)
        ekind1.generate_entry(entry_params1)
        entry_params2 = {'customer_id': '22222222'}
        ekind1.generate_entry(entry_params2)
        
        ekind2 = EmailKind.objects.create(
            name='my-other-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        ekind2.generate_entry(entry_params1)
        ekind2.generate_entry(entry_params2)

        ekind3 = EmailKind.objects.create(
            name='my-third-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        ekind3.generate_entry(entry_params1)

        response = self.client.get(
            reverse('emailentry-list') +
            '?customer_id=11111111&include_kinds=my-first-email,my-other-email'
        )
        self.assertEqual(200, response.status_code)

        content = self.parse_response_content(response)
        self.assertEqual(3, content['count'])

    def test_filter(self):
        entry_params = {}
        entry1 = self.ekind.generate_entry(entry_params)
        entry2 = self.ekind.generate_entry(entry_params)
        entry3 = self.ekind.generate_entry(entry_params)

        middle_id = entry2.id

        gt_response = self.client.get(reverse('emailentry-list') + '?id__gt={}'.format(middle_id))
        gte_response = self.client.get(reverse('emailentry-list') + '?id__gte={}'.format(middle_id))
        lt_response = self.client.get(reverse('emailentry-list') + '?id__lt={}'.format(middle_id))
        lte_response = self.client.get(reverse('emailentry-list') + '?id__lte={}'.format(middle_id))

        self.assertEqual(200, gt_response.status_code)
        self.assertEqual(200, gte_response.status_code)
        self.assertEqual(200, lt_response.status_code)
        self.assertEqual(200, lte_response.status_code)

        lt_content = self.parse_response_content(lt_response)
        lte_content = self.parse_response_content(lte_response)
        gt_content = self.parse_response_content(gt_response)
        gte_content = self.parse_response_content(gte_response)

        self.assertEqual(1, lt_content['count'])
        self.assertEqual(2, lte_content['count'])
        self.assertEqual(1, gt_content['count'])
        self.assertEqual(2, gte_content['count'])

        lt_result_ids = set([result['id'] for result in lt_content['results']])
        lte_result_ids = set([result['id'] for result in lte_content['results']])
        gt_result_ids = set([result['id'] for result in gt_content['results']])
        gte_result_ids = set([result['id'] for result in gte_content['results']])

        self.assertEqual({entry1.id}, lt_result_ids)
        self.assertEqual({entry1.id, entry2.id}, lte_result_ids)
        self.assertEqual({entry3.id}, gt_result_ids)
        self.assertEqual({entry3.id, entry2.id}, gte_result_ids)


class AttachTests(LeelaApiTestCase):

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

    def tearDown(self):
        EmailKind.objects.all().delete()
        EmailEntry.objects.all().delete()
        Attachment.objects.all().delete()

    def test_attachs_list_empty(self):
        response = self.client.get(reverse('attachment-list'))
        content = self.parse_response_content(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, content['count'])
        self.assertIsNone(content['next'])
        self.assertIsNone(content['previous'])
        self.assertEqual([], content['results'])

    def test_attachs_list_some(self):
        image_content = get_jpg_content()
        text_content = b'Some text\nHere in the carabanchel\nthugh life.'
        entry_params = {
            'attachs': [
                {
                    'filename': 'test.jpg',
                    'content_type': 'image/jpeg',
                    'content': base64.b64encode(image_content)
                },
                {
                    'filename': 'sss.txt',
                    'content_type': 'text/plain',
                    'content': base64.b64encode(text_content)
                }
            ]
        }
        self.ekind.generate_entry(entry_params)

        response = self.client.get(reverse('attachment-list'))
        content = self.parse_response_content(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, content['count'])
        self.assertIsNone(content['next'])
        self.assertIsNone(content['previous'])
        self.assertEqual(2, len(content['results']))

    def test_attachs_detail_not_found(self):
        response = self.client.get(reverse('attachment-detail', args=[5]))
        content = self.parse_response_content(response)
        self.assertEqual(404, response.status_code)
        self.assertEqual('Not found.', content['detail'])

    def test_attachs_detail_exist(self):
        text_content = b'Some text\nHere in the carabanchel\nthugh life.'
        entry_params = {
            'attachs': [
                {
                    'filename': 'sss.txt',
                    'content_type': 'text/plain',
                    'content': base64.b64encode(text_content)
                }
            ]
        }
        entry = self.ekind.generate_entry(entry_params)
        attach = entry.attachments.first()

        response = self.client.get(reverse('attachment-detail',
                                           args=[attach.pk]))
        content = self.parse_response_content(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual(entry.id, content['entry'])
        self.assertEqual('text/plain', content['content_type'])
        self.assertEqual('sss.txt', content['name'])
        self.assertNotEqual(0, len(content['attached_file']))

        response_attach_content = self.client.get(content['attached_file'])
        attach_content = b''
        for chunk in response_attach_content.streaming_content:
            attach_content += chunk
        self.assertEqual(text_content, attach_content)


class HealthCheckTest(TestCase):
    def test_healt_check_ok(self):
        response = self.client.get('/api/healthcheck/')
        self.assertEqual(200, response.status_code)
        self.assertEqual(b'Everything up and running.', response.content)
