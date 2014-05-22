# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common import engine_def, engine_def_sqlite

logger = getLogger(__name__)

django_sa_mappings = {
    'NAME': 'sqlite_path',
    'HOST': 'host',
    'PORT': 'port',
    'USER': 'username',
    'PASSWORD': 'password',
    'odb_type': 'engine',
    'db_type': 'engine',
}

def get_engine_url(args):
    attrs = {}
    is_sqlite = getattr(args, 'odb_type', None) == 'sqlite' or args.get('engine') == 'sqlite' or args.get('db_type') == 'sqlite'
    names = ('engine', 'username', 'password', 'host', 'port', 'name', 'db_name', 'sqlite_path', 'odb_type', 'odb_user',
             'odb_password', 'odb_host', 'odb_port', 'odb_db_name', 'odb_type', 'ENGINE', 'NAME', 'HOST', 'USER', 'PASSWORD',
             'PORT')

    # Args as attributes
    if is_sqlite:
        for name in names:
            attrs[name] = getattr(args, name, '')

    # Args as keys
    else:
        if attrs.get('NAME'):
            for name in names:
                attrs[name] = getattr(args, name, '')
        else:
            for name in names:
                attrs[name] = args.get(name, '')

    # Re-map Django params into SQLAlchemy params
    if attrs.get('NAME'):
        for name in django_sa_mappings:
            attrs[django_sa_mappings[name]] = attrs[name]

    # Re-map server ODB params into SQLAlchemy params
    if attrs['engine'] == 'sqlite':
        attrs['sqlite_path'] = attrs.get('db_name')

    engine_url = (engine_def_sqlite if is_sqlite else engine_def).format(**attrs)

    logger.warn(args)
    logger.warn(attrs)
    logger.warn(is_sqlite)
    logger.warn(engine_url)

    return engine_url