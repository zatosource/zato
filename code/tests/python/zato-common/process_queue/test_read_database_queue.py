# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import time
import traceback
from multiprocessing import get_context

# Zato
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from pathlib import Path
    from zato.common.typing_ import any_

    any_ = any_
    Connection = Connection
    Path = Path

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The processes are forked, as the arbiter forks them, so that they inherit the mapping and the descriptors
    Context = get_context('fork')

    Region_Config = {
        'queue_count': 1,
        'lock_capacity': 0,
    }

    Queue = 0

    # The config process holds the turn and the worker reads and writes
    Holder_Place = 1
    Worker_Place = 0

    # The deadline of a write that receives no turn, in seconds
    Write_Deadline = 1.0

    # How often the holder polls for its turn, in seconds
    Poll_Interval = 0.01

    # How long the test waits for a process to report, in seconds
    Report_Timeout = 20.0

    # The shared object that the worker writes before the turn is held and reads while it is held
    Object_Type = 'test.read-database-queue'
    Object_Name = 'object.1'
    Object_Data = {'key': 'value'}

    # What the write of the worker returns when it runs
    Write_Result = 'written'

# ################################################################################################################################
# ################################################################################################################################

def _hold_turn(region:'SharedRegion', conn:'Connection') -> 'None':
    """ Takes the turn of the queue and keeps it until the test asks for its release.
    """
    _ = region.queue_enter(ModuleCtx.Queue, ModuleCtx.Holder_Place)

    while not region.queue_poll(ModuleCtx.Queue, ModuleCtx.Holder_Place):
        time.sleep(ModuleCtx.Poll_Interval)

    conn.send('holding')

    _ = conn.recv()
    region.queue_release(ModuleCtx.Queue, ModuleCtx.Holder_Place)

    conn.send('released')

# ################################################################################################################################

def _read_while_turn_held(region:'SharedRegion', db_path:'str', conn:'Connection') -> 'None':
    """ Writes a shared object while the queue is free, then, once the test reports that the config process holds
    the turn, reads the object through the store and writes through call_database, and reports the outcome of each.
    """
    exit_code = 1

    try:

        # The worker runs under gevent, as a server does, so the store runs its calls in the pool of the hub ..
        from gevent import monkey, reinit
        reinit()
        _ = monkey.patch_all()
        from zato.common.common_db.schema import metadata
        from zato.common.common_db.store import SharedObjectStore
        from zato.common.db_env.engine import call_database, create_schema, new_zato_engine, set_process_queue
        from zato.common.db_env.process_queue import ProcessQueue

        engine = new_zato_engine(f'sqlite:///{db_path}')
        process_queue = ProcessQueue(region, ModuleCtx.Queue, ModuleCtx.Worker_Place, ModuleCtx.Write_Deadline)
        set_process_queue(engine, process_queue)

        # .. the object is written while the queue is free ..
        create_schema(engine, metadata)

        store = SharedObjectStore(engine)
        _ = store.compare_and_set(ModuleCtx.Object_Type, ModuleCtx.Object_Name, ModuleCtx.Object_Data, None)

        conn.send('written')

        # .. and read once the config process holds the turn ..
        _ = conn.recv()

        try:
            shared_object = store.get(ModuleCtx.Object_Type, ModuleCtx.Object_Name)
            shared_objects = store.list(ModuleCtx.Object_Type)
        except Exception as exception:
            read_outcome = type(exception).__name__
        else:
            names:'list[str]' = []

            for item in shared_objects:
                names.append(item.name)

            read_outcome = (shared_object.data, names) # type: ignore

        # .. while a write receives no turn ..
        def write() -> 'str':
            return ModuleCtx.Write_Result

        try:
            write_outcome = call_database(engine, write)
        except Exception as exception:
            write_outcome = type(exception).__name__

        # .. and the worker reports both.
        conn.send((read_outcome, write_outcome))
        exit_code = 0

    # The exception reaches the output of the test, since the worker exits without unwinding
    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def _start(target:'any_', args:'any_') -> 'Connection':
    parent_conn, child_conn = ModuleCtx.Context.Pipe()

    process = ModuleCtx.Context.Process(target=target, args=(*args, child_conn))
    process.daemon = True
    process.start()

    return parent_conn

# ################################################################################################################################

def _receive(conn:'Connection') -> 'any_':
    assert conn.poll(ModuleCtx.Report_Timeout)
    out = conn.recv()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_store_reads_do_not_wait_for_the_turn_of_the_config_process(tmp_path:'Path') -> 'None':
    region = SharedRegion(ModuleCtx.Region_Config)
    db_path = str(tmp_path / 'store-reads.db')

    # The worker writes the object while the queue is free ..
    worker_conn = _start(_read_while_turn_held, (region, db_path))
    assert _receive(worker_conn) == 'written'

    # .. the config process takes the turn and keeps it throughout ..
    holder_conn = _start(_hold_turn, (region,))
    assert _receive(holder_conn) == 'holding'

    # .. the reads of the worker return the object, while its write raises at the deadline without running ..
    worker_conn.send('read')
    read_outcome, write_outcome = _receive(worker_conn)

    assert read_outcome == (ModuleCtx.Object_Data, [ModuleCtx.Object_Name])
    assert write_outcome == 'ProcessQueueTimeout'

    # .. and the config process releases its turn.
    holder_conn.send('release')
    assert _receive(holder_conn) == 'released'

# ################################################################################################################################
# ################################################################################################################################
