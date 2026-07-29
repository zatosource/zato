# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.webapp.settings import build_settings
from zato.rule_engine_dashboard.app.database import database_from_url

# ################################################################################################################################
# ################################################################################################################################

# The database both the rule engine's SQL backend and Django share - Django keeps only its own tables there
Env_DB_URL = 'Zato_Rule_Engine_Dashboard_DB_URL'

# A local SQLite file is the default, created where the application runs
Default_DB_URL = 'sqlite:///zato-rule-engine-dashboard.db'

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

# The screens are found by the app-directories loader, both the dashboard's own and the shared UI kit's
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'zato.common.webapp.ui.context.theme',
            ],
        },
    },
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if _db_url := os.environ.get(Env_DB_URL):
    pass
else:
    _db_url = Default_DB_URL

DATABASES = {
    'default': database_from_url(_db_url),
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# ################################################################################################################################
# ################################################################################################################################
