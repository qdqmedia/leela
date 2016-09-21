import json
import logging

from django.contrib import admin
from django.views.generic import FormView, ListView, View
from django.forms import Form, IntegerField, CharField, Textarea
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.safestring import mark_safe

from .models import EmailKind, EmailEntry, Attachment, EmailKindFragment
from .models import EmbeddedImage, FragmentEmbeddedImage
from .render import render_html, render_plain
from .send import send


logger = logging.getLogger('admin')


##############
# MODELS
##############
class EmbeddedImageInline(admin.TabularInline):
    model = EmbeddedImage
    exclude = ('content_id',)


class FragmentEmbeddedImageInline(admin.TabularInline):
    model = FragmentEmbeddedImage
    exclude = ('content_id',)


FRAGMENTS_DESCRIPTION = mark_safe("""If an email kind fragment is included it can be referenced
with referenced with <b>{{ fragments.name }}</b>, where <i>name</i> is the fragment name.""")


class EmailKindAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'language', 'description']}),
        (None, {'fields': ['active']}),
        ('Templates', {'fields': ['template', 'plain_template']}),
        ('Defaults', {'fields': [
            'default_context', 'default_sender', 'default_recipients',
            'default_subject', 'default_reply_to'
        ]}),
        ('Fragments', {'fields': ['fragments'], 'description': FRAGMENTS_DESCRIPTION})
    ]
    inlines = [EmbeddedImageInline]
    filter_horizontal = ('fragments',)
    list_filter = ('active',)
    search_fields = ['name']


class EmailKindFragmentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'description', 'is_plain']}),
        ('Content', {'fields': ['content']}),
        ('Defaults', {'fields': ['default_context']})
    ]
    inlines = [FragmentEmbeddedImageInline]
    search_fields = ['name']

    def _warn_about_related_kinds(self, request, obj):
        if request.method == 'GET' and obj.kinds.count() > 0:

            def _kind_link(kind):
                return '<a href="{url}">{name}/{lang}</a>'.format(
                    name=kind.name,
                    lang=kind.language,
                    url=reverse('admin:emails_emailkind_change', args=(kind.pk,)))

            message = (
                'Changing this fragment will affect the following email'
                'kinds: {}</b>').format(', '.join(map(_kind_link, obj.kinds.all())))
            messages.warning(request, mark_safe(message))

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self._warn_about_related_kinds(request, obj)
        return super().get_form(request, obj=obj, **kwargs)


class EmailEntryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'datetime_sent')
    readonly_fields = ('kind', 'send_at', 'sent', 'is_spam', 'customer_id',
                       'sender', 'recipients', 'subject', 'reply_to',
                       'backend', 'thirdparty_id', 'thirdparty_reject',
                       'check_url', 'deleted', 'datetime_sent',
                       'datetime_scheduled')

    list_filter = ('sent', 'is_spam')
    search_fields = ['kind__name', 'customer_id', 'recipients', 'subject',
                     'thirdparty_id']


admin.site.register(EmailKind, EmailKindAdmin)
admin.site.register(EmailKindFragment, EmailKindFragmentAdmin)
admin.site.register(EmailEntry, EmailEntryAdmin)


# ##############
# VIEWS
# ##############
class RenderForm(Form):
    emailkind_id = IntegerField()
    test_context = CharField(initial='{}', required=False, widget=Textarea)
    operation = CharField(max_length=12)

    def render(self):
        operation = self.cleaned_data['operation']
        if operation == 'Render plain':
            return self._get_plain_response()
        else:
            return self._get_html_response()

    def _get_html_response(self):
        emailkind_id = self.cleaned_data['emailkind_id']
        test_context = json.loads(self.cleaned_data['test_context'])
        emailkind = EmailKind.objects.get(id=emailkind_id)
        response = HttpResponse(
            render_html(emailkind, test_context, test=True),
            content_type='text/html'
        )
        return response

    def _get_plain_response(self):
        emailkind_id = self.cleaned_data['emailkind_id']
        test_context = json.loads(self.cleaned_data['test_context'])
        emailkind = EmailKind.objects.get(id=emailkind_id)
        response = HttpResponse(
            render_plain(emailkind, test_context),
            content_type='text/plain'
        )
        return response


class RenderView(FormView):
    template_name = 'admin/renderform.html'
    form_class = RenderForm
    emailkind = None

    def get_context_data(self, **kwargs):
        kwargs['emailkind'] = self.emailkind
        return super(RenderView, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.emailkind = get_object_or_404(EmailKind,
                                           id=kwargs['emailkind_id'])
        return super(RenderView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        return form.render()


class SendForm(Form):
    emailkind_id = IntegerField()
    test_params = CharField(initial='{}', required=False, widget=Textarea)

    def send_test(self):
        emailkind_id = self.cleaned_data['emailkind_id']
        test_params = json.loads(self.cleaned_data['test_params'])

        emailkind = EmailKind.objects.get(id=emailkind_id)
        entry = emailkind.generate_entry(test_params)
        send(entry) ## Will send twice with this line and the above
        return entry.sent


class SendView(FormView):
    template_name = 'admin/sendform.html'
    form_class = SendForm
    emailkind = None
    success_url = None

    def get_context_data(self, **kwargs):
        kwargs['emailkind'] = self.emailkind
        return super(SendView, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.emailkind = get_object_or_404(EmailKind,
                                           id=kwargs['emailkind_id'])
        return super(SendView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.emailkind = get_object_or_404(EmailKind,
                                           id=kwargs['emailkind_id'])
        return super(SendView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        if form.send_test():
            messages.add_message(self.request, messages.INFO, 'Test sent correctly.')
        else:
            messages.add_message(self.request, messages.ERROR, 'Test could not be sent.')
        return super(SendView, self).form_valid(form)

    def get_success_url(self):
        return reverse('cadmin:send', args=[self.emailkind.id])


class RenderEntryView(View):
    def get(self, request, *args, **kwargs):
        entry = get_object_or_404(EmailEntry, id=kwargs['emailentry_id'])
        if kwargs['version'] == 'html':
            images = entry.kind.iter_all_images()
            response = HttpResponse(
                self.__revert_content_ids(entry.rendered_template, images),
                content_type='text/html'
            )
        else:
            response = HttpResponse(
                entry.rendered_plain_template,
                content_type='text/plain;charset=utf-8'
            )
        return response

    def __revert_content_ids(self, template, images):
        for image in images:
            content_id_src = 'src="cid:{cid}"'.format(cid=image.content_id[1:-1])
            browser_src = 'src="{url}"'.format(url=image.image.url)
            template = template.replace(content_id_src, browser_src)
        return template


class EntryAttachmentsView(ListView):
    entry_id = None
    queryset = Attachment.objects.all()
    template_name = 'admin/attach_list.html'

    def get_queryset(self):
        return self.queryset.filter(entry_id=self.entry_id)

    def get_context_data(self, **kwargs):
        kwargs['entry_id'] = self.entry_id
        return super(EntryAttachmentsView, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        self.entry_id = kwargs['emailentry_id']
        return super(EntryAttachmentsView, self).get(request, *args, **kwargs)
