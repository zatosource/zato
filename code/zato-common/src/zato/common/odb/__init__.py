# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import copy, logging

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

AMQP_DEFAULT_PRIORITY = 5
WMQ_DEFAULT_PRIORITY = 5

# ODB version
VERSION = 1

SUPPORTED_DB_TYPES = (b'oracle', b'postgresql')

engine_def = '{engine}://{username}:{password}@{host}:{port}/{db_name}'

# Queries to use in pinging the databases.
ping_queries = {
    'access': 'SELECT 1',
    'db2': 'SELECT current_date FROM sysibm.sysdummy1',
    'firebird': 'SELECT current_timestamp FROM rdb$database',
    'informix': 'SELECT 1 FROM systables WHERE tabid=1',
    'mssql': 'SELECT 1',
    'mysql': 'SELECT 1+1',
    'oracle': 'SELECT 1 FROM dual',
    'postgresql': 'SELECT 1',
}

def create_pool(crypto_manager, engine_params):
    engine_params = copy.deepcopy(engine_params)
    engine_params['password'] = str(crypto_manager.decrypt(engine_params['password']))
    engine_url = engine_def.format(**engine_params)

    engine = create_engine(engine_url, pool_size=engine_params['pool_size'], **engine_params['extra'])
    engine.execute(ping_queries[engine_params['engine']])

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    return session

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
        except SQLError, e:
            print(e)

    for seq in [name for (name,) in engine.execute(text(sequence_sql))]:
        try:
            engine.execute(text('DROP SEQUENCE %s CASCADE' % seq))
        except SQLError, e:
            print(e)