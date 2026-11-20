# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A rolling update replaces both pods of a running pair one after the other under traffic, without waiting
# on the role of either pod.

# stdlib
import json
import time

# Zato
from kube_checks import finish, ModuleCtx as ChecksCtx, start_workload
from kube_cluster import kubectl, ModuleCtx as ClusterCtx, wait_for_rollout
from kube_env import ModuleCtx as EnvCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The annotation of the pod template that a rolling update changes
    Restart_Annotation = 'zato.io/restarted-at'

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
# ################################################################################################################################
