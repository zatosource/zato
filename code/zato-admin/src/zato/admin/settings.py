# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# stdlib
import logging, logging.config, os

# SQLAlchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

# Zato
from zato.common.odb import engine_def
from zato.common.util import TRACE1
from zato_settings import *

if 'DEBUG' not in globals():
    DEBUG = os.environ.get('ZATO_ADMIN_DEBUG', False)

if DEBUG:
    try:
        from debug_settings import *
    except ImportError:
        pass

logging.addLevelName('TRACE1', TRACE1)
if 'log_config' in globals():
    logging.config.fileConfig(log_config)
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

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'zato.admin.middleware.ZatoMiddleware',
)

ROOT_URLCONF = 'zato.admin.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'debug_toolbar',
    'django_settings',
    'zato.admin.web',
)

# A list of prefixes pointing to resources (such as CSS or JS) which may be
# accessed by anonymous users
DONT_REQUIRE_LOGIN = [
    '/static/',
    '/favicon.ico',
]

# Some values below, e.g. db_type, DATABASE_USER and others are magically injected
# here by the 'zato start /path/to/zato/admin' command. The command in turn
# fetches values from the 'zato-admin.conf' file.

if 'DATABASES' in globals():
    DATABASES['default']['ENGINE'] = 'django.db.backends.' + django_sqlalchemy_engine[db_type]
    
    # SQLAlchemy setup
    SASession = scoped_session(sessionmaker())
    engine = create_engine(engine_def.format(engine=db_type, username=DATABASE_USER,
                    password=DATABASE_PASSWORD, host=DATABASE_HOST, db_name=DATABASE_NAME))
    SASession.configure(bind=engine)
    
    # Crypto
    ssl_key_file = os.path.join(config_dir, SSL_KEY_FILE)
    ssl_cert_file = os.path.join(config_dir, SSL_CERT_FILE)
    ssl_ca_certs = os.path.join(config_dir, SSL_CA_CERTS)
    
    TEMPLATE_DEBUG = True
else:
    TECH_ACCOUNT_NAME = 'dummy'
    TECH_ACCOUNT_PASSWORD = 'dummy'
    DATABASES = {}
    DATABASES['default'] = {}
    DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
    
    ssl_key_file = 'dummy'
    ssl_cert_file = 'dummy'
    ssl_ca_certs = 'dummy'
    
    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'