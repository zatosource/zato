# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# Zato
from zato.common.webapp.settings import build_settings, build_templates, get_csrf_trusted_origins

# ################################################################################################################################
# ################################################################################################################################

# The origins of reverse proxies that serve the portal under names and ports of their own
_csrf_trusted_origins_env_key = 'Zato_API_Portal_CSRF_Trusted_Origins'

# ################################################################################################################################
# ################################################################################################################################

globals().update(build_settings(
    root_urlconf='zato.openapi.app.urls',
    cookie_name='zato-api-portal',
    extra_apps=['zato.openapi.app', 'zato.common.webapp.ui'],
    extra_middleware=[],
))

# ################################################################################################################################
# ################################################################################################################################

WSGI_APPLICATION = 'zato.openapi.app.wsgi.application'

# HAProxy terminates TLS and reports the scheme of the browser's connection in this header,
# which it sets on every request, so a value sent by the browser itself never reaches the portal.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = get_csrf_trusted_origins(_csrf_trusted_origins_env_key)

TEMPLATES = build_templates(context_processors=[
    'django.template.context_processors.request',
])

# ################################################################################################################################
# ################################################################################################################################
