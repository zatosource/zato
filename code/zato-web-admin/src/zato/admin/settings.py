# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import logging.config
import os
from uuid import uuid4

# Zato
from zato.common.util.open_ import open_r

# SQLAlchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

# YAML
import yaml

# These are needed for pyflakes
log_config = None
config_dir = None
DATABASES = None
db_type = None
django_sqlalchemy_engine = None
SSL_CA_CERTS = None  # type: ignore
SSL_CERT_FILE = None # type: ignore
SSL_KEY_FILE = None  # type: ignore

# Zato
from zato.common.api import TRACE1
from zato.common.settings_db import SettingsDB
from zato.common.util.api import get_engine_url
from zato.admin.zato_settings import *  # type: ignore

# ################################################################################################################################
# ################################################################################################################################

logging.addLevelName('TRACE1', TRACE1) # type: ignore

if log_config:
    with open_r(log_config) as f:
        try:
            logging.config.dictConfig(yaml.load(f, yaml.FullLoader))
        except ValueError:
            # This will be raised by 'zato quickstart' but we can ignore it
            pass
else:
    logging.basicConfig(level=logging.DEBUG)

# ################################################################################################################################
# ################################################################################################################################

# Session timeout
_session_timeout_env_key = 'Zato_Dashboard_Session_Timeout'
_session_timeout_default = 60 * 60 * 24 * 1 # In seconds, default = one day
SESSION_COOKIE_AGE = os.environ.get(_session_timeout_env_key) or _session_timeout_default

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

INTERNAL_IPS = ('127.0.0.1',)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

DEBUG = os.environ.get('Zato_Dashboard_Debug_Enabled') or False

_crsf_env1 = 'Zato_Dashboard_CSRF_Trusted_Origins'
_crsf_env2 = 'Zato_Django_CSRF_TRUSTED_ORIGINS'

if csrf_trusted_origins := (os.environ.get(_crsf_env1) or os.environ.get(_crsf_env2)):
    CSRF_TRUSTED_ORIGINS = [f'{csrf_trusted_origins}']

APPEND_SLASH = True
SECURE_CONTENT_TYPE_NOSNIFF = False

# Absolute path to the directory that holds media.
# Example: '/home/media/media.lawrence.com/'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: 'https://media.lawrence.com', 'https://example.com/media/'
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: 'https://foo.com/media/', '/media/'.
ADMIN_MEDIA_PREFIX = '/media/'

CSP_DEFAULT_SRC = ["'none'"]
CSP_IMG_SRC     = ["'self'", "data:"]
CSP_STYLE_SRC   = ["'self'"]
CSP_FONT_SRC   = ["'self'"]
CSP_SCRIPT_SRC  = ["'self'", "'unsafe-inline'", "'unsafe-eval'"]
CSP_CONNECT_SRC = ["'self'"]
CSP_FORM_ACTION = ["'self'"]
CSP_STYLE_SRC_ATTR = ["'self'", "'unsafe-inline'"]
CSP_STYLE_SRC_ELEM = ["'self'", "'unsafe-inline'"]
CSP_INCLUDE_NONCE_IN = ["'script-src'"]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'csp.middleware.CSPMiddleware',
    'zato.admin.middleware.ZatoMiddleware',
]

ROOT_URLCONF = 'zato.admin.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(os.path.dirname(__file__), 'templates')],
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
            'csp.context_processors.nonce',
        ],
        'loaders': ['django.template.loaders.filesystem.Loader']
    },
}]

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.humanize',
    # 'django.contrib.staticfiles',
    'zato.admin.web',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

# Some values below, e.g. db_type, DATABASE_USER and others are magically injected
# here by the 'zato start /path/to/zato/admin' command. The command in turn
# fetches values from the 'web-admin.conf' file.

if 'DATABASES' in globals():

    # So that Django doesn't complain about an unknown engine type
    if db_type.startswith('mysql'): # type: ignore
        db_type = 'mysql'

    db_data = DATABASES['default'] # type: ignore
    db_data['ENGINE'] = 'django.db.backends.' + django_sqlalchemy_engine[db_type] # type: ignore

    for name in('ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST', 'PORT', 'OPTIONS'):
        globals()['DATABASE_{}'.format(name)] = DATABASES['default'].get(name) # type: ignore

    db_data['db_type'] = db_type

    # Crypto
    if config_dir:
        ssl_key_file = os.path.abspath(os.path.join(config_dir, SSL_KEY_FILE))
        ssl_cert_file = os.path.abspath(os.path.join(config_dir, SSL_CERT_FILE))
        ssl_ca_certs = os.path.abspath(os.path.join(config_dir, SSL_CA_CERTS))

    # ODB SQLAlchemy setup
    SASession = scoped_session(sessionmaker())

    kwargs = {}

    if db_data['db_type'] == 'mysql':
        kwargs['pool_recycle'] = 600

    engine = create_engine(get_engine_url(db_data), **kwargs)
    SASession.configure(bind=engine)

    # Settings DB
    _settings_db_path = os.path.join(config_dir, 'config', 'repo', 'settings.db') # type: ignore
    _settings_db_session = scoped_session(sessionmaker())
    _settings_db_engine = create_engine('sqlite:///{}'.format(_settings_db_path))
    _settings_db_session.configure(bind=_settings_db_engine)

    settings_db = SettingsDB(_settings_db_path, _settings_db_session)

else:
    ADMIN_INVOKE_NAME = 'dummy'
    ADMIN_INVOKE_PASSWORD = 'dummy'
    DATABASES = {} # type: ignore
    DATABASES['default'] = {}
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

    ssl_key_file = 'dummy'
    ssl_cert_file = 'dummy'
    ssl_ca_certs = 'dummy'

    lb_agent_use_tls = False
    lb_use_tls = False
    lb_tls_verify = True

    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'

    DATABASE_ENGINE = DATABASES['default']['ENGINE']
    DATABASE_NAME = 'dummy'
    DATABASE_USER = 'dummy'
    DATABASE_PASSWORD = 'dummy'
    DATABASE_HOST = 'dummy'
    DATABASE_PORT = 123456
    SECRET_KEY = uuid4().hex

    settings_db = None
    is_totp_enabled = False
