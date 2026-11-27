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
from zato.common.lets_encrypt.config import get_dashboard_host_names
from zato.common.util.open_ import open_r

# SQLAlchemy
from sqlalchemy.orm import sessionmaker, scoped_session

# YAML
import yaml

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

    # Add dummy assignments to satisfy type checkers
    any_ = any_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# These are placeholders that the 'zato start' command overwrites through the star import below.
log_config:'any_' = None
config_dir:'any_' = None
DATABASES:'any_' = {}

# Zato Django plugin configuration
ZATO_URL = os.environ.get('ZATO_URL', 'http://localhost:17010/zato/api/invoke/django/{}')
ZATO_USERNAME = 'django'
ZATO_PASSWORD = os.environ.get('Zato_Django_Password') or os.environ.get('Zato_Password', '')

# Zato
from zato.common.api import TRACE1
from zato.common.crypto.api import CryptoManager
from zato.common.db_env.database import new_odb_engine
from zato.common.util.eval_ import as_bool
from zato.common.webapp.dashboard_db import Django_Engine, get_django_database
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

            # Django creates django.request before the settings are read, and a disabled logger stays disabled
            # through Django's own configuration, which would drop the traceback of every request that fails.
            logging_config['disable_existing_loggers'] = False

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
    _session_cookie_age = int(_session_timeout)
else:
    _session_cookie_age = _session_timeout_default

SESSION_COOKIE_AGE = _session_cookie_age

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
    _is_debug = as_bool(_debug)
else:
    _is_debug = False

DEBUG = _is_debug

csrf_trusted_origins = os.environ.get(_csrf_env_key_dashboard)

if not csrf_trusted_origins:
    csrf_trusted_origins = os.environ.get(_csrf_env_key_django)

_csrf_trusted_origins:'strlist' = []

if csrf_trusted_origins:

    for origin in csrf_trusted_origins.split(','):
        origin = origin.strip()
        if origin:
            _csrf_trusted_origins.append(origin)

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

    _csrf_trusted_origins.append(f'http://{common_name}:{dashboard_port}')
    _csrf_trusted_origins.append(f'https://{common_name}:{dashboard_ssl_port}')

CSRF_TRUSTED_ORIGINS = _csrf_trusted_origins

# The host names under which the shared HTTPS port serves the Dashboard are trusted as well
for dashboard_host_name in get_dashboard_host_names(dict(os.environ)):
    CSRF_TRUSTED_ORIGINS.append(f'https://{dashboard_host_name}')

APPEND_SLASH = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Absolute path to the directory that holds media.
# Example: '/home/media/media.lawrence.com/'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')

# Where the shared UI assets from zato-common live, the rule editor component among them,
# served under /shared-ui/
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

# DATABASES is injected by the 'zato start' command, which reads the configuration from the web-admin.conf file.
# The Django tables of the Dashboard reside in its own SQLite database in its configuration directory.

if DATABASES:

    DATABASES['default'] = get_django_database(config_dir)

    # SQLAlchemy setup for the configuration database
    SASession = scoped_session(sessionmaker())

    engine = new_odb_engine()
    SASession.configure(bind=engine)

else:
    ADMIN_INVOKE_NAME     = _standalone_value
    ADMIN_INVOKE_PASSWORD = _standalone_value

    DATABASES['default'] = {}
    DATABASES['default']['ENGINE'] = Django_Engine

    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'

    SECRET_KEY = CryptoManager.generate_secret(as_str=True)

# ################################################################################################################################
# ################################################################################################################################
