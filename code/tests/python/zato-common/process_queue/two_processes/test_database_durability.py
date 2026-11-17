# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Each connection to the Zato database commits durably - SQLite writes its log ahead of the file and syncs it
# fully in the worker and in the config process alike, and PostgreSQL waits for the log to reach the disk.

# Zato
from server_processes import ModuleCtx as ProcessesCtx, receive, ServerProcesses
from zato.common.db_env.database import dispose_database_engine, get_database_engine
from zato.common.test.pubsub_database import PubSubDBMode, pubsub_db_env, start_pubsub_database, stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from sqlalchemy.engine import Connection as SAConnection
    from zato.common.typing_ import anylist

    Connection = Connection
    SAConnection = SAConnection
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # What SQLite reports for a write-ahead log synced fully
    Journal_Mode = 'wal'
    Synchronous_Full = 2

    # What PostgreSQL reports for commits that wait for the log to reach the disk
    Synchronous_Commit = 'on'

    # How many connections of the pool are checked at the same time
    Connection_Count = 3

    # The label of the PostgreSQL container of this test
    Label = 'durability'

    # How long the test waits for the report of a process, in seconds
    Report_Timeout = 60.0

# ################################################################################################################################
# ################################################################################################################################

def _read_pragmas(conn:'Connection') -> 'None':
    """ Reports the journal mode and the synchronous level of a connection of this process.
    """
    engine = get_database_engine()

    with engine.connect() as connection:
        journal_mode = connection.exec_driver_sql('pragma journal_mode').scalar()
        synchronous = connection.exec_driver_sql('pragma synchronous').scalar()

    report = {
        'journal_mode': journal_mode,
        'synchronous': synchronous,
    }

    conn.send(report)

# ################################################################################################################################

def _read_synchronous_commit(connection:'SAConnection') -> 'str':
    """ Returns the synchronous commit level of one PostgreSQL connection.
    """
    out = connection.exec_driver_sql('show synchronous_commit').scalar()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_sqlite_durability_in_both_processes(database_path:'str') -> 'None':
    processes = ServerProcesses()

    config_conn = processes.start(ProcessesCtx.Role_Config, _read_pragmas)
    config_report = receive(config_conn, ModuleCtx.Report_Timeout)

    worker_conn = processes.start(ProcessesCtx.Role_Worker, _read_pragmas)
    worker_report = receive(worker_conn, ModuleCtx.Report_Timeout)

    processes.join()

    expected = {
        'journal_mode': ModuleCtx.Journal_Mode,
        'synchronous': ModuleCtx.Synchronous_Full,
    }

    assert config_report == expected, config_report
    assert worker_report == expected, worker_report

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
