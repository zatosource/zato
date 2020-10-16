# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

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
                port     = params['port'],
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
                port     = params['port'],
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

    print('SAPO-0', datetime.utcnow())

    # stdlib
    import copy

    print('SAPO-1', datetime.utcnow())

    # SQLAlchemy
    from sqlalchemy import create_engine

    print('SAPO-1b', datetime.utcnow())

    from sqlalchemy.orm import sessionmaker

    print('SAPO-2', datetime.utcnow())

    # Zato
    from zato.common.util.api import get_engine_url

    print('SAPO-3', datetime.utcnow())

    engine_params = copy.deepcopy(engine_params)
    if engine_params['engine'] != 'sqlite':
        engine_params['password'] = str(engine_params['password'])
        engine_params['extra']['pool_size'] = engine_params.pop('pool_size')

    print('SAPO-4', datetime.utcnow())

    engine = create_engine(get_engine_url(engine_params), **engine_params.get('extra', {}))

    print('SAPO-5', datetime.utcnow())

    engine.execute(ping_query)

    print('SAPO-6', datetime.utcnow())

    Session = sessionmaker()

    print('SAPO-7', datetime.utcnow())

    Session.configure(bind=engine, query_cls=query_class)

    print('SAPO-8', datetime.utcnow())

    session = Session()

    print('SAPO-9', datetime.utcnow())

    print()
    print('SAPO-10-1', engine_params)
    print('SAPO-10-2', ping_query)
    print()

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
