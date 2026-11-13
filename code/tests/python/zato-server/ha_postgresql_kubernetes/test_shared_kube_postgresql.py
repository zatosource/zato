# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The fault of the database under traffic. Its pod is deleted, which takes the pub/sub database and the referee
# away from both pods at once, until its StatefulSet creates the pod again with its volume.

# stdlib
import time

# Zato
from ha_checks import check_scheduler, check_workload
from kube_checks import get_pair, ModuleCtx as ChecksCtx, start_workload
from kube_cluster import get_pod_uid, kubectl, ModuleCtx as ClusterCtx, wait_for_rollout
from kube_faults import delete_pod
from kube_postgresql import ModuleCtx as PostgreSQLCtx
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment
    from kube_postgresql import KubePostgreSQL
    from zato.common.typing_ import any_

    KubePostgreSQL = KubePostgreSQL
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the StatefulSet may take to create the pod again, and how often the pod is read meanwhile, in seconds
    Replace_Timeout = 300
    Poll_Interval = 0.5

    # The scheduler claims that the active server may have taken without running them while it was stopped
    Unrun_Claims = 1

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_new_pod(deleted_uid:'str') -> 'None':
    """ Waits until the StatefulSet created the pod of the database again, under its name with a new identity.
    """
    deadline = time.monotonic() + ModuleCtx.Replace_Timeout

    while True:
        result = kubectl('get', 'pod', PostgreSQLCtx.Pod_Name, '-n', ClusterCtx.Namespace, '-o', 'jsonpath={.metadata.uid}',
            check=False)

        uid = result.stdout.strip()

        if uid:
            if uid != deleted_uid:
                return

        assert time.monotonic() < deadline, f'Pod {PostgreSQLCtx.Pod_Name} not created again'
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

def test_postgresql_pod_deleted(kube_pair:'KubeEnvironment') -> 'None':
    """ The pod of the database is deleted under traffic. The standby does not take over, and once the database
    returns with its volume, the same pod is active under the same generation and nothing acknowledged is lost.
    """
    env = kube_pair
    referee = cast_('KubePostgreSQL', env.referee)
    workload = start_workload(env)

    active, _ = get_pair(env)

    record = referee.read_record()
    assert record is not None
    generation = record['generation']

    deleted_uid = get_pod_uid(PostgreSQLCtx.Pod_Name)
    started = delete_pod(PostgreSQLCtx.Pod_Name)

    _wait_for_new_pod(deleted_uid)
    wait_for_rollout('statefulset', PostgreSQLCtx.StatefulSet_Name)
    referee.wait_until_ready()

    returned = env.wait_for_pair(ChecksCtx.Recovery_Timeout)
    assert returned is active, f'{returned.pod_name} became active instead of {active.pod_name}'

    record = referee.read_record()
    assert record is not None
    assert record['generation'] == generation, record
    assert record['active_node'] == active.pod_name, record

    workload.fault_windows.append((started, time.time()))

    check_workload(cast_('any_', env), workload)
    _ = check_scheduler(cast_('any_', env), active, ModuleCtx.Unrun_Claims)

# ################################################################################################################################
# ################################################################################################################################
