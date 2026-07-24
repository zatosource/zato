# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.crypto.api import CryptoManager
from zato.rule_engine_dashboard.app.database import database_from_url

# ################################################################################################################################
# ################################################################################################################################

# The database both the rule engine's SQL backend and Django share - Django keeps only its own tables there
Env_DB_URL = 'Zato_Rule_Engine_Dashboard_DB_URL'

# A local SQLite file is the default, created where the application runs
Default_DB_URL = 'sqlite:///zato-rule-engine-dashboard.db'

# ################################################################################################################################
# ################################################################################################################################

SECRET_KEY = CryptoManager.generate_secret(as_str=True)

DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'zato.rule_engine_dashboard.app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zato.rule_engine_dashboard.app.urls'

LOGIN_URL = '/login/'

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
            ],
        },
    },
]

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_NAME = 'zato-rule-engine-dashboard'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if _db_url := os.environ.get(Env_DB_URL):
    pass
else:
    _db_url = Default_DB_URL

DATABASES = {
    'default': database_from_url(_db_url),
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ################################################################################################################################
# ################################################################################################################################
