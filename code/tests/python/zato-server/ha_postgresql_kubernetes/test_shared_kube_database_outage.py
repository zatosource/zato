# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Outages of the database longer than the takeover time, repeated under traffic. The primary of the local build stops
# and starts again on its reserved port. During an outage neither pod renews or takes over the lease, and once
# the primary returns, the active pod renews its lease and keeps its role, its generation and its running server,
# while the other pod remains its standby.

# stdlib
import logging
import time
from dataclasses import dataclass

# Zato
from ha_checks import check_scheduler, check_workload
from kube_checks import ModuleCtx as ChecksCtx, start_workload, wait_for_publications
from kube_env import ModuleCtx as EnvCtx
from kube_faults import get_server_pids
from kube_local_postgresql import KubeLocalPostgreSQL
from zato.common.test.local_postgresql import LocalCluster, start_primary, stop_primary
from zato.common.typing_ import any_, cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment
    from workload import Workload
    from zato.common.typing_ import intset, strlist

# ################################################################################################################################
# ################################################################################################################################

outage_result_list = list['OutageResult']

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.database_outage')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many outages one test runs
    Outages = 20

    # How long each outage lasts, which exceeds the takeover time of the pods, in seconds
    Outage_Seconds = 15

    # How long the lease may take to be written once the primary returned, and how often it is read meanwhile, in seconds
    Lease_Write_Timeout = 60
    Poll_Interval = 0.5

    # How long the active server may take to acknowledge publications again once the pair returned, in seconds
    Resume_Timeout = 45

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutageResult:
    """ The pod that held the lease before one outage and after it, with its generation and the PIDs of its server.
    """
    index: 'int'
    active_before: 'str'
    active_after: 'str'
    generation_before: 'int'
    generation_after: 'int'
    pids_before: 'intset'
    pids_after: 'intset'
    standby_role: 'str'

    def is_kept(self) -> 'bool':
        """ Returns whether the active pod kept its lease, its generation and its server, with the other pod its standby.
        """
        if self.active_after != self.active_before:
            return False

        if self.generation_after != self.generation_before:
            return False

        if self.pids_after != self.pids_before:
            return False

        out = self.standby_role == EnvCtx.Role_Standby
        return out

    def describe(self) -> 'str':
        out = f'outage {self.index}: {self.active_before} at {self.generation_before} with {sorted(self.pids_before)} ->' + \
            f' {self.active_after} at {self.generation_after} with {sorted(self.pids_after)}, standby {self.standby_role}'
        return out

# ################################################################################################################################
# ################################################################################################################################

def _get_local_cluster(env:'KubeEnvironment') -> 'LocalCluster':
    """ Returns the local cluster whose primary the pods of the pair use as their Zato database.
    """
    backend = cast_(KubeLocalPostgreSQL, env.session.backends[0])

    out = cast_(LocalCluster, backend.database.local_cluster)
    return out

# ################################################################################################################################

def _read_version(env:'KubeEnvironment') -> 'str':
    """ Returns the version of the referee record.
    """
    record = env.referee.read_record()
    assert record is not None, 'No referee record'

    out = record['version']
    return out

# ################################################################################################################################

def _wait_for_lease_write(env:'KubeEnvironment', version:'str') -> 'None':
    """ Waits until the referee record has a version other than the given one, which a renewal or a takeover writes.
    """
    deadline = time.monotonic() + ModuleCtx.Lease_Write_Timeout

    while True:
        current = _read_version(env)

        if current != version:
            return

        assert time.monotonic() < deadline, f'Lease not written within {ModuleCtx.Lease_Write_Timeout}s, version {version}'
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################

def _run_outage(env:'KubeEnvironment', cluster:'LocalCluster', workload:'Workload', index:'int') -> 'OutageResult':
    """ Stops the primary for longer than the takeover time, starts it again and returns which pod holds the lease
    once the pair serves again.
    """
    # Our response to produce
    out = OutageResult()
    out.index = index

    # The pair is formed before the outage ..
    active = env.wait_for_pair(ChecksCtx.Recovery_Timeout)

    record = env.referee.read_record()
    assert record is not None, 'No referee record'

    out.active_before = active.pod_name
    out.generation_before = record['generation']
    out.pids_before = get_server_pids(active.pod_name)

    # .. the primary stops for longer than the takeover time, during which neither pod writes the lease ..
    started = time.time()
    stop_primary(cluster)
    time.sleep(ModuleCtx.Outage_Seconds)

    version = _read_version(env)

    # .. the primary returns, the lease is written again, the pair forms and the active server acknowledges
    # publications again ..
    start_primary(cluster)
    _wait_for_lease_write(env, version)

    returned = env.wait_for_pair(ChecksCtx.Recovery_Timeout)
    wait_for_publications(workload, ModuleCtx.Resume_Timeout)

    workload.fault_windows.append((started, time.time()))

    # .. and the record, the server of the active pod and the role of the other pod tell what the outage left.
    record = env.referee.read_record()
    assert record is not None, 'No referee record'

    standby = env.get_other(returned)
    report = standby.read_role()
    assert report is not None, f'No role from {standby.pod_name}'

    out.active_after = returned.pod_name
    out.generation_after = record['generation']
    out.pids_after = get_server_pids(returned.pod_name)
    out.standby_role = report['role']

    logger.info('Result of %s', out.describe())

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_database_outage_keeps_the_active_pod(local_pair:'KubeEnvironment') -> 'None':
    """ The primary is unavailable to both pods for longer than the takeover time, repeatedly and under traffic.
    After every outage, the pod that was active holds the lease at its generation with the same server,
    the other pod is its standby, and nothing acknowledged is lost.
    """
    env = local_pair
    cluster = _get_local_cluster(env)
    workload = start_workload(env)

    results:'outage_result_list' = []

    for index in range(ModuleCtx.Outages):
        result = _run_outage(env, cluster, workload, index)
        results.append(result)

    taken_over:'strlist' = []

    for result in results:
        if not result.is_kept():
            description = result.describe()
            taken_over.append(description)

    assert not taken_over, f'Outages after which the active pod did not keep its lease -> {taken_over}'

    # Each outage may end a claim whose commit or whose confirmation before the run the server did not receive,
    # which the run state counts without a run.
    unrun_claims = ModuleCtx.Outages * ChecksCtx.Unrun_Claims_After_Fault

    check_workload(cast_(any_, env), workload)
    _ = check_scheduler(cast_(any_, env), unrun_claims)

# ################################################################################################################################
# ################################################################################################################################
