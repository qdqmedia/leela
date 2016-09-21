"""leela URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles import views

from emails import custom_admin_urls
from emails.views import ImageView

import djwiggum.urls


urlpatterns = [
    # Admin views
    url(r'^admin/', include(admin.site.urls)),

    # Custom admin views
    url(r'^cadmin/', include(custom_admin_urls, namespace='cadmin')),

    # API
    url(r'^api/', include('api.urls')),

    # Serve medias for admin panel. Medias in emails are attached with CID.
    url(r'^media/(?P<path>.*)$'.format(mediaurl=settings.MEDIA_URL), ImageView.as_view())
]

# Serve statics from django, only used in the admin panel
urlpatterns += [url(r'^static/(?P<path>.*)$', views.serve, kwargs={"insecure": True})]
