# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The worker and the config process of one server on one SQLite file of the Zato database, started as the arbiter
# starts them. The test process creates the schemas and the shared region with the queue of the file, confirms that
# nothing that a fork would duplicate is open, and forks each process, which records its slot and binds its place
# in the queue of the file before it runs its part of a test.

# stdlib
import os
import traceback
from multiprocessing import get_context

# Zato
from zato.common.db_env.connection import SQLite_Busy_Timeout_Ms
from zato.common.db_env.engine import bind_process_queues, get_queue_by_path
from zato.common.db_env.process_queue import get_deadline_seconds
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx, set_process_slot
from zato.server.arbiter_start import check_fork_ready, get_sqlite_paths, prepare_databases, stop_threadpool
from zato.server.server_region import new_server_region

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from multiprocessing.connection import Connection
    from zato.common.typing_ import any_, anylist, anytuple, callable_, strintdict
    from zato_ipc_core.zato_ipc_core import SharedRegion

    any_ = any_
    anylist = anylist
    anytuple = anytuple
    callable_ = callable_
    Connection = Connection
    SharedRegion = SharedRegion
    strintdict = strintdict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The name of the server whose processes the tests start
    Server_Name = 'test.two-processes'

    # The roles of the processes
    Role_Worker = 'worker'
    Role_Config = 'config'

    # How long a process takes to exit once it reported its results, in seconds
    Exit_Timeout = 30.0

# ################################################################################################################################
# ################################################################################################################################

# The processes are forked, as the arbiter forks them, so that they inherit the mapping and the descriptors
_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

def _run_process(
    region:'SharedRegion',
    queue_by_path:'strintdict',
    role:'str',
    target:'callable_',
    args:'anytuple',
    conn:'Connection',
    ) -> 'None':
    """ Runs the part of a test of one process, with the slot and the place in the queue of the file of its role.
    """
    exit_code = 1

    try:

        # The worker and the config process take their own slots and their own places in the queue ..
        if role == ModuleCtx.Role_Worker:
            slot = WorkerSlotCtx.Worker_Slot
            place = region.worker_place
        else:
            slot = WorkerSlotCtx.Config_Slot
            place = region.config_place

        set_process_slot(slot, WorkerSlotCtx.First_Generation)

        # .. their writes to the file take turns, with the deadline that a server uses ..
        deadline_seconds = get_deadline_seconds(SQLite_Busy_Timeout_Ms)
        bind_process_queues(region, place, deadline_seconds, queue_by_path)

        # .. and each runs its part of the test.
        target(conn, *args)
        exit_code = 0

    # The exception reaches the output of the test, since the process exits without unwinding
    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################
# ################################################################################################################################

class ServerProcesses:
    """ The shared region of one server and the processes forked over it.
    """

    def __init__(self) -> 'None':

        # The schemas exist before any process starts ..
        prepare_databases(ModuleCtx.Server_Name)

        # .. and the SQLite file of the Zato database receives one queue of the region.
        sqlite_paths = get_sqlite_paths()
        self.queue_by_path = get_queue_by_path(sqlite_paths)

        queue_count = len(self.queue_by_path)
        self.region = new_server_region(queue_count)

        self.processes:'anylist' = []

    def start(self, role:'str', target:'callable_', *args:'any_') -> 'Connection':
        """ Forks one process of the given role, which runs the target with the given arguments and a connection
        to the test process, and returns the end of that connection that the test process uses.
        """
        stop_threadpool()
        check_fork_ready()

        parent_conn, child_conn = _context.Pipe()

        process_args = (self.region, self.queue_by_path, role, target, args, child_conn)
        process = _context.Process(target=_run_process, args=process_args)
        process.daemon = True
        process.start()

        self.processes.append(process)

        return parent_conn

    def join(self) -> 'None':
        """ Waits until each process exits and confirms that each of them completed its part of the test.
        """
        for process in self.processes:
            process.join(ModuleCtx.Exit_Timeout)
            assert process.exitcode == 0, process.exitcode

# ################################################################################################################################
# ################################################################################################################################

def receive(conn:'Connection', timeout:'float') -> 'any_':
    """ Returns the next report of a process, which it sends within the given time.
    """
    assert conn.poll(timeout), f'No report in {timeout}s'

    out = conn.recv()
    return out

# ################################################################################################################################
# ################################################################################################################################
