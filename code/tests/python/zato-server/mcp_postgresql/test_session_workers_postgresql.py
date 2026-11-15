# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import traceback
from multiprocessing import get_context

# Zato
from zato.common.db_env.engine import dispose_env_engine
from zato.common.pubsub.sql.config import get_pubsub_engine, pubsub_db_config
from zato.server.connection.mcp.session import remove_all_sessions

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from multiprocessing.process import BaseProcess
    from multiprocessing.synchronize import Event
    from live_sql.containers import DatabaseServer
    from pytest import MonkeyPatch
    from zato.common.typing_ import list_

    BaseProcess = BaseProcess
    Connection = Connection
    DatabaseServer = DatabaseServer
    Event = Event
    MonkeyPatch = MonkeyPatch

    connectionlist = list_[Connection]
    processlist    = list_[BaseProcess]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Gateway_Name = 'test.mcp.gateway'
    Identity = 'test.identity'
    Protocol_Version = '2025-06-18'

    Worker_Count = 4

    # How many greenlets of each worker create sessions at once, how many each of them creates, and the cap of the identity
    Greenlets_Per_Worker = 8
    Creates_Per_Greenlet = 4
    Max_Sessions = 5

    # How long the test waits for a worker, in seconds
    Report_Timeout = 60.0

# ################################################################################################################################
# ################################################################################################################################

# Workers are forked, as the arbiter forks them
_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

def _create_many(start:'Event', conn:'Connection') -> 'None':
    """ Creates sessions of one identity from several greenlets of one worker and reports how many were created
    and how many were refused.
    """
    exit_code = 1

    try:

        # The worker runs under gevent, as a server does, so its greenlets wait for PostgreSQL concurrently ..
        from gevent import joinall, monkey, reinit, spawn
        reinit()
        _ = monkey.patch_all()

        from zato.server.connection.mcp.session import MCPSessionManager

        manager = MCPSessionManager(ModuleCtx.Gateway_Name, max_sessions=ModuleCtx.Max_Sessions)
        outcomes = {'created': 0, 'refused': 0}

        def create_some() -> 'None':
            for _ in range(ModuleCtx.Creates_Per_Greenlet):
                try:
                    _ = manager.create(ModuleCtx.Protocol_Version, ModuleCtx.Identity)
                except ValueError:
                    outcomes['refused'] += 1
                else:
                    outcomes['created'] += 1

        # .. every worker connects to the database first and then starts at once ..
        _ = manager.session_count
        _ = start.wait(ModuleCtx.Report_Timeout)

        greenlets = []

        for _ in range(ModuleCtx.Greenlets_Per_Worker):
            greenlet = spawn(create_some)
            greenlets.append(greenlet)

        _ = joinall(greenlets, raise_error=True)

        # .. and reports what it achieved.
        conn.send(outcomes)
        exit_code = 0

    # The exception reaches the output of the test, since the worker exits without unwinding
    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

def test_the_workers_together_create_no_more_sessions_than_the_cap(
    postgresql_server:'DatabaseServer',
    monkeypatch:'MonkeyPatch',
    ) -> 'None':

    details = postgresql_server.details

    monkeypatch.setenv(pubsub_db_config.env_type, details['type'])
    monkeypatch.setenv(pubsub_db_config.env_host, details['host'])
    monkeypatch.setenv(pubsub_db_config.env_port, details['port'])
    monkeypatch.setenv(pubsub_db_config.env_username, details['username'])
    monkeypatch.setenv(pubsub_db_config.env_password, details['password'])
    monkeypatch.setenv(pubsub_db_config.env_name, details['name'])

    # The schema exists and holds no sessions before the workers are forked, and no worker inherits a connection ..
    engine = get_pubsub_engine()
    remove_all_sessions(engine)
    dispose_env_engine(pubsub_db_config)

    # .. after which every worker creates sessions at once ..
    start = _context.Event()

    connections:'connectionlist' = []
    processes:'processlist' = []

    for _ in range(ModuleCtx.Worker_Count):
        parent_conn, child_conn = _context.Pipe()
        process = _context.Process(target=_create_many, args=(start, child_conn))
        process.start()

        connections.append(parent_conn)
        processes.append(process)

    start.set()

    created = 0
    refused = 0

    for parent_conn in connections:
        assert parent_conn.poll(ModuleCtx.Report_Timeout)
        outcomes = parent_conn.recv()

        created += outcomes['created']
        refused += outcomes['refused']

    for process in processes:
        process.join(ModuleCtx.Report_Timeout)
        assert process.exitcode == 0

    attempts = ModuleCtx.Worker_Count * ModuleCtx.Greenlets_Per_Worker * ModuleCtx.Creates_Per_Greenlet

    # .. and the identity received exactly its cap of them.
    assert created == ModuleCtx.Max_Sessions
    assert refused == attempts - ModuleCtx.Max_Sessions

# ################################################################################################################################
# ################################################################################################################################
