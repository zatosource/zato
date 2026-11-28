# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import tempfile
from contextlib import contextmanager, ExitStack

# Zato
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.test.expected_records import expected_records
from zato.common.test.pubsub_database import get_db_mode, get_runtime_dir, is_managed_mode, pubsub_db_env, PubSubDBMode
from zato.common.test.pubsub_replication import start_replicated_database, stop_replicated_database

# local
from workload import stop_running_workloads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator, Iterator
    from zato.common.test.pubsub_replication import ReplicatedDatabase

    nonegen = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

# How long a pulled message waits for its acknowledgement, in seconds, short enough for a test to see
# the messages of failed acknowledgements handed out again.
Pull_Lease_Seconds = '5'

# The loggers whose records the faults of the database provoke - the outages of the components that use the database,
# and the pooled connections that could not be closed after their sessions or links were lost.
_fault_logger_names = ['zato.common.db_env.outage', 'sqlalchemy.pool.impl.QueuePool']

# ################################################################################################################################
# ################################################################################################################################

def get_replication_mode() -> 'str':
    """ The replication suites run on PostgreSQL with TLS or in a managed mode when the session asks for it,
    and on PostgreSQL otherwise.
    """
    mode = get_db_mode()

    if mode == PubSubDBMode.PostgreSQL_TLS:
        out = mode
    elif is_managed_mode(mode):
        out = mode
    else:
        out = PubSubDBMode.PostgreSQL

    return out

# ################################################################################################################################

@contextmanager
def expected_fault_records() -> 'nonegen':
    """ Marks each record of the loggers of the database faults as expected while the block runs.
    """
    with ExitStack() as stack:
        for logger_name in _fault_logger_names:
            _ = stack.enter_context(expected_records(logger_name))
        yield

# ################################################################################################################################

@contextmanager
def replicated_environment(label:'str') -> 'Iterator[ReplicatedDatabase]':
    """ A primary, its synchronous standby and the proxy, with the Zato_Database_* variables pointing at the proxy,
    the generation file and the audit log of the test in a directory of their own.
    """
    mode = get_replication_mode()
    database = start_replicated_database(label, mode, is_sync=True)
    work_dir = tempfile.mkdtemp(prefix=f'zato_pubsub_replication_{label}_', dir=get_runtime_dir())

    env = dict(database.env)
    env['Zato_Database_Generation_File'] = os.path.join(work_dir, 'generation')
    env[ModuleCtx.Env_Pull_Lease_Seconds] = Pull_Lease_Seconds

    try:
        with pubsub_db_env(env), expected_fault_records():
            try:
                yield database
            finally:
                stop_running_workloads()
    finally:
        stop_replicated_database(database)
        shutil.rmtree(work_dir)

# ################################################################################################################################
# ################################################################################################################################
