# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import subprocess
import tempfile
from time import monotonic

# gevent
from gevent import sleep

# Zato
from zato.common.test.pubsub_database import connect, get_runtime_dir, pubsub_db_env, start_pubsub_database, \
     stop_pubsub_database
from zato.common.test.pubsub_replication import ReplicatedDatabase

# local
from checks import check_counts_equal_rows, check_delivery
from environment import get_replication_mode
from workload import stop_running_workloads, Workload

# ################################################################################################################################
# ################################################################################################################################

# Where the tablespace of the pub/sub tables is mounted in the container, and how large it is.
_tablespace_dir = '/pubsub_ts'
_tablespace_size = '512m'

# How much of the tablespace the ballast file takes, leaving the rest for the traffic.
_ballast_size = '384M'
_ballast_path = f'{_tablespace_dir}/ballast'

# How large each payload is, in characters.
_padding_size = 65_536

# How long the traffic may take to fill the tablespace, how long the tablespace stays full,
# how long the traffic runs once the space is available again and how long the backlog may take to drain, in seconds.
_fill_timeout = 300
_full_seconds = 10
_traffic_after_seconds = 10
_drain_timeout = 300

# ################################################################################################################################
# ################################################################################################################################

def _docker_exec(container_name:'str', command:'list[str]') -> 'None':
    _ = subprocess.run(['docker', 'exec', container_name, *command], check=True, capture_output=True)

# ################################################################################################################################

def _run_full_disk(database:'ReplicatedDatabase') -> 'None':

    container_name = database.primary.container_name

    # Most of the storage is taken before the traffic starts ..
    _docker_exec(container_name, ['fallocate', '-l', _ballast_size, _ballast_path])

    workload = Workload('full-disk', _padding_size)
    workload.backend.take_over()
    workload.subscribe()
    workload.start()

    # .. the traffic fills the rest ..
    deadline = monotonic() + _fill_timeout

    while workload.publisher_state.errors == 0:
        assert monotonic() < deadline, f'The storage did not fill up in {_fill_timeout}s'
        sleep(0.5)

    full_time = monotonic()
    sleep(_full_seconds)

    acknowledged_while_full = 0
    for acknowledged_time in workload.acknowledged.values():
        if acknowledged_time > full_time + 1:
            acknowledged_while_full += 1

    # .. space becomes available again ..
    _docker_exec(container_name, ['rm', _ballast_path])
    restore_time = monotonic()

    sleep(_traffic_after_seconds)
    workload.stop_publishing()

    # .. every publication reaches its subscriber ..
    workload.wait_until_delivered(_drain_timeout, set())
    workload.stop()

    measurements = check_delivery(database, workload, restore_time)
    measurements['acknowledged_while_full'] = acknowledged_while_full
    measurements['publish_error_sample'] = workload.publisher_state.error_messages[:1]

    print(f'\nFull disk -> {measurements}')

    # .. nothing acknowledged was lost and every component resumed.
    assert measurements['lost'] == 0, measurements

    for name in ('publish_resumed_after', 'pull_resumed_after', 'push_resumed_after', 'cleanup_resumed_after'):
        assert measurements[name] >= 0, measurements

    check_counts_equal_rows(database, workload)

    guard = workload.backend.generation_guard
    assert guard is not None
    guard.uninstall(workload.backend.engine)

# ################################################################################################################################

def test_full_disk() -> 'None':
    """ The storage of the pub/sub tables runs out of space during traffic. Publications that were not written fail
    and are repeated, nothing acknowledged is lost, and processing resumes once space is available again.
    """
    mode = get_replication_mode()
    tmpfs = f'{_tablespace_dir}:rw,size={_tablespace_size},uid={os.getuid()},gid={os.getgid()},mode=0700'

    primary = start_pubsub_database('full-disk', mode, extra_docker_args=['--tmpfs', tmpfs])
    work_dir = tempfile.mkdtemp(prefix='zato_pubsub_full_disk_', dir=get_runtime_dir())

    try:
        database = ReplicatedDatabase(mode=mode, is_sync=False, primary=primary)

        # The pub/sub tables are created in the tablespace on the size-limited storage.
        connection = connect(primary)
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(f"create tablespace pubsub_ts location '{_tablespace_dir}'")
        cursor.execute(f'alter database {primary.env["Zato_PubSub_DB_Name"]} set default_tablespace = pubsub_ts')
        connection.close()

        env = dict(primary.env)
        env['Zato_PubSub_Generation_File'] = os.path.join(work_dir, 'generation')

        with pubsub_db_env(env):
            try:
                _run_full_disk(database)
            finally:
                stop_running_workloads()

    finally:
        stop_pubsub_database(primary)
        shutil.rmtree(work_dir)

# ################################################################################################################################
# ################################################################################################################################
