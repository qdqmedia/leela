import collections
import logging
import base64
import datetime
from django.db import models, transaction
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from jsonfield import JSONField

# Ubuntu runs python programs with -O by default, which causes to
# remove all `assert` statements as long as `raise AssertionError()`.
# So we need a custom assert function to check params.

from emails.utils import custom_assert as cassert, EmailAssertionError


logger = logging.getLogger('emails')


class EmailKind(models.Model):
    """
    This model represents a kind of email. Created and configured manually
    through the admin panel.
    """
    MIN_NAME_LENGTH = 6

    name = models.CharField(max_length=255, verbose_name='email kind name')
    language = models.CharField(max_length=2, choices=settings.LANGUAGES,
                                default=settings.DEFAULT_LANGUAGE_CODE,
                                verbose_name='language')
    description = models.CharField(max_length=300, verbose_name='description',
                                   default='')
    template = models.TextField(verbose_name='template')
    plain_template = models.TextField(verbose_name='plain text template')
    default_context = JSONField(
        load_kwargs={'object_pairs_hook': collections.OrderedDict},
        blank=True, verbose_name='default template context', default={}
    )
    default_sender = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='default from (can be named format)'
    )
    default_recipients = models.TextField(
        blank=True,
        verbose_name='default to (comma separated, can be named format)'
    )
    default_subject = models.TextField(blank=True,
                                       verbose_name='default subject')
    default_reply_to = models.TextField(
        blank=True,
        verbose_name='default reply to (comma separated, can be named format)'
    )
    active = models.BooleanField(default=True, verbose_name='Is active')
    fragments = models.ManyToManyField(
        'EmailKindFragment',
        related_name='kinds',
        blank=True
    )

    model_name = 'EmailKind'

    class Meta:
        unique_together = ('name', 'language')
        ordering = ['name', 'language']

    def __str__(self):
        return '{}/{}'.format(self.name, self.language)

    def iter_all_images(self):
        for img in self.images.all():
            yield img
        for fragment in self.fragments.all():
            for img in fragment.images.all():
                yield img

    def generate_entry(self, params):
        """
        Creates and persists an EmailEntry given the current EmailKind.
        Checks that both the EmailKind and the params for EmailEntry are
        consistent.

        @type params **dict
        @param params Dictionary containing data to build the EmailEntry from
            the current EmailKind. Example:
            {
                'sender': 'from@qdqmedia.com',
                'recipients': ['to@qdqmedia.com', 'to2@qdqmedia.com', ...],
                'reply_to': ['reply@qdqmedia.com', 'reply2@qdqmedia.com', ...],
                'customer_id': '3838383',
                'subject': 'This is the email subject',
                'context': {'first_name': 'Troll', ...},
                'send_at': 1434029573, # Unix timestamp, UTC
                'check_url': 'http://myservice.qdqmedia.com/canisend/4983/323'
                'attachs': [{
                                'filename': 'invoice.pdf',
                                'content_type': 'application/pdf',
                                'content': 'raw content of the file'
                            }, ...]
            }
        """
        try:
            self.assert_well_formed()
            self.assert_sane_params(params)
        except EmailAssertionError as e:
            logger.exception("The EmailKind: {ek} is not well formed or was badly called with: {pa}"\
                .format(ek=self, pa=params))
            raise e

        context = params.get('context', None) or self.default_context
        sender = params.get('sender', None) or self.default_sender
        recipients = ','.join(params.get('recipients', [])) or \
                     self.default_recipients
        subject = params.get('subject', None) or self.default_subject
        reply_to = ','.join(params.get('reply_to', [])) or \
                   self.default_reply_to


        with transaction.atomic():
            entry = EmailEntry.objects.create(
                kind=self,
                customer_id=params.get('customer_id', ''),
                context=context,
                sender=sender,
                recipients=recipients,
                subject=subject,
                reply_to=reply_to,
                send_at=params.get('send_at', None),
                check_url=params.get('check_url', ''),
                backend=params.get('backend', ''),
                metadata=params.get('meta_fields', {}),
            )

            attachs = params.get('attachs', [])
            for attach in attachs:
                uploaded_file = SimpleUploadedFile(
                    attach['filename'],
                    give_me_bytes(base64.b64decode(attach['content'])),
                    attach['content_type']
                )
                Attachment.objects.create(entry=entry, attached_file=uploaded_file,
                                          content_type=attach['content_type'],
                                          name=attach['filename'])

        return entry

    def assert_well_formed(self):
        cassert(len(self.name) >= self.MIN_NAME_LENGTH,
                'kind: {}. too short name'.format(self))
        # TODO: Do something here when language policy is clear.
        # assert self.language in allowed_language_codes(), \
        #     'kind: {}. language not recognized'.format(self)
        cassert(len(self.template) > 0,
                'kind: {}. empty template'.format(self))
        cassert(len(self.plain_template) > 0,
                'kind: {}. empty plain template'.format(self))

    def assert_sane_params(self, params):
        cassert(self.default_sender or ('sender' in params and params['sender']),
                'kind: {}. sender never specified'.format(self))
        cassert(self.default_recipients or \
                ('recipients' in params and params['recipients'] and \
                 any(r for r in params['recipients'])),
                'kind: {}. recipients never specified'.format(self))
        cassert(self.default_subject or \
                ('subject' in params and params['subject']),
                'kind: {}. subject never specified'.format(self))

        if 'backend' in params:
            flattened_backends = sum(settings.CUSTOM_EMAIL_BACKENDS, ())
            cassert(
                params['backend'] in flattened_backends,
                'kind: {}. backend {} not known'.format(self, params['backend'])
            )


class EmailKindFragment(models.Model):
    """
    Represents a content fragment to be used in any EmailKind. Created and
    configured manually through admin.
    """
    name = models.CharField(
        max_length=255,
        verbose_name='content fragment name',
        unique=True
    )
    description = models.CharField(
        max_length=300,
        verbose_name='description',
        default=''
    )
    content = models.TextField(
        verbose_name='content'
    )
    is_plain = models.BooleanField(
        default=False,
        verbose_name='is plain',
        help_text='tells if the content is should be used in plain text'
    )
    default_context = JSONField(
        load_kwargs={'object_pairs_hook': collections.OrderedDict},
        blank=True,
        verbose_name='default template context',
        default={}
    )

    @property
    def template(self):
        if self.is_plain:
            raise ValueError(('"template" property cannot be used in plain '
                              'EmailKindFragment "{}"').format(self.name))
        return self.content

    @property
    def plain_template(self):
        if not self.is_plain:
            raise ValueError(('"plain_template" property cannot be used in not-plain '
                              'EmailKindFragment "{}"').format(self.name))
        return self.content

    def __str__(self):
        return '{} ({})'.format(self.name, 'plain' if self.is_plain else 'html')


class EmailEntry(models.Model):
    """
    This model represents a sent email. It's related to an EmailKind.
    So it can be understood like an instance (EmailEntry) of the class
    (EmailKind)

    It contains the data that is actually sent to the email backend.
    """
    kind = models.ForeignKey('EmailKind')
    send_at = models.IntegerField(null=True)
    sent = models.BooleanField(default=False, db_index=True)
    customer_id = models.CharField(max_length=30, blank=True,
                                   verbose_name='customer id')
    context = JSONField(
        load_kwargs={'object_pairs_hook': collections.OrderedDict},
        blank=True, verbose_name='template context', default={}
    )
    sender = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='from'
    )
    recipients = models.TextField(
        blank=True,
        verbose_name='to'
    )
    subject = models.TextField(blank=True, verbose_name='subject')
    reply_to = models.TextField(
        blank=True,
        verbose_name='reply to'
    )
    rendered_template = models.TextField(verbose_name='rendered template')
    rendered_plain_template = models.TextField(
        verbose_name='plain text template'
    )
    thirdparty_id = models.CharField(max_length=100, blank=True)
    thirdparty_reject = models.CharField(max_length=30, blank=True)
    datetime_sent = models.DateTimeField(null=True)
    datetime_scheduled = models.DateTimeField(auto_now_add=True, null=False)
    check_url = models.URLField(blank=True)
    deleted = models.BooleanField(default=False, db_index=True, verbose_name='Marked for deletion')
    is_spam = models.BooleanField(default=False, verbose_name='Marked as SPAM')
    backend = models.CharField(max_length=40, blank=True, verbose_name='Email Backend')
    metadata = JSONField(
        load_kwargs={'object_pairs_hook': collections.OrderedDict},
        blank=True, verbose_name='Email meta fields', default={}
    )

    model_name = 'EmailEntry'

    def __str__(self):
        return '{} - {}'.format(self.id, self.kind)


def get_attachment_filename(self, filename):
    """
    Calculates the file path of the attached file.
    """
    if self.entry.customer_id:
        path = 'attachs/{kind}/{lang}/{cust}_{filename}'.format(
            kind=self.entry.kind.name,
            lang=self.entry.kind.language,
            cust=self.entry.customer_id,
            filename=filename
        )
    else:
        path = 'attachs/{kind}/{lang}/{filename}'.format(
            kind=self.entry.kind.name,
            lang=self.entry.kind.language,
            filename=filename
        )
    return path


class Attachment(models.Model):
    """
    Represents an attachment of an email. It's relatated to an EmailEntry.
    """
    entry = models.ForeignKey('EmailEntry', related_name='attachments')
    attached_file = models.FileField(upload_to=get_attachment_filename)
    content_type = models.CharField(max_length=50)
    name = models.CharField(max_length=100)


def get_image_filename(self, filename):
    """
    Calculates the file path of the embedded image
    """
    path = 'images/{folder}/{filename}'.format(
        folder=self.folder,
        filename=filename
    )
    return path


class EmailImage(models.Model):
    """
    Represents an image embedded into an email template.
    """
    placeholder_name = models.CharField(max_length=100, blank=False)
    content_id = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to=get_image_filename)

    class Meta:
        abstract = True


class EmbeddedImage(EmailImage):
    """
    Represents an image embedded into an email template. It's related to
    an EmailKind.
    """
    kind = models.ForeignKey('EmailKind', related_name='images')

    class Meta:
        unique_together = ('kind', 'placeholder_name')
        ordering = ['kind', 'placeholder_name']

    @property
    def folder(self):
        return '{}/{}'.format(self.kind.name, self.kind.language)


class FragmentEmbeddedImage(EmailImage):
    """
    Represents an image embedded into any email template using an
    EmailKingFragment. It's related to an EmailKindFragment.
    """
    fragment = models.ForeignKey(
        'EmailKindFragment',
        related_name='images'
    )

    class Meta:
        unique_together = ('fragment', 'placeholder_name')
        ordering = ['fragment', 'placeholder_name']

    @property
    def folder(self):
        return 'fragments/{}'.format(self.fragment.name)


def give_me_bytes(string):
    """We want bytes, and only bytes"""
    return string.encode('utf8') if isinstance(string, str) else string
