# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faults of the worker node of the active pod under traffic - the node is drained, its container is stopped, which
# takes its zone away, it is paused and resumed, and it is partitioned from the other zones while it still reaches
# the control plane. The standby takes over each time, and the active pod joins again once the fault is removed.

# stdlib
import time

# pytest
import pytest

# Zato
from kube_checks import finish, get_pair, ModuleCtx as ChecksCtx, start_workload
from kube_faults import drain_node, heal_node, partition_node, pause_node, start_node, stop_node, uncordon_node, \
    unpause_node
from nodes import ModuleCtx as NodesCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The faults of the worker node of the active pod
    Fault_Drain = 'drain'
    Fault_Stop = 'stop'
    Fault_Pause = 'pause'
    Fault_Partition = 'partition'
    Faults = [Fault_Drain, Fault_Stop, Fault_Pause, Fault_Partition]

    # How long the standby may take to take over, in seconds
    Takeover_Timeout = 120

    # How long the traffic reaches the new active pod before the fault is removed, in seconds
    Traffic_Seconds = 15

    # The roles of a pod that serves requests
    Active_Roles:'strlist' = list(NodesCtx.Active_Roles)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault', ModuleCtx.Faults)
def test_node_fault(kube_pair:'KubeEnvironment', fault:'str') -> 'None':
    """ The worker node of the active pod fails under traffic, the standby takes over, and the former active pod
    joins again once the fault is removed.
    """
    env = kube_pair
    workload = start_workload(env)

    active, standby = get_pair(env)
    node_name = active.host_node

    if fault == ModuleCtx.Fault_Drain:
        started = drain_node(node_name)
    elif fault == ModuleCtx.Fault_Stop:
        started = stop_node(node_name)
    elif fault == ModuleCtx.Fault_Pause:
        started = pause_node(node_name)
    else:
        started = partition_node(node_name)

    _ = standby.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Takeover_Timeout)
    time.sleep(ModuleCtx.Traffic_Seconds)

    if fault == ModuleCtx.Fault_Drain:
        uncordon_node(node_name)
    elif fault == ModuleCtx.Fault_Stop:
        start_node(node_name)
    elif fault == ModuleCtx.Fault_Pause:
        unpause_node(node_name)
    else:
        heal_node(node_name)

    workload.fault_windows.append((started, time.time()))

    # The active pod that the fault ends leaves the claim it committed before the run began without a run.
    _ = finish(env, workload, started, ChecksCtx.Unrun_Claims_After_Fault)

# ################################################################################################################################
# ################################################################################################################################
