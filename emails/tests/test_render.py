import re
from unittest import TestCase, mock

from django.test import override_settings

from emails.models import EmailKind, EmbeddedImage, EmailKindFragment
from emails.render import render_html, render_plain, _minify_html
from emails.tests.utils import create_upload_image


class RenderTest(TestCase):

    def tearDown(self):
        EmailKind.objects.all().delete()
        EmailKindFragment.objects.all().delete()

    def test_render_html_no_default_context(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
        )
        rendered = render_html(ekind, {'first_name': 'Luisa'})
        self.assertEqual('<h1>Hola, Luisa</h1>', rendered)

    def test_render_html_no_context_needed(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, Luisa</h1>',
            plain_template='Hola, Luisa',
        )
        rendered = render_html(ekind, {})
        self.assertEqual('<h1>Hola, Luisa</h1>', rendered)

    def test_render_html_default_context_used(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
            default_context={'first_name': 'Luisa'}
        )
        rendered = render_html(ekind, {})
        self.assertEqual('<h1>Hola, Luisa</h1>', rendered)

    def test_render_html_default_context_override(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
            default_context={'first_name': 'Luisa'}
        )
        rendered = render_html(ekind, {'first_name': 'Matias'})
        self.assertEqual('<h1>Hola, Matias</h1>', rendered)

    def test_render_html_meta_context(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}. Kind: {{ meta.name }}</h1>',
            plain_template='Hola, {{ first_name }}',
            default_context={'first_name': 'Luisa'}
        )
        rendered = render_html(ekind, {'first_name': 'Matias'})
        self.assertEqual('<h1>Hola, Matias. Kind: my-test-email</h1>', rendered)

    def test_render_html_not_enough_context(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
        )
        rendered = render_html(ekind, {})
        self.assertEqual('<h1>Hola, </h1>', rendered)

    def test_render_html_with_embedded_images_testing_false(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template=('<h1>Hola, {{ first_name }}</h1>'
                      '<img src="cid:logo-solocal">'
                      '<img src="cid:logo-qdq">'),
            plain_template='Hola, {{ first_name }}',
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
        image1 = EmbeddedImage.objects.get(kind=ekind,
                                           placeholder_name='logo-solocal')
        self.assertEqual('', image1.content_id)

        rendered = render_html(ekind, {})
        image1 = EmbeddedImage.objects.get(kind=ekind,
                                           placeholder_name='logo-solocal')
        self.assertIn('src="cid:', rendered)
        self.assertNotIn('src="cid:<', rendered)
        self.assertIn('logo-solocal@', rendered)
        self.assertIn('logo-qdq@', rendered)
        self.assertTrue(len(image1.content_id) > 0)

    def test_render_html_with_embedded_images_testing_true(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template=('<h1>Hola, {{ first_name }}</h1>'
                      '<img src="cid:logo-solocal">'
                      '<img src="cid:logo-qdq">'),
            plain_template='Hola, {{ first_name }}',
            default_context={'first_name': 'Luisa'}
        )
        upload_image1 = create_upload_image()
        upload_image2 = create_upload_image()
        image1 = EmbeddedImage.objects.create(
            kind=ekind,
            placeholder_name='logo-solocal',
            image=upload_image1
        )
        image2 = EmbeddedImage.objects.create(
            kind=ekind,
            placeholder_name='logo-qdq',
            image=upload_image2
        )
        rendered = render_html(ekind, {}, test=True)
        self.assertIn(image1.image.url, rendered)
        self.assertIn(image2.image.url, rendered)

    def test_render_plain_no_default_context(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
        )
        rendered = render_plain(ekind, {'first_name': 'Luisa'})
        self.assertEqual('Hola, Luisa', rendered)

    def test_render_plain_no_context_needed(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, Luisa</h1>',
            plain_template='Hola, Luisa',
        )
        rendered = render_plain(ekind, {})
        self.assertEqual('Hola, Luisa', rendered)

    def test_render_plain_default_context_used(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
            default_context={'first_name': 'Luisa'}
        )
        rendered = render_plain(ekind, {})
        self.assertEqual('Hola, Luisa', rendered)

    def test_render_plain_default_context_override(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
            default_context={'first_name': 'Luisa'}
        )
        rendered = render_plain(ekind, {'first_name': 'Matias'})
        self.assertEqual('Hola, Matias', rendered)

    def test_render_plain_not_enough_context(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
        )
        rendered = render_plain(ekind, {})
        self.assertEqual('Hola, ', rendered)

    def test_render_html_fragment(self):
        fkind = EmailKindFragment.objects.create(
            name='throne-fragment',
            content='<h1>I am {{ name }} and I rule {{ kingdom }}</h1>',
            default_context={'name': 'Cersei Lannister'},
            is_plain=False
        )
        context = {'kingdom': 'Kingslanding'}
        rendered = render_html(fkind, context)
        self.assertEqual('<h1>I am Cersei Lannister and I rule Kingslanding</h1>', rendered)

    def test_render_plain_fragment(self):
        fkind = EmailKindFragment.objects.create(
            name='throne-fragment',
            content='I am {{ name }} and I rule {{ kingdom }}',
            default_context={'name': 'Cersei Lannister'},
            is_plain=True
        )
        context = {'kingdom': 'Kingslanding'}
        rendered = render_plain(fkind, context)
        self.assertEqual('I am Cersei Lannister and I rule Kingslanding', rendered)

    def test_render_html_with_fragments(self):
        header = EmailKindFragment.objects.create(
            name='header',
            content='<title>Hello {{ name }}. {{ sentence }}</title>',
            default_context={'name': 'Yo'},
            is_plain=False
        )
        footer = EmailKindFragment.objects.create(
            name='footer',
            content='<div>{{ smiley }}</div>',
            default_context={'smiley': '^_^'},
            is_plain=False
        )
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='{{ fragments.header }}<h1>Hola, {{ name }}</h1>{{ fragments.footer }}',
            plain_template='Hola, {{ name }}',
            default_context={'name': 'Manola'}
        )
        ekind.fragments.add(header)
        ekind.fragments.add(footer)
        context = {'sentence': 'How are you?'}
        rendered = render_html(ekind, context)
        self.assertEqual(
            '<title>Hello Manola. How are you?</title><h1>Hola, Manola</h1><div>^_^</div>',
            rendered
        )
        rendered_plain = render_plain(ekind, context)
        self.assertEqual(rendered_plain, 'Hola, Manola')

    def test_render_html_fragments_with_images(self):
        header = EmailKindFragment.objects.create(
            name='header',
            content='<div>Hello {{ name }}</div><img src="cid:logo">',
            default_context={'name': 'Yo'},
            is_plain=False
        )
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='{{ fragments.header }}<h1>{{ sentence }}</h1><img src="cid:other">',
            plain_template='Hola, {{ name }}',
            default_context={'name': 'Bran'}
        )
        logo = create_upload_image()
        header.images.create(placeholder_name='logo', image=logo)
        other = create_upload_image()
        ekind.images.create(placeholder_name='other', image=other)
        ekind.fragments.add(header)
        context = {'sentence': 'Hold the door!'}
        rendered = render_html(ekind, context)
        self.assertEqual(re.sub('<img.*?>', '', rendered),
                         '<div>Hello Bran</div><h1>Hold the door!</h1>')
        imgs = re.findall(r'<img\s+src="(?P<img>.*?)"', rendered)
        self.assertEqual(len(imgs), 2)
        logo_src, other_src = imgs
        self.assertTrue(logo_src.startswith('cid:'))
        self.assertTrue(other_src.startswith('cid:'))
        self.assertIn('logo@', logo_src)
        self.assertIn('other@', other_src)

    def test_render_html_fragments_with_images_test_true(self):
        header = EmailKindFragment.objects.create(
            name='header',
            content='<div>Hello {{ name }}</div><img src="cid:logo">',
            default_context={'name': 'Yo'},
            is_plain=False
        )
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='{{ fragments.header }}<h1>{{ sentence }}</h1><img src="cid:other">',
            plain_template='Hola, {{ name }}',
            default_context={'name': 'Bran'}
        )
        logo = create_upload_image()
        logo_img = header.images.create(placeholder_name='logo', image=logo)
        other = create_upload_image()
        other_img = ekind.images.create(placeholder_name='other', image=other)
        ekind.fragments.add(header)
        context = {'sentence': 'Hold the door!'}
        rendered = render_html(ekind, context, test=True)
        self.assertEqual(re.sub('<img.*?>', '', rendered),
                         '<div>Hello Bran</div><h1>Hold the door!</h1>')
        imgs = re.findall(r'<img\s+src="(?P<img>.*?)"', rendered)
        self.assertEqual(len(imgs), 2)
        logo_src, other_src = imgs
        self.assertEqual(logo_img.image.url, logo_src)
        self.assertEqual(other_img.image.url, other_src)

    def test_render_plain_with_fragments(self):
        fragment = EmailKindFragment.objects.create(
            name='question',
            content='What is {{ who }} name?',
            default_context={'who': 'the girl'},
            is_plain=True
        )
        ekind = EmailKind.objects.create(
            name='test-email',
            language='es',
            template='<div>{{ answer }}</div>',
            plain_template='{{ fragments.question }} {{ answer }}',
            default_context={'answer': 'Arya Stark'}
        )
        context = {'answer': 'The girl is no one'}
        ekind.fragments.add(fragment)
        rendered = render_plain(ekind, context)
        self.assertEqual('What is the girl name? The girl is no one', rendered)

        rendered_html = render_html(ekind, context)
        self.assertEqual('<div>The girl is no one</div>', rendered_html)

    @override_settings(MINIFY_HTML=True)
    def test_render_active_html_minification(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
        )

        with mock.patch('emails.render._minify_html') as _minify_html:
            rendered = render_html(ekind, {'first_name': 'Luisa'})
            _minify_html.assert_any_call(mock.ANY)
            self.assertEqual(rendered, _minify_html.return_value)
            _minify_html.reset()

        with mock.patch('emails.render._minify_html') as _minify_html:
            rendered = render_html(ekind, {'first_name': 'Luisa'}, ignore_minify=True)
            self.assertFalse(_minify_html.called)
            self.assertNotEqual(rendered, _minify_html.return_value)

    @override_settings(MINIFY_HTML=False)
    def test_render_not_active_html_minification(self):
        ekind = EmailKind.objects.create(
            name='my-test-email',
            language='es',
            template='<h1>Hola, {{ first_name }}</h1>',
            plain_template='Hola, {{ first_name }}',
        )
        with mock.patch('emails.render._minify_html') as _minify_html:
            rendered = render_html(ekind, {'first_name': 'Luisa'})
            self.assertFalse(_minify_html.called)
            self.assertNotEqual(rendered, _minify_html.return_value)


class MinifyHtmlTestCase(TestCase):

    def test_whitespace(self):
        html = """
        <div         class =        "test"

        >
            <p>
                <a href="#">A word</a> <span>Other</span>
            </p>
                </div>"""
        minified = _minify_html(html)
        self.assertEqual(
            minified,
            '<div class="test"> <p> <a href="#">A word</a> <span>Other</span> </p> </div>')

    def test_remove_comments(self):
        html = """
        <!-- A very cool
                    comment -->
        <span>Hello</span> <!-- Other comment -->
        <span>Yo!</span>
        """
        minified = _minify_html(html)
        self.assertEqual(
            minified,
            '<span>Hello</span> <span>Yo!</span>')

    def test_keep_tag_attributes(self):
        # We need to be extra-careful with tag attributes, see htmlmin issues: #32 and #33
        # <https://github.com/mankyd/htmlmin/issues>
        html = """
        <img cid="cid:logo-solocal" style="background-color:#FFFFFF" visible="true"
             data-stuff="=!?<">
        """
        minified = _minify_html(html)
        self.assertEqual(
            minified,
            '<img cid="cid:logo-solocal" style="background-color:#FFFFFF" visible="true" data-stuff="=!?<">')
