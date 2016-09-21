import base64
from unittest import TestCase, skip
from unittest import mock
from unittest.mock import Mock

from emails.models import EmailKind, EmailEntry, EmailKindFragment
from emails.models import EmbeddedImage, FragmentEmbeddedImage, get_image_filename
from emails.tests.utils import create_upload_image
from emails.utils import EmailAssertionError


class EmailKindTest(TestCase):

    def tearDown(self):
        EmailKind.objects.all().delete()
        EmbeddedImage.objects.all().delete()

    def test_email_with_no_defaults_no_context(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )

        self.assertEqual('my-test-email', ekind.name)
        self.assertEqual('es', ekind.language)
        self.assertEqual('Hello, world!', ekind.template)
        self.assertEqual('Hello, world! soy antiguo', ekind.plain_template)

    def test_email_with_all_defaults_some_context(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_context={'a': 'b', '1': '2'},
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )

        self.assertEqual('my-test-email', ekind.name)
        self.assertEqual('es', ekind.language)
        self.assertEqual('Hello, world!', ekind.template)
        self.assertEqual('Hello, world! soy antiguo', ekind.plain_template)
        self.assertEqual({'a': 'b', '1': '2'}, ekind.default_context)
        self.assertEqual('trololo@qdqmedia.com', ekind.default_sender)
        self.assertEqual('cliente@gemilio.com', ekind.default_recipients)
        self.assertEqual('Email Test', ekind.default_subject)
        self.assertEqual('atecli@qdqmedia.com', ekind.default_reply_to)

    def test_email_with_embedded_images(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )
        uploaded_image = create_upload_image()
        embedded_image = EmbeddedImage.objects.create(
            kind=ekind,
            placeholder_name='placeholder',
            image=uploaded_image
        )
        images = ekind.images.all()
        self.assertEqual(1, len(images))
        self.assertEqual(embedded_image.image.path, images[0].image.path)
        self.assertEqual(embedded_image.placeholder_name, images[0].placeholder_name)

    def test_assert_well_formed_ok(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )
        ekind.assert_well_formed()

    def test_assert_well_formed_fail_name(self):
        ekind = EmailKind.objects.create(
            name='my-te',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )
        self.assertRaises(EmailAssertionError, ekind.assert_well_formed)

    @skip('TODO: Do something here when language policy is clear.')
    def test_assert_well_formed_fail_language(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='ru',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )
        self.assertRaises(EmailAssertionError, ekind.assert_well_formed)

    def test_assert_well_formed_fail_template(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            plain_template='Hello, world! soy antiguo',
        )
        self.assertRaises(EmailAssertionError, ekind.assert_well_formed)

    def test_assert_well_formed_fail_plain_template(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='',
        )
        self.assertRaises(EmailAssertionError, ekind.assert_well_formed)

    def test_assert_sane_params_all_default_ok(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_context={'a': 'b', '1': '2'},
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        ekind.assert_sane_params({})

    def test_assert_sane_params_no_defaults_ok(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )
        entry_params = {
            'sender': 'trololo@qdqmedia.com',
            'recipients': ['trelele@qdqmedia.com'],
            'subject': 'JAJAJAJA'
        }
        ekind.assert_sane_params(entry_params)

    def test_assert_sane_params_no_sender_fail(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )
        entry_params = {
            'recipients': ['trelele@qdqmedia.com'],
            'subject': 'JAJAJAJA'
        }
        self.assertRaises(EmailAssertionError,
                          ekind.assert_sane_params, entry_params)

    def test_assert_sane_params_no_recipients_fail(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )
        entry_params = {
            'sender': 'trololo@qdqmedia.com',
            'subject': 'JAJAJAJA'
        }
        self.assertRaises(EmailAssertionError,
                          ekind.assert_sane_params, entry_params)

    def test_assert_sane_params_no_subject_fail(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )
        entry_params = {
            'sender': 'trololo@qdqmedia.com',
            'recipients': ['trelele@qdqmedia.com'],
        }
        self.assertRaises(EmailAssertionError,
                          ekind.assert_sane_params, entry_params)


class GenerateEntryTest(TestCase):

    def tearDown(self):
        EmailKind.objects.all().delete()
        EmailEntry.objects.all().delete()

    def test_entry_use_all_defaults_no_attachs(self):
        ekind = EmailKind.objects.create(
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

        eentry = ekind.generate_entry(entry_params)
        self.assertEqual(ekind, eentry.kind)
        self.assertEqual('', eentry.customer_id)
        self.assertEqual({}, eentry.context)
        self.assertEqual(ekind.default_sender, eentry.sender)
        self.assertEqual(ekind.default_recipients, eentry.recipients)
        self.assertEqual(ekind.default_subject, eentry.subject)
        self.assertEqual(ekind.default_reply_to, eentry.reply_to)
        self.assertFalse(eentry.sent)
        self.assertIsNone(eentry.send_at)

    def test_entry_override_all_defaults_no_attachs(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )

        entry_params = {
            'customer_id': '08838234',
            'sender': 'donpinpon@qdqmedia.com',
            'recipients': ['cliente2@gemailio.com'],
            'subject': 'Alta nueva',
            'reply_to': ['noreply@qdqmedia.com']
        }

        eentry = ekind.generate_entry(entry_params)
        self.assertEqual(ekind, eentry.kind)
        self.assertEqual('08838234', eentry.customer_id)
        self.assertEqual({}, eentry.context)
        self.assertEqual('donpinpon@qdqmedia.com', eentry.sender)
        self.assertEqual('cliente2@gemailio.com', eentry.recipients)
        self.assertEqual('Alta nueva', eentry.subject)
        self.assertEqual('noreply@qdqmedia.com', eentry.reply_to)
        self.assertFalse(eentry.sent)
        self.assertIsNone(eentry.send_at)

    def test_entry_use_all_defaults_with_all_attachs(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
            default_sender='trololo@qdqmedia.com',
            default_recipients='cliente@gemilio.com',
            default_subject='Email Test',
            default_reply_to='atecli@qdqmedia.com'
        )
        entry_params = {
            'attachs': [
                {
                    'filename': 'file1.txt',
                    'content_type': 'text/plain',
                    'content': base64.b64encode(b'Hola')
                },
                {
                    'filename': 'file2.txt',
                    'content_type': 'text/plain',
                    'content': base64.b64encode(b'Adios')
                },
                {
                    'filename': 'file3.txt',
                    'content_type': 'text/plain',
                    'content': base64.b64encode(b'LLALLAA')
                },
                {
                    'filename': 'file4.txt',
                    'content_type': 'text/plain',
                    'content': base64.b64encode(b'EKEKEKEK')
                },
                {
                    'filename': 'file5.txt',
                    'content_type': 'text/plain',
                    'content': base64.b64encode(b'Bluf')
                }
            ]
        }

        eentry = ekind.generate_entry(entry_params)
        self.assertEqual(ekind, eentry.kind)
        self.assertEqual('', eentry.customer_id)
        self.assertEqual({}, eentry.context)
        self.assertEqual(ekind.default_sender, eentry.sender)
        self.assertEqual(ekind.default_recipients, eentry.recipients)
        self.assertEqual(ekind.default_subject, eentry.subject)
        self.assertEqual(ekind.default_reply_to, eentry.reply_to)
        self.assertEqual(5, len(eentry.attachments.all()))
        self.assertFalse(eentry.sent)
        self.assertIsNone(eentry.send_at)

    def test_entry_no_defaults_empty_recipients(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='Hello, world!',
            plain_template='Hello, world! soy antiguo',
        )

        entry_params = {
            'sender': 'trololo@qdqmedia.com',
            'recipients': [''],
            'subject': 'Email Test',
            'reply_to': 'atecli@qdqmedia.com'
        }

        self.assertRaises(EmailAssertionError, ekind.generate_entry, entry_params)

    def test_iter_all_images(self):
        f1 = EmailKindFragment.objects.create(name='f1')
        f2 = EmailKindFragment.objects.create(name='f2')
        ekind = EmailKind.objects.create(name='ekind', language='es')
        ekind.fragments.add(f1)
        ekind.fragments.add(f2)
        f1.images.create(placeholder_name='f1.1', image=create_upload_image())
        f1.images.create(placeholder_name='f1.2', image=create_upload_image())
        f2.images.create(placeholder_name='f2.1', image=create_upload_image())
        f2.images.create(placeholder_name='f2.2', image=create_upload_image())
        ekind.images.create(placeholder_name='ekind.1', image=create_upload_image())
        ekind.images.create(placeholder_name='ekind.2', image=create_upload_image())
        all_images = list(ekind.iter_all_images())
        self.assertEqual(len(all_images), 6)
        self.assertEqual({img.placeholder_name for img in all_images},
                         {'f1.1', 'f1.2', 'f2.1', 'f2.2', 'ekind.1', 'ekind.2'})


class EmailKindFragmentTestCase(TestCase):

    def test_template_property(self):
        fragment = EmailKindFragment()
        fragment.content = ';-)'
        fragment.is_plain = False
        self.assertEqual(fragment.template, fragment.content)
        fragment.is_plain = True
        with self.assertRaises(ValueError):
            fragment.template

    def test_plain_template_property(self):
        fragment = EmailKindFragment()
        fragment.content = ';-)'
        fragment.is_plain = True
        self.assertEqual(fragment.plain_template, fragment.content)
        fragment.is_plain = False
        with self.assertRaises(ValueError):
            fragment.plain_template


class EmbeddedImageTestCase(TestCase):

    def test_embedded_image_folder(self):
        ei = EmbeddedImage()
        with mock.patch.object(EmbeddedImage, 'kind'):
            ei.kind.name = 'jake'
            ei.kind.language = 'es'
            self.assertEqual(ei.folder, 'jake/es')

    def test_fragment_embedded_image_folder(self):
        fei = FragmentEmbeddedImage()
        with mock.patch.object(FragmentEmbeddedImage, 'fragment'):
            fei.fragment.name = 'finn'
            self.assertEqual(fei.folder, 'fragments/finn')

    def test_get_email_filename(self):
        img = Mock(folder='a/folder')
        self.assertEqual(get_image_filename(img, 'pic.png'), 'images/a/folder/pic.png')
