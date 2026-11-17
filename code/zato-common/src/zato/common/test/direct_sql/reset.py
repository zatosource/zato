# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Resetting tables between tests - the tables of a schema are emptied so that the next test starts from no rows.

# Zato
from zato.common.db_env.engine import call_database
from zato.common.db_env.write_path import Mechanism, write_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Engine

    Engine = Engine
    MetaData = MetaData

# ################################################################################################################################
# ################################################################################################################################

def _delete_all_rows(engine:'Engine', metadata:'MetaData') -> 'None':

    # The tables that others refer to are emptied after the tables that refer to them
    tables = reversed(metadata.sorted_tables)

    with engine.begin() as connection:
        for table in tables:
            _ = connection.execute(table.delete())

# ################################################################################################################################

def reset_tables(engine:'Engine', metadata:'MetaData') -> 'None':
    """ Deletes every row of every table of a schema in one transaction, in turn with the other writes to the database.
    The rows are removed as a seed removes its own, which no other mechanism may do to the tables of the audit log.
    """
    with write_path(Mechanism.Seed):
        _ = call_database(engine, _delete_all_rows, engine, metadata)

# ################################################################################################################################
# ################################################################################################################################
