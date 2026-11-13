# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faults of the Consul leader pod under traffic. The leader pod is paused and resumed, or partitioned from the other
# Consul pods while it reaches the Zato pods. The other Consul pods elect a new leader, and with the standby in sync,
# the active pod continues in both cases.

# stdlib
import time

# pytest
import pytest

# Zato
from kube_checks import finish, get_pair, start_workload
from kube_cluster import get_pod_node
from kube_consul_leader import get_leader_pod, partition_pod
from kube_faults import freeze_pod, heal_node, thaw_pod
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeConsul, KubeEnvironment

    KubeConsul = KubeConsul

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The faults of the leader pod
    Fault_Pause = 'pause'
    Fault_Partition = 'partition'

    Faults = [Fault_Pause, Fault_Partition]

    # How long the traffic runs during the fault, in seconds
    Traffic_Seconds = 30

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault', ModuleCtx.Faults)
def test_consul_leader_fault(kube_pair:'KubeEnvironment', fault:'str') -> 'None':
    """ The Consul leader pod is paused or partitioned from the other Consul pods under traffic, the active pod keeps
    its role and generation and acknowledges publications throughout, and Consul returns with its data.
    """
    env = kube_pair
    consul = cast_('KubeConsul', env.referee)
    workload = start_workload(env)

    active, _ = get_pair(env)

    record = consul.read_record()
    assert record is not None
    generation = record['generation']

    leader = get_leader_pod(consul)
    node_name = get_pod_node(leader)

    acknowledged_before = len(workload.acknowledged)

    if fault == ModuleCtx.Fault_Pause:
        started = freeze_pod(leader, node_name)
    else:
        started = partition_pod(leader, node_name)

    time.sleep(ModuleCtx.Traffic_Seconds)

    assert active.is_active(), f'{active.pod_name} left its role during the fault of Consul leader {leader}'
    assert len(workload.acknowledged) > acknowledged_before, f'No publication acknowledged during the fault of {leader}'

    if fault == ModuleCtx.Fault_Pause:
        thaw_pod(leader, node_name)
    else:
        heal_node(node_name)

    consul.wait_until_ready()

    record = consul.read_record()
    assert record is not None
    assert record['generation'] == generation, record
    assert record['active_node'] == active.pod_name, record

    workload.fault_windows.append((started, time.time()))

    _ = finish(env, workload, started)

# ################################################################################################################################
# ################################################################################################################################
