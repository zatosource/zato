# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faults of the Consul servers under traffic. One Consul pod is deleted, which keeps the majority, and two are deleted,
# which loses it until they start again. With the standby in sync, the active pod continues in both cases.

# stdlib
import time

# pytest
import pytest

# Zato
from kube_checks import finish, get_pair, start_workload
from kube_cluster import wait_for_rollout
from kube_env import ModuleCtx as EnvCtx
from kube_faults import delete_consul_pods
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeConsul, KubeEnvironment

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The Consul pods that each test deletes
    Deleted_Pods = [
        ['consul-0'],
        ['consul-0', 'consul-1'],
    ]

    # How long the traffic runs after the pods are deleted, in seconds
    Traffic_Seconds = 30

    # How long requests in flight when the pods were deleted may still be acknowledged, in seconds
    In_Flight_Grace = 2.0

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('pod_names', ModuleCtx.Deleted_Pods)
def test_consul_pods_deleted(kube_pair:'KubeEnvironment', pod_names:'list[str]') -> 'None':
    """ Consul pods are deleted under traffic, the active pod keeps its role and generation and acknowledges
    publications throughout, and Consul returns with its data.
    """
    env = kube_pair
    consul = cast_('KubeConsul', env.referee)
    workload = start_workload(env)

    active, _ = get_pair(env)

    record = consul.read_record()
    assert record is not None
    generation = record['generation']

    acknowledged_before = len(workload.acknowledged)

    started = delete_consul_pods(pod_names)
    time.sleep(ModuleCtx.Traffic_Seconds)

    assert active.is_active(), f'{active.pod_name} left its role while Consul pods were deleted'
    assert len(workload.acknowledged) > acknowledged_before, 'No publication acknowledged while Consul pods were deleted'

    wait_for_rollout('statefulset', EnvCtx.Consul_StatefulSet)
    consul.wait_until_ready()

    record = consul.read_record()
    assert record is not None
    assert record['generation'] == generation, record
    assert record['active_node'] == active.pod_name, record

    workload.fault_windows.append((started, time.time()))

    _ = finish(env, workload, started)

# ################################################################################################################################
# ################################################################################################################################
