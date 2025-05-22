# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# Django
from django.conf import settings
from django.urls import path

# Zato
from zato.openapi.app.views import swagger_view, serve_openapi

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [
    path('', swagger_view, name='swagger'),
    path('openapi.yaml', serve_openapi, name='openapi'),
]

# Explicit routes for Swagger UI static assets
from django.http import FileResponse
import os

# Function to serve static files with explicit MIME types
def serve_static_with_mime(request, file_path, mime_type):
    full_path = os.path.join(settings.STATICFILES_DIRS[0], file_path)
    return FileResponse(open(full_path, 'rb'), content_type=mime_type)

# Add routes for each Swagger UI file
urlpatterns += [
    # CSS file
    path('static/swagger-ui/swagger-ui.css',
         lambda request: serve_static_with_mime(request, 'swagger-ui/swagger-ui.css', 'text/css')),

    # JavaScript files
    path('static/swagger-ui/swagger-ui-bundle.js',
         lambda request: serve_static_with_mime(request, 'swagger-ui/swagger-ui-bundle.js', 'application/javascript')),
    path('static/swagger-ui/swagger-ui-standalone-preset.js',
         lambda request: serve_static_with_mime(request, 'swagger-ui/swagger-ui-standalone-preset.js', 'application/javascript')),

    # Favicon files
    path('static/swagger-ui/favicon-32x32.png',
         lambda request: serve_static_with_mime(request, 'swagger-ui/favicon-32x32.png', 'image/png')),
    path('static/swagger-ui/favicon-16x16.png',
         lambda request: serve_static_with_mime(request, 'swagger-ui/favicon-16x16.png', 'image/png')),
    path('static/swagger-ui/favicon.ico',
         lambda request: serve_static_with_mime(request, 'swagger-ui/favicon.ico', 'image/x-icon')),
    path('static/swagger-ui/android-chrome-192x192.png',
         lambda request: serve_static_with_mime(request, 'swagger-ui/android-chrome-192x192.png', 'image/png')),
    path('static/swagger-ui/android-chrome-512x512.png',
         lambda request: serve_static_with_mime(request, 'swagger-ui/android-chrome-512x512.png', 'image/png')),
    path('static/swagger-ui/apple-touch-icon.png',
         lambda request: serve_static_with_mime(request, 'swagger-ui/apple-touch-icon.png', 'image/png')),
    path('static/swagger-ui/site.webmanifest',
         lambda request: serve_static_with_mime(request, 'swagger-ui/site.webmanifest', 'application/manifest+json')),
]

# ################################################################################################################################
# ################################################################################################################################
