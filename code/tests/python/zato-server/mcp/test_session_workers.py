# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import traceback
from multiprocessing import get_context

# SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import event as sa_event

# Zato
from zato.common.db_env.connection import set_sqlite_pragmas
from zato.common.pubsub.sql.schema import metadata
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from multiprocessing.process import BaseProcess
    from multiprocessing.synchronize import Event
    from zato.common.typing_ import any_, list_

    any_ = any_
    BaseProcess = BaseProcess
    Connection = Connection
    Event = Event

    connectionlist = list_[Connection]
    processlist    = list_[BaseProcess]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Gateway_Name = 'test.mcp.gateway'
    Identity = 'test.identity'
    Protocol_Version = '2025-06-18'

    Worker_Count = 3
    Queue = 0

    # How many greenlets of each worker create sessions at once, how many each of them creates, and the cap of the identity
    Greenlets_Per_Worker = 2
    Creates_Per_Greenlet = 4
    Max_Sessions = 5

    # How long a write waits for its turn at most, and how long the test waits for a worker, in seconds
    Deadline = 20.0
    Report_Timeout = 60.0

# ################################################################################################################################
# ################################################################################################################################

# Workers are forked, as the arbiter forks them, so that they inherit the mapping and the descriptors
_context = get_context('fork')

_region_config = {
    'slot_count': ModuleCtx.Worker_Count,
    'wake_capacity': 8,
    'cell_capacity': 8,
    'queue_count': 1,
    'metric_count': 1,
    'series_capacity': 0,
    'series_key_bytes': 0,
    'dedup_capacity': 0,
    'breaker_capacity': 0,
    'lock_capacity': 0,
    'start_id': 1,
}

# ################################################################################################################################
# ################################################################################################################################

def _create_schema(db_path:'str') -> 'None':
    """ Creates the tables of the pub/sub database in the WAL mode before the workers are forked, as the arbiter does,
    through an engine of its own, so that no worker inherits a connection.
    """
    engine = create_engine(f'sqlite:///{db_path}')
    sa_event.listen(engine, 'connect', set_sqlite_pragmas)

    metadata.create_all(engine)
    engine.dispose()

# ################################################################################################################################

def _run_step(step:'str', session_id:'str', conn:'Connection') -> 'None':
    """ Performs one step of the life of a session in a worker of its own and reports its result.
    """
    exit_code = 1

    try:
        from zato.server.connection.mcp.session import MCPSessionManager

        manager = MCPSessionManager(ModuleCtx.Gateway_Name)

        if step == 'create':
            out = manager.create(ModuleCtx.Protocol_Version, ModuleCtx.Identity)

        elif step == 'validate':
            out = manager.validate(session_id, ModuleCtx.Identity), manager.get_protocol_version(session_id)

        else:
            out = manager.delete(session_id)

        conn.send(out)
        exit_code = 0

    # The exception reaches the output of the test, since the worker exits without unwinding
    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def _run_in_worker(step:'str', session_id:'str') -> 'any_':
    parent_conn, child_conn = _context.Pipe()

    process = _context.Process(target=_run_step, args=(step, session_id, child_conn))
    process.start()

    assert parent_conn.poll(ModuleCtx.Report_Timeout)
    out = parent_conn.recv()

    process.join(ModuleCtx.Report_Timeout)
    assert process.exitcode == 0

    return out

# ################################################################################################################################

def _create_many(region:'SharedRegion', slot:'int', start:'Event', conn:'Connection') -> 'None':
    """ Creates sessions of one identity from several greenlets of one worker and reports how many were created
    and how many were refused.
    """
    exit_code = 1

    try:

        # A real worker runs with Django settings configured, so the lazy settings object a preceding test
        # left in this process resolves to defaults instead of raising while gevent scans existing locks.
        from django.conf import settings as django_settings
        if not django_settings.configured:
            django_settings.configure()

        # The worker runs under gevent, as a server does, and takes turns with the other workers
        # for the writes to the pub/sub database ..
        from gevent import joinall, monkey, reinit, spawn
        reinit()
        _ = monkey.patch_all()

        from zato.common.db_env.engine import set_process_queue
        from zato.common.db_env.process_queue import ProcessQueue
        from zato.common.pubsub.sql.config import get_pubsub_engine
        from zato.server.connection.mcp.session import MCPSessionManager

        engine = get_pubsub_engine()
        process_queue = ProcessQueue(region, ModuleCtx.Queue, slot, ModuleCtx.Deadline)
        set_process_queue(engine, process_queue)

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

        # .. every worker starts at once ..
        _ = start.wait(ModuleCtx.Report_Timeout)

        greenlets = []

        for _ in range(ModuleCtx.Greenlets_Per_Worker):
            greenlet = spawn(create_some)
            greenlets.append(greenlet)

        _ = joinall(greenlets, raise_error=True)

        # .. and reports what it achieved.
        conn.send(outcomes)
        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

def test_a_session_created_through_one_worker_is_found_through_every_other(pubsub_db_path:'str') -> 'None':
    _create_schema(pubsub_db_path)

    # One worker creates the session ..
    session_id = _run_in_worker('create', '')

    # .. another one finds it with its protocol version ..
    assert _run_in_worker('validate', session_id) == ('session_valid', ModuleCtx.Protocol_Version)

    # .. a third one deletes it ..
    assert _run_in_worker('delete', session_id) is True

    # .. after which no worker finds it.
    assert _run_in_worker('validate', session_id) == ('session_not_found', None)

# ################################################################################################################################

def test_the_workers_together_create_no_more_sessions_than_the_cap(pubsub_db_path:'str') -> 'None':
    _create_schema(pubsub_db_path)

    region = SharedRegion(_region_config)
    start = _context.Event()

    connections:'connectionlist' = []
    processes:'processlist' = []

    for slot in range(ModuleCtx.Worker_Count):
        parent_conn, child_conn = _context.Pipe()
        process = _context.Process(target=_create_many, args=(region, slot, start, child_conn))
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

    # Every worker created sessions at once, and the identity received exactly its cap of them
    assert created == ModuleCtx.Max_Sessions
    assert refused == attempts - ModuleCtx.Max_Sessions

# ################################################################################################################################
# ################################################################################################################################
