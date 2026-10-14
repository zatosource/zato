# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import logging.config
import os

# Zato
from zato.common.util.open_ import open_r

# SQLAlchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

# YAML
import yaml

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    # Add dummy assignments to satisfy type checkers
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# These are placeholders that the 'zato start' command overwrites through the star import below.
log_config:'any_' = None
config_dir:'any_' = None
DATABASES:'any_' = None
db_type:'any_' = None

# Zato Django plugin configuration
ZATO_URL = os.environ.get('ZATO_URL', 'http://localhost:17010/zato/api/invoke/django/{}')
ZATO_USERNAME = 'django'
ZATO_PASSWORD = os.environ.get('Zato_Django_Password') or os.environ.get('Zato_Password', '')

# Zato
from zato.common.api import TRACE1
from zato.common.crypto.api import CryptoManager
from zato.common.settings_db import SettingsDB
from zato.common.util.eval_ import as_bool
# Star import is how these settings are pulled into Django's settings module.
from zato.admin.zato_settings import * # noqa: F403

# ################################################################################################################################
# ################################################################################################################################

# The environment variables the Dashboard reads its own configuration from.
_debug_env_key = 'Zato_Dashboard_Debug'
_session_timeout_env_key = 'Zato_Dashboard_Session_Timeout'
_csrf_env_key_dashboard = 'Zato_Dashboard_CSRF_Trusted_Origins'
_csrf_env_key_django = 'Zato_Django_CSRF_TRUSTED_ORIGINS'

# In seconds.
_session_timeout_default = 60 * 60 * 2

# What the CSRF trusted origins are derived from when no environment variable names them.
_default_ssl_subject = '/C=US/ST=State/L=City/O=Organization/CN=localhost'
_common_name_prefix = 'CN='
_default_common_name = 'localhost'
_default_dashboard_port = '8183'
_default_dashboard_ssl_port = '8184'

# The values the module runs with when it is imported without an injected database configuration.
_standalone_value = 'standalone'

# ################################################################################################################################
# ################################################################################################################################

logging.addLevelName(TRACE1, 'TRACE1')

from zato.common.util.logging_ import apply_logging_env_overrides, attach_service_context_filter

if log_config:
    with open_r(log_config) as f:
        try:
            logging_config = yaml.load(f, yaml.FullLoader)
            logging_config = apply_logging_env_overrides(logging_config)
            logging.config.dictConfig(logging_config)
        except ValueError:
            # This will be raised by 'zato quickstart' but we can ignore it
            pass
else:
    logging.basicConfig(level=logging.DEBUG)

attach_service_context_filter()

# ################################################################################################################################
# ################################################################################################################################

# Session timeout
if _session_timeout := os.environ.get(_session_timeout_env_key):
    SESSION_COOKIE_AGE = int(_session_timeout)
else:
    SESSION_COOKIE_AGE = _session_timeout_default

SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

INTERNAL_IPS = ('127.0.0.1',)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Debug mode is off unless explicitly requested.
if _debug := os.environ.get(_debug_env_key):
    DEBUG = as_bool(_debug)
else:
    DEBUG = False

csrf_trusted_origins = os.environ.get(_csrf_env_key_dashboard)

if not csrf_trusted_origins:
    csrf_trusted_origins = os.environ.get(_csrf_env_key_django)

if csrf_trusted_origins:

    CSRF_TRUSTED_ORIGINS = []

    for origin in csrf_trusted_origins.split(','):
        origin = origin.strip()
        if origin:
            CSRF_TRUSTED_ORIGINS.append(origin)

else:
    ssl_subject = os.environ.get('Zato_SSL_Subject', _default_ssl_subject)

    for part in ssl_subject.split('/'):
        if part.startswith(_common_name_prefix):
            common_name = part[len(_common_name_prefix):]
            break
    else:
        common_name = _default_common_name

    if not common_name:
        common_name = _default_common_name

    dashboard_port = os.environ.get('Zato_Port_Dashboard', _default_dashboard_port)
    dashboard_ssl_port = os.environ.get('Zato_Port_Dashboard_SSL', _default_dashboard_ssl_port)

    CSRF_TRUSTED_ORIGINS = [
        f'http://{common_name}:{dashboard_port}',
        f'https://{common_name}:{dashboard_ssl_port}'
    ]

APPEND_SLASH = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Absolute path to the directory that holds media.
# Example: '/home/media/media.lawrence.com/'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')

# Where the shared UI assets from zato-common live - the rule editor component among them -
# served under /shared-ui/ so web-admin and the rule engine dashboard load one codebase
import zato.common.webapp.ui as _webapp_ui
SHARED_UI_ROOT = os.path.join(os.path.dirname(_webapp_ui.__file__), 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: 'https://media.lawrence.com', 'https://example.com/media/'
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: 'https://foo.com/media/', '/media/'.
ADMIN_MEDIA_PREFIX = '/media/'

# Same origin rather than nothing at all, because every fetch kind that has no
# directive of its own falls back to this one - the web manifest, the media and
# what the browser itself reads back, e.g. a devtools fetch of a page or of a
# script it already loaded, each of which was logged as a violation under
# 'none' even though the page's own loads went through. Plugins stay banned
# outright below and everything that matters keeps its own directive.
CSP_DEFAULT_SRC = ["'self'"]
CSP_OBJECT_SRC  = ["'none'"]
CSP_IMG_SRC     = ["'self'", "data:", "https://upcdn.io"]
CSP_STYLE_SRC   = ["'self'"]
CSP_FONT_SRC   = ["'self'", "data:"]
CSP_SCRIPT_SRC  = ["'self'", "'unsafe-inline'", "'unsafe-eval'"]
CSP_CONNECT_SRC = ["'self'"]
# GitHub is where the form that creates the dashboard's GitHub App is posted to.
CSP_FORM_ACTION = ["'self'", "https://github.com"]
CSP_STYLE_SRC_ATTR = ["'self'", "'unsafe-inline'"]
CSP_STYLE_SRC_ELEM = ["'self'", "'unsafe-inline'"]
# Empty on purpose - templates still render nonce attributes but the nonce is not added to any directive yet.
# It can only go into script-src once the inline onclick= handlers and javascript: links are migrated,
# because a nonce in script-src makes browsers ignore 'unsafe-inline' which those still require.
CSP_INCLUDE_NONCE_IN = []

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
    'zato.admin.web',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

# The values below, e.g. db_type and DATABASES, are injected by the 'zato start' command,
# which reads them from the web-admin.conf file.

if DATABASES:

    db_data = DATABASES['default']
    db_data['ENGINE'] = 'django.db.backends.sqlite3'
    db_data['db_type'] = db_type

    DATABASE_ENGINE  = db_data['ENGINE']
    DATABASE_NAME    = db_data['NAME']
    DATABASE_OPTIONS = db_data.get('OPTIONS')

    # SQLAlchemy setup for web admin's database.
    SASession = scoped_session(sessionmaker())

    engine = create_engine(f'sqlite:///{DATABASE_NAME}')
    SASession.configure(bind=engine)

    # Settings DB
    _settings_db_path = os.path.join(config_dir, 'config', 'repo', 'settings.db')
    _settings_db_session = scoped_session(sessionmaker())
    _settings_db_engine = create_engine(f'sqlite:///{_settings_db_path}')
    _settings_db_session.configure(bind=_settings_db_engine)

    settings_db = SettingsDB(_settings_db_path, _settings_db_session)

else:
    ADMIN_INVOKE_NAME     = _standalone_value
    ADMIN_INVOKE_PASSWORD = _standalone_value
    DATABASES             = {}

    DATABASES['default'] = {}
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'

    DATABASE_ENGINE = DATABASES['default']['ENGINE']
    DATABASE_NAME   = _standalone_value
    SECRET_KEY      = CryptoManager.generate_secret(as_str=True)

    settings_db = None

# ################################################################################################################################
# ################################################################################################################################
