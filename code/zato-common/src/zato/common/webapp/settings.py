# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, stranydict, strlist

# ################################################################################################################################
# ################################################################################################################################

# What every standalone application needs of Django itself - sessions for the signed cookie
# and staticfiles for the finders that serve each application's own assets.
_base_apps = [
    'django.contrib.sessions',
    'django.contrib.staticfiles',
]

# The order is what Django requires - sessions before anything that reads them.
_base_middleware = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Every application serves its assets from under this prefix
static_url = '/static/'

# The loaders are named here rather than left to APP_DIRS, because Django then wraps them in its
# caching loader, which holds every compiled screen in memory for the life of a worker process.
_template_loaders = [
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
]

# ################################################################################################################################
# ################################################################################################################################

def build_settings(
    *,
    root_urlconf:'str',
    cookie_name:'str',
    extra_apps:'strlist',
    extra_middleware:'strlist',
    ) -> 'stranydict':
    """ The Django settings that every standalone Zato web application shares, for its own
    settings module to merge into its globals and then add whatever is genuinely its own.

    Sessions are kept in a signed cookie, whose key is generated once per process tree - the
    application is imported in the gunicorn master before workers fork, so all of them share it.
    Restarting an application invalidates all of its sessions, which is desired.
    """
    secret_key = CryptoManager.generate_secret(as_str=True)

    installed_apps = _base_apps + extra_apps
    middleware = _base_middleware + extra_middleware

    out = {
        'SECRET_KEY': secret_key,
        'DEBUG': False,
        'ALLOWED_HOSTS': ['*'],

        'INSTALLED_APPS': installed_apps,
        'MIDDLEWARE': middleware,
        'ROOT_URLCONF': root_urlconf,

        'SESSION_ENGINE': 'django.contrib.sessions.backends.signed_cookies',
        'SESSION_COOKIE_NAME': cookie_name,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',

        'STATIC_URL': static_url,

        'LANGUAGE_CODE': 'en-us',
        'TIME_ZONE': 'UTC',
        'USE_I18N': True,
        'USE_TZ': True,
    }

    return out

# ################################################################################################################################

def build_templates(*, context_processors:'strlist') -> 'anylist':
    """ The template configuration every standalone Zato web application shares - the screens are
    found by the app-directories loader, both an application's own and the shared UI kit's, and each
    one is read from disk as it is used, so editing a screen needs no restart.
    """
    out = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'OPTIONS': {
                'context_processors': context_processors,
                'loaders': _template_loaders,
            },
        },
    ]

    return out

# ################################################################################################################################
# ################################################################################################################################
