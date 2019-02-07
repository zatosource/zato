# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import copy
import logging
from traceback import format_exc

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

WMQ_DEFAULT_PRIORITY = 5

# ODB version
VERSION = 1

# These databases may be used for ODB but individual SQL outconns can connect to, say, MS SQL
SUPPORTED_DB_TYPES = ('mysql', 'postgresql', 'sqlite')

# ################################################################################################################################

def get_ping_query(fs_sql_config, engine_params):
    """ Returns a ping query for input engine and component-wide SQL configuration.
    """
    ping_query = None
    for key, value in fs_sql_config.items():
        if key == engine_params['engine']:
            ping_query = value.get('ping_query')
            break

    if not ping_query:

        # We special case SQLite because it is never server from sql.ini
        if engine_params['engine'] == 'sqlite':
            ping_query = 'SELECT 1'

        if not ping_query:
            raise ValueError('Could not find ping_query for {}'.format(engine_params))

    # If we are here it means that a query was found
    return ping_query

# ################################################################################################################################

def create_pool(crypto_manager, engine_params, ping_query):
    from zato.common.util import get_engine_url

    engine_params = copy.deepcopy(engine_params)
    if engine_params['engine'] != 'sqlite':
        engine_params['password'] = str(engine_params['password'])
        engine_params['extra']['pool_size'] = engine_params.pop('pool_size')

    engine = create_engine(get_engine_url(engine_params), **engine_params['extra'])
    engine.execute(ping_query)

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    return session

# ################################################################################################################################

# Taken from http://www.siafoo.net/snippet/85
# Licensed under BSD2 - http://opensource.org/licenses/bsd-license.php
def drop_all(engine):
    """ Drops all tables and sequences (but not VIEWS) from a Postgres database
    """

    sequence_sql="""SELECT sequence_name FROM information_schema.sequences
                    WHERE sequence_schema='public'
                 """

    table_sql="""SELECT table_name FROM information_schema.tables
                 WHERE table_schema='public' AND table_type != 'VIEW' AND table_name NOT LIKE 'pg_ts_%%'
              """

    for table in [name for (name,) in engine.execute(text(table_sql))]:
        try:
            engine.execute(text('DROP TABLE %s CASCADE' % table))
        except Exception:
            logger.warn(format_exc())

    for seq in [name for (name,) in engine.execute(text(sequence_sql))]:
        try:
            engine.execute(text('DROP SEQUENCE %s CASCADE' % seq))
        except Exception:
            logger.warn(format_exc())

# ################################################################################################################################
