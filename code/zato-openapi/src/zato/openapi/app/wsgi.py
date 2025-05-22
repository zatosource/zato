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

# ################################################################################################################################
# ################################################################################################################################
