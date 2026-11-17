# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.db_env.common import Type_SQLite
from zato.common.db_env.database import get_database_values

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# The Django backend of each type of the Zato database
_engine_by_type = {
    'sqlite':     'django.db.backends.sqlite3',
    'postgresql': 'django.db.backends.postgresql',
}

# The libpq SSL modes, by whether the certificate of the server is verified
_ssl_mode_verify    = 'verify-full'
_ssl_mode_no_verify = 'require'

# ################################################################################################################################
# ################################################################################################################################

def _get_password(values:'stranydict') -> 'str':
    """ Returns the password of the database, read out of its file if the Password_File variable names one.
    """
    if password_file := values['password_file']:
        with open(password_file) as password_file_object:
            out = password_file_object.read()
        out = out.strip()
    else:
        out = values['password']

    return out

# ################################################################################################################################

def _get_ssl_options(values:'stranydict') -> 'stranydict':
    """ Returns the libpq SSL options of the database, empty when SSL is off.
    """
    out:'stranydict' = {}

    if not values['ssl']:
        return out

    if values['ssl_verify']:
        out['sslmode'] = _ssl_mode_verify
    else:
        out['sslmode'] = _ssl_mode_no_verify

    if ssl_ca_file := values['ssl_ca_file']:
        out['sslrootcert'] = ssl_ca_file

    if ssl_cert_file := values['ssl_cert_file']:
        out['sslcert'] = ssl_cert_file

    if ssl_key_file := values['ssl_key_file']:
        out['sslkey'] = ssl_key_file

    return out

# ################################################################################################################################

def get_django_database() -> 'stranydict':
    """ Returns the Django DATABASES entry of the Zato database, as the Zato_Database_* variables select it.
    """
    values = get_database_values()
    db_type = values['type']
    engine = _engine_by_type[db_type]

    # SQLite needs nothing beyond the file path ..
    if db_type == Type_SQLite:
        out:'stranydict' = {
            'ENGINE': engine,
            'NAME': values['name'],
        }
        return out

    # .. while PostgreSQL has an address, credentials and SSL options.
    password = _get_password(values)
    ssl_options = _get_ssl_options(values)

    out = {
        'ENGINE': engine,
        'NAME': values['name'],
        'USER': values['username'],
        'PASSWORD': password,
        'HOST': values['host'],
        'PORT': values['port'],
        'OPTIONS': ssl_options,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
