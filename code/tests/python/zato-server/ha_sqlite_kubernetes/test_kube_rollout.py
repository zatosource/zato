# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Changes of the cluster around a running pair. A rolling update replaces both pods one after the other under traffic,
# without waiting on the role of either pod, and the worker node of the standby stops and starts again, after which
# its pod joins again while the Service lists only the active pod.

# stdlib
import json
import time

# Zato
from kube_checks import finish, get_pair, ModuleCtx as ChecksCtx, start_workload
from kube_cluster import kubectl, ModuleCtx as ClusterCtx, wait_for_rollout
from kube_env import ModuleCtx as EnvCtx
from kube_faults import start_node, stop_node

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The annotation of the pod template that a rolling update changes
    Restart_Annotation = 'zato.io/restarted-at'

    # How long the active pod runs alone while the node of the standby is stopped, in seconds
    Zone_Away_Seconds = 60

    # How long the active pod may take to continue alone, in seconds
    Mark_Out_Timeout = 60

    # The role of an active pod without a standby
    Active_Solo = ['ActiveSolo']

# ################################################################################################################################
# ################################################################################################################################

def test_rolling_update(kube_pair:'KubeEnvironment') -> 'None':
    """ An annotation of the pod template changes under traffic, both pods are replaced one after the other,
    and the update completes while nothing acknowledged is lost.
    """
    env = kube_pair
    workload = start_workload(env)

    patch = {
        'spec': {
            'template': {
                'metadata': {
                    'annotations': {
                        ModuleCtx.Restart_Annotation: str(time.time()),
                    },
                },
            },
        },
    }

    started = time.time()
    _ = kubectl('patch', 'statefulset', EnvCtx.StatefulSet_Name, '-n', ClusterCtx.Namespace, '-p', json.dumps(patch))

    wait_for_rollout('statefulset', EnvCtx.StatefulSet_Name)
    workload.fault_windows.append((started, time.time()))

    # The replaced active pod leaves the claim it committed before the run began without a run.
    _ = finish(env, workload, started, ChecksCtx.Unrun_Claims_After_Fault)

# ################################################################################################################################

def test_zone_return(kube_pair:'KubeEnvironment') -> 'None':
    """ The worker node of the standby stops, the active pod continues alone, and once the node starts again,
    its pod joins again through a rejoin while the Service lists only the active pod.
    """
    env = kube_pair
    workload = start_workload(env)

    active, standby = get_pair(env)

    started = stop_node(standby.host_node)
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    time.sleep(ModuleCtx.Zone_Away_Seconds)

    start_node(standby.host_node)
    workload.fault_windows.append((started, time.time()))

    returned = finish(env, workload, started)
    assert returned is active, f'{returned.pod_name} became active instead of {active.pod_name}'

# ################################################################################################################################
# ################################################################################################################################
