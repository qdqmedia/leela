from rest_framework import serializers
from django.conf import settings

from emails.models import EmailEntry, Attachment, EmailKind


class AttachmentSerializer(serializers.HyperlinkedModelSerializer):
    entry = serializers.ReadOnlyField(source='entry.id')

    class Meta:
        model = Attachment
        fields = ('url', 'entry', 'attached_file', 'content_type', 'name')


class EmailEntrySerializer(serializers.HyperlinkedModelSerializer):
    attachments = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='attachment-detail'
    )
    kind_name = serializers.ReadOnlyField(source='kind.name')
    kind_language = serializers.ReadOnlyField(source='kind.language')
    render_link = serializers.SerializerMethodField('_render_link')

    class Meta:
        model = EmailEntry
        fields = ('url', 'id', 'kind_name', 'kind_language', 'send_at', 'sent',
                  'customer_id', 'sender', 'recipients', 'subject', 'reply_to',
                  'thirdparty_id', 'datetime_sent', 'check_url', 'deleted',
                  'attachments', 'render_link', 'datetime_scheduled', 'is_spam')

    @staticmethod
    def _render_link(obj):
        path = '/cadmin/renderentry/{id}/html/'.format(id=obj.id)
        return settings.CURRENT_HOST + path if obj.sent else None


class EmailKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailKind
        fields = ('name', 'language')
