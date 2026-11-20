# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Zato server of the active pod is killed under traffic. The deletion and the freeze of the pod end the lease
# renewal as the faults of the node do, which the suite of the worker nodes covers.

# stdlib
import time

# Zato
from kube_checks import finish, get_pair, ModuleCtx as ChecksCtx, start_workload
from kube_faults import kill_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a server may take to start again, in seconds
    Server_Timeout = 180

# ################################################################################################################################
# ################################################################################################################################

def test_kill_server(kube_pair:'KubeEnvironment') -> 'None':
    """ The server of the active pod is killed under traffic, and the pod keeps its role and starts its server again.
    """
    env = kube_pair
    workload = start_workload(env)

    active, _ = get_pair(env)

    started = kill_server(active.pod_name)
    _ = active.wait_until_server_up(ModuleCtx.Server_Timeout)

    workload.fault_windows.append((started, time.time()))

    # The server that the fault ends leaves the claim it committed before the run began without a run.
    _ = finish(env, workload, started, ChecksCtx.Unrun_Claims_After_Fault)

# ################################################################################################################################
# ################################################################################################################################
