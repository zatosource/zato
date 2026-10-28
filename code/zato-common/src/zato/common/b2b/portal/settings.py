# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.b2b.portal.config import Template_Dir
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

# No application, middleware, session or cookie is configured, so a response sets none.
SECRET_KEY = CryptoManager.generate_secret(as_str=True)

DEBUG = False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS:'list[str]' = []

MIDDLEWARE:'list[str]' = []

ROOT_URLCONF = 'zato.common.b2b.portal.urls'

WSGI_APPLICATION = 'zato.common.b2b.portal.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Template_Dir],
        'OPTIONS': {
            'loaders': ['django.template.loaders.filesystem.Loader'],
        },
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_TZ = True

# ################################################################################################################################
# ################################################################################################################################
