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

def _with_referenced_tables(tables:'tablelist') -> 'tablelist':
    """ Returns the tables together with each table that their foreign keys refer to, directly or through another table,
    because the database rejects a foreign key to a table that does not exist.
    """
    out:'tablelist' = []
    pending = list(tables)

    while pending:
        table = pending.pop()

        if table in out:
            continue

        out.append(table)

        for foreign_key in table.foreign_keys:
            pending.append(foreign_key.column.table)

    return out

# ################################################################################################################################

@contextmanager
def config_database_engine(tables:'tablelist') -> 'enginegen':
    """ Yields an engine of the configuration database in a new database of its own, built by the engine factory
    with the settings of durability of every database of Zato, and with the given tables of the configuration model
    and the tables that they refer to, then disposes of the engine and drops the database.
    """
    with isolated_database_env():
        engine = new_odb_engine()

        tables = _with_referenced_tables(tables)
        Base.metadata.create_all(engine, tables=tables)

        try:
            yield engine
        finally:
            engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
