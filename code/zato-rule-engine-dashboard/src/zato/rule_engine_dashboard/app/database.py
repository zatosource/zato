# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from urllib.parse import urlparse

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

# Maps SQLAlchemy-style URL schemes to Django database backends - the same URL configures
# both the rule engine's SQL backend and Django's own tables in one database.
_engine_by_scheme = {
    'sqlite':     'django.db.backends.sqlite3',
    'postgresql': 'django.db.backends.postgresql',
    'mysql':      'django.db.backends.mysql',
}

# ################################################################################################################################
# ################################################################################################################################

def database_from_url(url:'str') -> 'stranydict':
    """ Turns an SQLAlchemy-style database URL into a Django DATABASES entry.
    """
    parsed = urlparse(url)

    # Driver suffixes such as postgresql+psycopg2 mean nothing to Django, only the dialect does
    scheme = parsed.scheme.split('+')[0]

    # An unknown scheme cannot be mapped to any backend, which has to be loud
    if scheme not in _engine_by_scheme:
        raise Exception(f'Unsupported database URL scheme `{scheme}` in `{url}`')

    engine = _engine_by_scheme[scheme]

    # SQLAlchemy puts the database name in the URL path with a leading slash,
    # so sqlite:///name.db is a relative file and sqlite:////dir/name.db an absolute one.
    name = parsed.path[1:]

    # SQLite needs nothing beyond the file path ..
    if scheme == 'sqlite':
        out:'stranydict' = {
            'ENGINE': engine,
            'NAME': name,
        }
        return out

    # .. while server databases carry credentials and an address - each part
    # is genuinely optional in a URL, hence the explicit checks.
    user = parsed.username
    if user is None:
        user = ''

    password = parsed.password
    if password is None:
        password = ''

    host = parsed.hostname
    if host is None:
        host = ''

    port = parsed.port
    if port is None:
        port_text = ''
    else:
        port_text = str(port)

    out = {
        'ENGINE': engine,
        'NAME': name,
        'USER': user,
        'PASSWORD': password,
        'HOST': host,
        'PORT': port_text,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
