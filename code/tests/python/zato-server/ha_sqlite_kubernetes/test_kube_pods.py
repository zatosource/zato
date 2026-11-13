# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Faults of the active pod under traffic - the pod is deleted, its Zato server is killed, and the pod is frozen
# through the cgroup of its node container.

# stdlib
import time

# pytest
import pytest

# Zato
from kube_checks import finish, get_pair, start_workload
from kube_faults import delete_pod, freeze_pod, kill_server, thaw_pod
from nodes import ModuleCtx as NodesCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The faults of the active pod
    Fault_Delete = 'delete-pod'
    Fault_Kill_Server = 'kill-server'
    Fault_Freeze = 'freeze'
    Faults = [Fault_Delete, Fault_Kill_Server, Fault_Freeze]

    # How long the standby may take to take over, and a server to start again, in seconds
    Takeover_Timeout = 120
    Server_Timeout = 180

    # The roles of a pod that serves requests
    Active_Roles:'strlist' = list(NodesCtx.Active_Roles)

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('fault', ModuleCtx.Faults)
def test_pod_fault(kube_pair:'KubeEnvironment', fault:'str') -> 'None':
    """ The active pod fails under traffic. A deleted or frozen pod is replaced by its standby and joins again,
    and a pod whose server was killed keeps its role and starts its server again.
    """
    env = kube_pair
    workload = start_workload(env)

    active, standby = get_pair(env)

    if fault == ModuleCtx.Fault_Delete:
        started = delete_pod(active.pod_name)
        _ = standby.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Takeover_Timeout)

    elif fault == ModuleCtx.Fault_Kill_Server:
        started = kill_server(active.pod_name)
        _ = active.wait_until_server_up(ModuleCtx.Server_Timeout)

    else:
        started = freeze_pod(active.pod_name, active.host_node)
        _ = standby.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Takeover_Timeout)
        thaw_pod(active.pod_name, active.host_node)

    workload.fault_windows.append((started, time.time()))

    _ = finish(env, workload, started)

# ################################################################################################################################
# ################################################################################################################################
