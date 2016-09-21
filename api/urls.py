from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from api import views
from custom.urls import api_urlpatterns as custom_urls


router = DefaultRouter()
router.register(r'entries', views.EmailEntryViewSet)
router.register(r'attachs', views.AttachmentViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),

    url(r'^healthcheck/$', views.health_check),
]

urlpatterns += custom_urls
