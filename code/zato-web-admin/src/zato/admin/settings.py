# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import logging.config
import os
from uuid import uuid4

# SQLAlchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

# YAML
import yaml

# Zato
from zato.common import TRACE1
from zato.common.settings_db import SettingsDB
from zato.common.util import get_engine_url
from zato_settings import * # noqa

logging.addLevelName('TRACE1', TRACE1)
if 'log_config' in globals():
    with open(log_config) as f:
        logging.config.dictConfig(yaml.load(f))
else:
    logging.basicConfig(level=logging.DEBUG)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

INTERNAL_IPS = ('127.0.0.1',)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: '/home/media/media.lawrence.com/'
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: 'http://media.lawrence.com', 'http://example.com/media/'
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: 'http://foo.com/media/', '/media/'.
ADMIN_MEDIA_PREFIX = '/media/'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'zato.admin.middleware.ZatoMiddleware',
)

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
    'django.contrib.staticfiles',
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
    if db_type.startswith('mysql'):
        db_type = 'mysql'

    db_data = DATABASES['default']
    db_data['ENGINE'] = 'django.db.backends.' + django_sqlalchemy_engine[db_type]

    for name in('ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST', 'PORT'):
        globals()['DATABASE_{}'.format(name)] = DATABASES['default'][name]

    db_data['db_type'] = db_type

    # Crypto
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
    _settings_db_path = os.path.join(config_dir, 'config', 'repo', 'settings.db')
    _settings_db_session = scoped_session(sessionmaker())
    _settings_db_engine = create_engine('sqlite:///{}'.format(_settings_db_path))
    _settings_db_session.configure(bind=_settings_db_engine)

    settings_db = SettingsDB(_settings_db_path, _settings_db_session)

else:
    ADMIN_INVOKE_NAME = 'dummy'
    ADMIN_INVOKE_PASSWORD = 'dummy'
    DATABASES = {}
    DATABASES['default'] = {}
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'

    ssl_key_file = 'dummy'
    ssl_cert_file = 'dummy'
    ssl_ca_certs = 'dummy'

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
