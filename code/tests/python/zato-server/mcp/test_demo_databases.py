# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The reporting databases of the MCP healthcare demo, built through the pools of the SQL connections of the demo.

# stdlib
import os

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.odb.api import SQLConnectionPool
from zato.common.typing_ import cast_
from zato.server.demo_mcp.common import SQL_Finance, SQL_Warehouse, SQL_Workforce
from zato.server.demo_mcp.warehouse import build_databases, get_database_paths

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, strdict, strintdict
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# The tables of each database, by the name of the SQL connection it is for
_tables = {
    SQL_Warehouse: ('facility', 'care_flow', 'quality'),
    SQL_Finance:   ('financial_performance',),
    SQL_Workforce: ('workforce',),
}

# How many facilities the demo has
_facility_count = 8

# ################################################################################################################################
# ################################################################################################################################

def _new_pool(name:'str', db_path:'str') -> 'SQLConnectionPool':
    """ A pool of an SQL connection of the demo, configured the way the import of the demo creates it.
    """
    config:'strdict' = {
        'engine': 'sqlite',
        'host': 'localhost',
        'port': 0,
        'db_name': db_path,
        'username': 'demo',
        'password': '',
        'pool_size': 1,
    }

    out = SQLConnectionPool(name, config, config)
    return out

# ################################################################################################################################

def _count_rows(engines:'dict[str, Engine]') -> 'strintdict':
    """ The row count of each table of each database, by the name of the table.
    """
    out:'strintdict' = {}

    for name, table_names in _tables.items():
        with engines[name].connect() as connection:
            for table_name in table_names:
                out[table_name] = connection.execute(text(f'select count(*) from {table_name}')).scalar_one()

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_databases_are_built_through_the_pools_of_their_connections(tmp_path:'any_') -> 'None':
    """ Each database is built through the pool of its SQL connection, in a file of its own,
    and a second import replaces the rows of the first one instead of adding to them.
    """
    database_paths = get_database_paths(os.path.join(str(tmp_path), 'databases'))

    engines:'dict[str, Engine]' = {}

    for name, path in database_paths.items():
        pool = _new_pool(name, path)
        engines[name] = cast_('Engine', pool.engine)

    try:

        # The first import fills in every table ..
        build_databases(engines)
        first_counts = _count_rows(engines)

        assert first_counts['facility'] == _facility_count

        for table_name, count in first_counts.items():
            assert count > 0, table_name

        # .. each database is a file of its own ..
        for path in database_paths.values():
            assert os.path.isfile(path)

        # .. and the next import replaces the rows.
        build_databases(engines)
        second_counts = _count_rows(engines)

        assert second_counts == first_counts

    finally:
        for engine in engines.values():
            engine.dispose()

# ################################################################################################################################
# ################################################################################################################################
