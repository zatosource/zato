# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# Zato
from zato.common.webapp.settings import build_settings, build_templates

# ################################################################################################################################
# ################################################################################################################################

globals().update(build_settings(
    root_urlconf='zato.openapi.app.urls',
    cookie_name='zato-openapi-console',
    extra_apps=['zato.openapi.app'],
    extra_middleware=[],
))

# ################################################################################################################################
# ################################################################################################################################

WSGI_APPLICATION = 'zato.openapi.app.wsgi.application'

TEMPLATES = build_templates(context_processors=[
    'django.template.context_processors.request',
])

# ################################################################################################################################
# ################################################################################################################################
