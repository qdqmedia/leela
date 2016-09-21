import os
from django.shortcuts import render
from django.views.generic import View
from django.views.static import serve
from django.conf import settings


class ImageView(View):
    def get(request, *args, **kwargs):
        path = kwargs['path']
        path_parts = path.split('/')
        
        # Needed because the serve function does not check for META existence
        request.META = {}
        return serve(request, path, document_root=settings.MEDIA_ROOT, show_indexes=True)
