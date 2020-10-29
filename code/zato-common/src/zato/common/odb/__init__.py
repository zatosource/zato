# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# ################################################################################################################################

def ping_database(params, ping_query):

    connection = None

    try:
        #
        # MySQL
        #
        if params['engine'].startswith('mysql'):
            import pymysql

            connection = pymysql.connect(
                host     = params['host'],
                port     = int(params['port']),
                user     = params['username'],
                password = params['password'],
                db       = params['db_name'],
            )

        #
        # PostgreSQL
        #
        elif params['engine'].startswith('postgres'):
            import pg8000

            connection = pg8000.connect(
                host     = params['host'],
                port     = int(params['port']),
                user     = params['username'],
                password = params['password'],
                database = params['db_name'],
            )

        #
        # SQLite
        #
        elif params['engine'].startswith('sqlite'):
            pass

        #
        # Unrecognised
        #
        else:
            raise ValueError('Unrecognised database `{}`'.format(params['engine']))

    finally:
        if connection:
            connection.close()

# ################################################################################################################################

def create_pool(engine_params, ping_query, query_class=None):

    # stdlib
    import copy

    # SQLAlchemy
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Zato
    from zato.common.util.api import get_engine_url

    engine_params = copy.deepcopy(engine_params)
    if engine_params['engine'] != 'sqlite':
        engine_params['password'] = str(engine_params['password'])
        engine_params['extra']['pool_size'] = engine_params.pop('pool_size')

    engine = create_engine(get_engine_url(engine_params), **engine_params.get('extra', {}))
    engine.execute(ping_query)
    Session = sessionmaker()
    Session.configure(bind=engine, query_cls=query_class)
    session = Session()
    return session

# ################################################################################################################################

# Taken from http://www.siafoo.net/snippet/85
# Licensed under BSD2 - http://opensource.org/licenses/bsd-license.php
def drop_all(engine):
    """ Drops all tables and sequences (but not VIEWS) from a Postgres database
    """

    # stdlib
    import logging
    from traceback import format_exc

    # SQLAlchemy
    from sqlalchemy.sql import text

    logger = logging.getLogger('zato')

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
