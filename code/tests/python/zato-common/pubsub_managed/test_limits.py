# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import sleep, spawn

# Zato
from faults import Total_Loss
from managed_faults import CPUCreditFault, IdleFault, StorageTierFault
from profiles import get_profile_limits
from run import FaultRun
from zato.common.test.pubsub_database import connect, ModuleCtx
from zato.common.test.pubsub_profile import Managed_Profiles

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import ManagedDatabase
    from profiles import StorageTier
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The server processes of the active-standby arrangement, each of which has a pool of its own,
# besides the pool of the cleanup process.
_server_count = 2

# The processes of a fault run that connect to the database - the server of the test and its cleanup process.
_run_process_count = 2

# How often the connections are counted, in seconds.
_sample_seconds = 1

# The connections of the pub/sub role and all the client connections.
_connections_query = """
    select count(*) filter (where usename = %s), count(*)
    from pg_stat_activity where backend_type = 'client backend'
"""

# The connection limit and the connections that it reserves.
_limit_query = """
    select current_setting('max_connections')::int,
        current_setting('superuser_reserved_connections')::int,
        current_setting('reserved_connections')::int
"""

# ################################################################################################################################
# ################################################################################################################################

class ConnectionSampler:
    """ Counts the connections of pub/sub and all the client connections once a second and keeps the highest counts.
    """

    def __init__(self, database:'PubSubDatabase') -> 'None':
        self.database = database
        self.peak_pubsub = 0
        self.peak_total = 0
        self._greenlet:'any_' = None

# ################################################################################################################################

    def _sample(self) -> 'None':
        connection = connect(self.database, is_admin=True)

        try:
            cursor = connection.cursor()

            while True:
                cursor.execute(_connections_query, (ModuleCtx.Username,))
                row:'any_' = cursor.fetchone()
                pubsub_count, total_count = row

                self.peak_pubsub = max(self.peak_pubsub, pubsub_count)
                self.peak_total = max(self.peak_total, total_count)

                connection.commit()
                sleep(_sample_seconds)

        finally:
            connection.close()

# ################################################################################################################################

    def start(self) -> 'None':
        self._greenlet = spawn(self._sample)

# ################################################################################################################################

    def stop(self) -> 'None':
        self._greenlet.kill()

# ################################################################################################################################
# ################################################################################################################################

def _get_available_connections(database:'PubSubDatabase') -> 'int':
    """ Returns the connections that the clients other than the superusers may open.
    """
    connection = connect(database, is_admin=True)

    try:
        cursor = connection.cursor()
        cursor.execute(_limit_query)
        row:'any_' = cursor.fetchone()
        max_connections, superuser_reserved, reserved = row
    finally:
        connection.close()

    out = max_connections - superuser_reserved - reserved
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_storage_tier(managed_database:'ManagedDatabase', storage_tier:'StorageTier') -> 'None':
    """ The storage of the database provides the operations per second and the bandwidth
    of a storage tier, including a burst that runs out during the traffic.
    """
    fault = StorageTierFault(managed_database.container, managed_database.device, storage_tier)

    run = FaultRun(fault.name)
    run.run(fault, Total_Loss)
    run.check()

# ################################################################################################################################

def test_cpu_credits(managed_database:'ManagedDatabase') -> 'None':
    """ A burstable instance class ran out of its CPU credits and is left with its baseline CPUs.
    """
    limits = get_profile_limits()
    fault = CPUCreditFault(managed_database.container, limits.baseline_cpus)

    run = FaultRun(fault.name)
    run.run(fault, Total_Loss)
    run.check()

# ################################################################################################################################

def test_connection_limits(managed_database:'ManagedDatabase') -> 'None':
    """ The pools of both servers and of the cleanup process fit within the connections
    that a small instance class leaves to the clients, and the traffic opens no more connections than its pools hold.
    """
    database = managed_database.database
    profile = Managed_Profiles[database.profile_name]

    available = _get_available_connections(database)

    # The pools as configured fit within the limit ..
    process_count = _server_count + 1
    capacity = process_count * profile.pool_size

    assert capacity <= available, f'Pools of {process_count} processes hold {capacity} connections, {available} available'

    # .. and so do the connections that the traffic opens.
    sampler = ConnectionSampler(database)
    sampler.start()

    fault = IdleFault('connection-limits')

    try:
        run = FaultRun(fault.name)
        run.run(fault, Total_Loss)
    finally:
        sampler.stop()

    run.check()

    run_capacity = _run_process_count * profile.pool_size

    assert sampler.peak_pubsub <= run_capacity, (sampler.peak_pubsub, run_capacity)
    assert sampler.peak_total <= available, (sampler.peak_total, available)

# ################################################################################################################################
# ################################################################################################################################
