# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import resource
import shutil
import tempfile
from time import monotonic

# gevent
from gevent import sleep

# Zato
from zato.common.test.pubsub_database import get_runtime_dir, pubsub_db_env, PubSubDatabase, PubSubDBMode
from zato.common.test.pubsub_replication import ReplicatedDatabase

# local
from checks import check_counts_equal_rows, check_delivery
from workload import stop_running_workloads, Workload

# ################################################################################################################################
# ################################################################################################################################

# The largest file that the process may write while the storage is full, in bytes.
_file_size_limit = 256 * 1024 * 1024

# How large each payload is, in characters.
_padding_size = 65_536

# How long the traffic may take to reach the limit, how long the limit stays in place,
# how long the traffic runs once it is lifted and how long the backlog may take to drain, in seconds.
_fill_timeout = 300
_full_seconds = 10
_traffic_after_seconds = 10
_drain_timeout = 300

# How many messages one pull hands out at most, which bounds what a pull whose response was lost takes along.
_pull_max_messages = 100

# ################################################################################################################################
# ################################################################################################################################

def _run_full_disk(database:'ReplicatedDatabase', soft_limit:'int', hard_limit:'int') -> 'None':

    workload = Workload('full-disk-sqlite', _padding_size)
    workload.backend.take_over()
    workload.subscribe()

    # The process may write files up to the limit only, and nothing is consumed until it is lifted,
    # so the backlog grows the file ..
    resource.setrlimit(resource.RLIMIT_FSIZE, (_file_size_limit, hard_limit))

    workload.start(with_consumers=False)

    # .. the traffic reaches it ..
    deadline = monotonic() + _fill_timeout

    while workload.publisher_state.errors == 0:
        assert monotonic() < deadline, f'The limit was not reached in {_fill_timeout}s'
        sleep(0.5)

    full_time = monotonic()
    sleep(_full_seconds)

    # .. the limit is lifted and the backlog is consumed ..
    resource.setrlimit(resource.RLIMIT_FSIZE, (soft_limit, hard_limit))
    restore_time = monotonic()

    workload.start_consumers()

    sleep(_traffic_after_seconds)
    workload.stop_publishing()

    # .. each pull whose response was lost may have taken at most one batch along ..
    failed_pulls = 0
    for failed_time in workload.failed_pull_times:
        if failed_time >= full_time - 1:
            failed_pulls += 1

    workload.wait_until_delivered(_drain_timeout, failed_pulls * _pull_max_messages, set())
    workload.stop()

    measurements = check_delivery(database, workload, restore_time)
    measurements['publish_error_sample'] = workload.publisher_state.error_messages[:1]

    print(f'\nFull disk SQLite -> {measurements}')

    # .. nothing acknowledged was lost and every component resumed.
    assert measurements['lost'] == 0, measurements

    for name in ('publish_resumed_after', 'pull_resumed_after', 'push_resumed_after', 'cleanup_resumed_after'):
        assert measurements[name] >= 0, measurements

    check_counts_equal_rows(database, workload)

# ################################################################################################################################

def test_full_disk_sqlite() -> 'None':
    """ The SQLite file of the server reaches the largest size that the process may write during traffic.
    Publications that were not written fail and are repeated, nothing acknowledged is lost,
    and processing resumes once the limit is lifted.
    """
    work_dir = tempfile.mkdtemp(prefix='zato_pubsub_full_disk_sqlite_', dir=get_runtime_dir())
    db_path = os.path.join(work_dir, 'pubsub.db')

    env = {
        'Zato_PubSub_DB_Path': db_path,
        'Zato_PubSub_Generation_File': os.path.join(work_dir, 'generation'),
    }

    primary = PubSubDatabase(mode=PubSubDBMode.SQLite, env=env)
    database = ReplicatedDatabase(mode=PubSubDBMode.SQLite, is_sync=False, primary=primary, env=env)

    soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_FSIZE)

    try:
        with pubsub_db_env(env):
            try:
                _run_full_disk(database, soft_limit, hard_limit)
            finally:
                stop_running_workloads()

    finally:
        resource.setrlimit(resource.RLIMIT_FSIZE, (soft_limit, hard_limit))
        shutil.rmtree(work_dir)

# ################################################################################################################################
# ################################################################################################################################
