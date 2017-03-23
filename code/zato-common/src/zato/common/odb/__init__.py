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

# Zato
from zato.common import ping_queries

logger = logging.getLogger(__name__)

WMQ_DEFAULT_PRIORITY = 5

# ODB version
VERSION = 1

SUPPORTED_DB_TYPES = (b'oracle', b'postgresql', b'mysql', b'sqlite')

def create_pool(crypto_manager, engine_params):
    from zato.common.util import get_engine_url

    engine_params = copy.deepcopy(engine_params)
    if engine_params['engine'] != 'sqlite':
        engine_params['password'] = str(crypto_manager.decrypt(engine_params['password']))
        engine_params['extra']['pool_size'] = engine_params.pop('pool_size')

    engine = create_engine(get_engine_url(engine_params), **engine_params['extra'])
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
        except Exception, e:
            print(e)

    for seq in [name for (name,) in engine.execute(text(sequence_sql))]:
        try:
            engine.execute(text('DROP SEQUENCE %s CASCADE' % seq))
        except Exception, e:
            print(e)
