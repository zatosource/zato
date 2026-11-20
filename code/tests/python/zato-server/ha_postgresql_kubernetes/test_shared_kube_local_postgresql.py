# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The pair on the local build of PostgreSQL, whose primary and synchronous standby run on the host. The pods reach
# the primary through a Service without a selector, under a name of the cluster.

# stdlib
import time

# Zato
from kube_checks import get_pair
from kube_cluster import get_node_ip, kubectl, ModuleCtx as ClusterCtx
from kube_env import ModuleCtx as EnvCtx
from kube_local_postgresql import KubeLocalPostgreSQL, ModuleCtx as LocalCtx
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeEnvironment
    from zato.common.typing_ import strset

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the server of the active pod may take to open its sessions with the primary, and how often they are read
    Sessions_Timeout = 60
    Poll_Interval = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _get_pod_ip(pod_name:'str') -> 'str':
    result = kubectl('get', 'pod', pod_name, '-n', ClusterCtx.Namespace, '-o', 'jsonpath={.status.podIP}')

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def _wait_for_sessions(backend:'KubeLocalPostgreSQL', addresses:'strset') -> 'strset':
    """ Waits until the primary has a session from one of the given addresses and returns the addresses of every session.
    """
    deadline = time.monotonic() + ModuleCtx.Sessions_Timeout

    while True:
        out = backend.read_client_addresses()

        if out & addresses:
            return out

        assert time.monotonic() < deadline, f'No session from {sorted(addresses)}, sessions from {sorted(out)}'
        time.sleep(ModuleCtx.Poll_Interval)

# ################################################################################################################################
# ################################################################################################################################

def test_pair_on_local_postgresql(local_pair:'KubeEnvironment') -> 'None':
    """ One pod is active and the other its standby, the primary waits for its synchronous standby at each commit,
    and the active pod has its sessions with the primary.
    """
    env = local_pair
    backend = cast_('KubeLocalPostgreSQL', env.session.backends[0])

    # One pod is active and the other one its standby ..
    active, standby = get_pair(env)

    report = standby.read_role()
    assert report is not None, f'No role from {standby.pod_name}'
    assert report['role'] == EnvCtx.Role_Standby, f'{standby.pod_name} -> {report}'

    # .. each commit on the primary waits for its standby ..
    sync_state = backend.read_sync_state()
    assert sync_state == LocalCtx.Sync_State, f'Standby of the local cluster -> `{sync_state}`'

    # .. and the active pod reaches the primary, from its own address or from that of its node, which the cluster
    # gives to the traffic of a pod that leaves the network of the cluster.
    node_ip = get_node_ip(active.host_node)
    pod_ip = _get_pod_ip(active.pod_name)

    _ = _wait_for_sessions(backend, {node_ip, pod_ip})

# ################################################################################################################################
# ################################################################################################################################
