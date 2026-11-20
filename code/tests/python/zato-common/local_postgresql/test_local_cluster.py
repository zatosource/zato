# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.local_postgresql import LocalCluster, remove_stale_clusters, run_psql, start_local_cluster, \
    stop_local_cluster
from zato.common.test.pubsub_database import get_container_settings, PubSubDatabase, PubSubDBMode
from zato.common.test.reservation import is_name_live, is_port_reserved

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intlist, list_, strlist

    clusterlist = list_[LocalCluster]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The superuser and the database of the clusters
    Username = 'zato_pubsub'
    Database = 'zato_pubsub'

    # The major version of the local build
    Major_Version = '19'

    # How many clusters start at the same time
    Concurrent_Clusters = 2

    # How long a process may take to report its cluster or to exit, and how often a process is checked, in seconds
    Process_Timeout = 120
    Poll_Interval = 0.1

    # The program of the process that holds a cluster
    Holder_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cluster_holder.py')

# ################################################################################################################################
# ################################################################################################################################

def _start_cluster() -> 'LocalCluster':
    """ Starts a cluster with the settings of the PostgreSQL containers of the tests.
    """
    password = 'pubsub.' + CryptoManager.generate_hex_string()

    database = PubSubDatabase(mode=PubSubDBMode.PostgreSQL_Local)
    settings = get_container_settings(database, None)

    out = start_local_cluster(ModuleCtx.Username, password, ModuleCtx.Database, settings)
    return out

# ################################################################################################################################

def _is_running(pid:'int') -> 'bool':
    """ Returns whether a process exists and has not exited.
    """
    try:
        with open(f'/proc/{pid}/stat') as stat_file:
            stat = stat_file.read()
    except FileNotFoundError:
        return False

    _, _, remainder = stat.rpartition(')')
    fields = remainder.split()
    state = fields[0]

    out = state != 'Z'
    return out

# ################################################################################################################################

def _wait_until_exited(pids:'intlist') -> 'None':
    """ Waits until none of the processes runs.
    """
    deadline = time.monotonic() + ModuleCtx.Process_Timeout

    for pid in pids:
        while _is_running(pid):
            assert time.monotonic() < deadline, f'Process {pid} still runs'
            time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def _get_postmaster_pids(cluster:'LocalCluster') -> 'intlist':
    """ Returns the PIDs of the postmasters of a cluster.
    """
    out:'intlist' = []

    for instance in (cluster.primary, cluster.standby):
        pid_path = os.path.join(instance.data_dir, 'postmaster.pid')

        with open(pid_path) as pid_file:
            first_line = pid_file.readline()

        pid = int(first_line)
        out.append(pid)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_standby_is_synchronous() -> 'None':
    """ The primary runs the local build and makes its commits wait for the standby, which is in recovery.
    """
    cluster = _start_cluster()

    try:
        version = run_psql(cluster, cluster.primary, 'SHOW server_version_num')
        sync_state = run_psql(cluster, cluster.primary, 'SELECT sync_state FROM pg_stat_replication')
        synchronous_names = run_psql(cluster, cluster.primary, 'SHOW synchronous_standby_names')
        is_in_recovery = run_psql(cluster, cluster.standby, 'SELECT pg_is_in_recovery()')

        assert version.startswith(ModuleCtx.Major_Version)
        assert sync_state == 'sync'
        assert synchronous_names == 'standby'
        assert is_in_recovery == 't'

    finally:
        stop_local_cluster(cluster)

# ################################################################################################################################

def test_concurrent_clusters_are_distinct() -> 'None':
    """ Clusters that start at the same time receive ports and directories of their own.
    """
    with ThreadPoolExecutor(ModuleCtx.Concurrent_Clusters) as executor:
        futures = []

        for _ in range(ModuleCtx.Concurrent_Clusters):
            future = executor.submit(_start_cluster)
            futures.append(future)

        clusters:'clusterlist' = []

        for future in futures:
            cluster = future.result()
            clusters.append(cluster)

    try:
        ports:'intlist' = []
        base_dirs:'strlist' = []

        for cluster in clusters:
            ports.append(cluster.primary.port)
            ports.append(cluster.standby.port)
            base_dirs.append(cluster.base_dir)

        distinct_ports = set(ports)
        distinct_dirs = set(base_dirs)

        assert len(distinct_ports) == len(ports)
        assert len(distinct_dirs) == len(base_dirs)

        for cluster in clusters:
            sync_state = run_psql(cluster, cluster.primary, 'SELECT sync_state FROM pg_stat_replication')
            assert sync_state == 'sync'

    finally:
        for cluster in clusters:
            stop_local_cluster(cluster)

# ################################################################################################################################

def test_removal_leaves_nothing_behind() -> 'None':
    """ A stopped cluster leaves no process, no directory and no reservation behind.
    """
    cluster = _start_cluster()
    pids = _get_postmaster_pids(cluster)

    stop_local_cluster(cluster)
    _wait_until_exited(pids)

    assert not os.path.exists(cluster.base_dir)
    assert not is_name_live(cluster.reservation.name)
    assert not is_port_reserved(cluster.primary.port)
    assert not is_port_reserved(cluster.standby.port)

# ################################################################################################################################

def test_cluster_of_killed_process_is_removed() -> 'None':
    """ A cluster whose process was killed is stopped and removed when the next cluster starts.
    """
    command = [sys.executable, ModuleCtx.Holder_Path]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    stdout = process.stdout
    assert stdout is not None

    line = stdout.readline()
    report = json.loads(line)

    process.kill()
    _ = process.wait(ModuleCtx.Process_Timeout)

    # The postmasters outlive the process that started them ..
    for pid in report['pids']:
        assert _is_running(pid)

    assert not is_name_live(report['name'])

    # .. until the stale clusters are removed.
    remove_stale_clusters()
    _wait_until_exited(report['pids'])

    assert not os.path.exists(report['base_dir'])

    for port in report['ports']:
        assert not is_port_reserved(port)

# ################################################################################################################################
# ################################################################################################################################
