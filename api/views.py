import django_filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets, filters

from django.http import HttpResponse

from emails.models import EmailEntry, Attachment
from api.serializers import EmailEntrySerializer, AttachmentSerializer


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'entries': reverse('emailentry-list', request=request, format=format),
        'attachs': reverse('attachments-list', request=request, format=format),
    })


class EmailEntryFilter(django_filters.FilterSet):

    class Meta:
        model = EmailEntry
        fields = {'id': ['exact', 'gte', 'gt', 'lte', 'lt'],
                  'customer_id': ['exact'],
                  'sent': ['exact']}


class EmailEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailEntry.objects.all()
    serializer_class = EmailEntrySerializer
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = EmailEntryFilter
    ordering_fields = ('id', 'customer_id')

    def get_queryset(self):
        queryset = super(EmailEntryViewSet, self).get_queryset()
        queryset = self.filter_include_kinds(queryset)
        return queryset

    def filter_include_kinds(self, queryset):
        kinds_param = self.request.query_params.get('include_kinds', None)
        if kinds_param:
            kinds_list = kinds_param.split(',')
            queryset = queryset.filter(kind__name__in=kinds_list)
        return queryset


class AttachmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer


def health_check(request, format=None):
    return HttpResponse('Everything up and running.', content_type='text/plain')
