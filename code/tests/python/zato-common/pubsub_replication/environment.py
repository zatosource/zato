# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import tempfile
from contextlib import contextmanager

# Zato
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.test.pubsub_database import get_db_mode, get_runtime_dir, pubsub_db_env, PubSubDBMode
from zato.common.test.pubsub_replication import start_replicated_database, stop_replicated_database

# local
from workload import stop_running_workloads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.test.pubsub_replication import ReplicatedDatabase

# ################################################################################################################################
# ################################################################################################################################

# How long a pulled message waits for its acknowledgement, in seconds, short enough for a test to see
# the messages of failed acknowledgements handed out again.
Pull_Lease_Seconds = '5'

# ################################################################################################################################
# ################################################################################################################################

def get_replication_mode() -> 'str':
    """ The replication suites run on PostgreSQL with TLS when the session asks for TLS, and on PostgreSQL otherwise.
    """
    if get_db_mode() == PubSubDBMode.PostgreSQL_TLS:
        out = PubSubDBMode.PostgreSQL_TLS
    else:
        out = PubSubDBMode.PostgreSQL

    return out

# ################################################################################################################################

@contextmanager
def replicated_environment(label:'str', is_sync:'bool') -> 'Iterator[ReplicatedDatabase]':
    """ A primary, its standby and the proxy, with the Zato_PubSub_DB_* variables pointing at the proxy,
    the generation file and the audit log of the test in a directory of their own.
    """
    mode = get_replication_mode()
    database = start_replicated_database(label, mode, is_sync)
    work_dir = tempfile.mkdtemp(prefix=f'zato_pubsub_replication_{label}_', dir=get_runtime_dir())

    env = dict(database.env)
    env['Zato_PubSub_Generation_File'] = os.path.join(work_dir, 'generation')
    env['Zato_Audit_Log_DB_Name'] = os.path.join(work_dir, 'audit.db')
    env[ModuleCtx.Env_Pull_Lease_Seconds] = Pull_Lease_Seconds

    try:
        with pubsub_db_env(env):
            try:
                yield database
            finally:
                stop_running_workloads()
    finally:
        stop_replicated_database(database)
        shutil.rmtree(work_dir)

# ################################################################################################################################
# ################################################################################################################################
