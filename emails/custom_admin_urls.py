from django.conf.urls import url

from emails.admin import (RenderView, SendView,
    RenderEntryView, EntryAttachmentsView)


urlpatterns = [
    url(r'^render/(?P<emailkind_id>[0-9]+)/$',
        RenderView.as_view(),
        name='render'),

    url(r'^send/(?P<emailkind_id>[0-9]+)/$',
        SendView.as_view(),
        name='send'),

    url(r'^renderentry/(?P<emailentry_id>[0-9]+)/(?P<version>html|plain)/$',
        RenderEntryView.as_view(),
        name='renderentry'),

    url(r'^emailentry/(?P<emailentry_id>[0-9]+)/attachments/$',
        EntryAttachmentsView.as_view(),
        name='attachs')
]
