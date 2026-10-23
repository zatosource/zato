# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.webapp.settings import build_settings, build_templates

# ################################################################################################################################
# ################################################################################################################################

globals().update(build_settings(
    root_urlconf='zato.common.b2b.console.urls',
    cookie_name='zato-b2b-console',
    extra_apps=['zato.common.b2b.console', 'zato.common.webapp.ui'],
    extra_middleware=[],
))

WSGI_APPLICATION = 'zato.common.b2b.console.wsgi.application'

TEMPLATES = build_templates(context_processors=[
    'django.template.context_processors.request',
    'zato.common.webapp.ui.context.theme',
])

# ################################################################################################################################
# ################################################################################################################################
