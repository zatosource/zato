# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.webapp.settings import build_settings, build_templates
from zato.rule_engine_dashboard.app.database import get_django_database

# ################################################################################################################################
# ################################################################################################################################

# What the dashboard needs of Django beyond the sessions and static files every application has -
# its users live in Django's own tables and its screens speak through the messages framework.
_extra_apps = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'zato.common.webapp.ui',
    'zato.rule_engine_dashboard.app',
]

_extra_middleware = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# ################################################################################################################################
# ################################################################################################################################

globals().update(build_settings(
    root_urlconf='zato.rule_engine_dashboard.app.urls',
    cookie_name='zato-rule-engine-dashboard',
    extra_apps=_extra_apps,
    extra_middleware=_extra_middleware,
))

# ################################################################################################################################
# ################################################################################################################################

LOGIN_URL = '/login/'

TEMPLATES = build_templates(context_processors=[
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'zato.common.webapp.ui.context.theme',
])

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# The Zato database, which holds the rule engine tables and the tables of Django
DATABASES = {
    'default': get_django_database(),
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# ################################################################################################################################
# ################################################################################################################################
