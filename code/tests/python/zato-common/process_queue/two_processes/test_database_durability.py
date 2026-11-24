# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Each connection to the Zato database commits durably - PostgreSQL waits for the log to reach the disk.

# Zato
from zato.common.db_env.database import dispose_database_engine, get_database_engine
from zato.common.test.pubsub_database import PubSubDBMode, pubsub_db_env, start_pubsub_database, stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection as SAConnection
    from zato.common.typing_ import anylist

    SAConnection = SAConnection
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What PostgreSQL reports for commits that wait for the log to reach the disk
    Synchronous_Commit = 'on'

    # How many connections of the pool are checked at the same time
    Connection_Count = 3

    # The label of the PostgreSQL container of this test
    Label = 'durability'

# ################################################################################################################################
# ################################################################################################################################

def _read_synchronous_commit(connection:'SAConnection') -> 'str':
    """ Returns the synchronous commit level of one PostgreSQL connection.
    """
    out = connection.exec_driver_sql('show synchronous_commit').scalar()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_postgresql_synchronous_commit() -> 'None':
    database = start_pubsub_database(ModuleCtx.Label, PubSubDBMode.PostgreSQL)

    try:
        with pubsub_db_env(database.env):
            engine = get_database_engine()

            # Each of the connections held at the same time is a separate connection of the pool ..
            connections:'anylist' = []

            for _ in range(ModuleCtx.Connection_Count):
                connection = engine.connect()
                connections.append(connection)

            # .. and each of them commits durably.
            try:
                for connection in connections:
                    synchronous_commit = _read_synchronous_commit(connection)
                    assert synchronous_commit == ModuleCtx.Synchronous_Commit, synchronous_commit
            finally:
                for connection in connections:
                    connection.close()

            dispose_database_engine()
    finally:
        stop_pubsub_database(database)

# ################################################################################################################################
# ################################################################################################################################
