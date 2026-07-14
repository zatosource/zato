# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import os

# Django
from django.core.wsgi import get_wsgi_application

# ################################################################################################################################
# ################################################################################################################################

# Register MIME types explicitly
import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('image/png', '.png')

_ = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zato.openapi.app.settings')

application = get_wsgi_application()

# Load the URL configuration, and with it the views and the session module, in this process
# rather than lazily on the first request - gunicorn imports this module in the master before workers fork,
# which is what makes all workers share the same credential encryption key.
from django.urls import get_resolver

_ = get_resolver().url_patterns

# ################################################################################################################################
# ################################################################################################################################
