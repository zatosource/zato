# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import contextmanager

# Zato
from zato.common.db_env.database import new_odb_engine
from zato.common.odb.model import Base
from zato.common.test.zato_database import isolated_database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Iterator
    from sqlalchemy import Table
    from sqlalchemy.engine import Engine

    Engine = Engine
    Iterator = Iterator
    Table = Table

    enginegen = Iterator[Engine]
    tablelist = list[Table]

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def config_database_engine(tables:'tablelist') -> 'enginegen':
    """ Yields an engine of the configuration database in a new database of its own, built by the engine factory
    with the settings of durability of every database of Zato, and with the given tables of the configuration model,
    then disposes of the engine and drops the database.
    """
    with isolated_database_env():
        engine = new_odb_engine()

        Base.metadata.create_all(engine, tables=tables)

        try:
            yield engine
        finally:
            engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
