# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import mimetypes
import os

# Django
from django.core.wsgi import get_wsgi_application
from django.urls import get_resolver

# ################################################################################################################################
# ################################################################################################################################

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

_ = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zato.common.b2b.portal.settings')

application = get_wsgi_application()

# The URL configuration is loaded in the master process, before the workers fork.
_ = get_resolver().url_patterns

# ################################################################################################################################
# ################################################################################################################################
