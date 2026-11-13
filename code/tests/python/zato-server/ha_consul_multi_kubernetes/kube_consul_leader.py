# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of the Consul leader pod. The leader pod is frozen through its cgroup, or the worker node it runs on
# drops every packet it forwards between the leader pod and the other Consul pods, while the leader pod still reaches
# the Zato pods. The rules of the partition are in the chain of the faults of the Kubernetes suite, which the
# restoration of the cluster flushes.

# stdlib
import logging
import time

# Zato
from kube_cluster import kubectl, ModuleCtx as ClusterCtx
from kube_env import ModuleCtx as EnvCtx
from kube_faults import ModuleCtx as FaultsCtx
from topology import docker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kube_env import KubeConsul
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul_multi_kubernetes.leader')

# ################################################################################################################################
# ################################################################################################################################

def get_consul_pods() -> 'strlist':
    out:'strlist' = []

    for index in range(EnvCtx.Consul_Replicas):
        out.append(f'{EnvCtx.Consul_StatefulSet}-{index}')

    return out

# ################################################################################################################################

def get_pod_ip(pod_name:'str') -> 'str':
    result = kubectl('get', 'pod', pod_name, '-n', ClusterCtx.Namespace, '-o', 'jsonpath={.status.podIP}')

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def get_leader_pod(consul:'KubeConsul') -> 'str':
    """ Returns the Consul pod that the cluster reports as its leader.
    """
    leader = consul.request('GET', '/v1/status/leader')
    assert leader, 'The Consul cluster has no leader'

    ip, _ = leader.rsplit(':', 1)

    for pod_name in get_consul_pods():
        if get_pod_ip(pod_name) == ip:
            return pod_name

    raise Exception(f'No Consul pod at {leader}')

# ################################################################################################################################

def partition_pod(pod_name:'str', node_name:'str') -> 'float':
    """ Drops every packet that the worker node of a Consul pod forwards between that pod and the other Consul pods,
    in both directions, and returns the time the partition began.
    """
    chain = FaultsCtx.Chain
    pod_ip = get_pod_ip(pod_name)

    commands:'strlist' = [
        f'iptables -N {chain} 2>/dev/null || true',
        f'iptables -C FORWARD -j {chain} 2>/dev/null || iptables -I FORWARD 1 -j {chain}',
    ]

    for other in get_consul_pods():
        if other == pod_name:
            continue

        other_ip = get_pod_ip(other)

        commands.append(f'iptables -A {chain} -s {pod_ip} -d {other_ip} -j DROP')
        commands.append(f'iptables -A {chain} -s {other_ip} -d {pod_ip} -j DROP')

    out = time.time()
    _ = docker('exec', node_name, 'sh', '-c', ' && '.join(commands))

    logger.info('Partitioned Consul pod %s from the other Consul pods', pod_name)

    return out

# ################################################################################################################################
# ################################################################################################################################
