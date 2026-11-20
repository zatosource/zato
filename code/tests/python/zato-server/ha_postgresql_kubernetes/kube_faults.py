# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of the Kubernetes suites. A pod is deleted or its Zato server is killed. A worker node is stopped,
# or partitioned from the other worker nodes while it still reaches the control plane. Every fault can be removed,
# and the cluster can be restored to the state in which every node runs and reaches every other one.

# stdlib
import logging
import time

# Zato
from kube_cluster import get_node_ip, get_node_pod_cidr, kubectl, ModuleCtx as ClusterCtx, run
from topology import docker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql_kubernetes.faults')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The chain of iptables in a node container that holds the rules of a partition
    Chain = 'ZATO-HA-TEST'

    # The chains that jump to it
    Parent_Chains = ['INPUT', 'OUTPUT', 'FORWARD']

    # The process of the Zato server in a pod
    Server_Process = 'zato.server.main'

    # The container of the Zato pods
    Zato_Container = 'zato'

    # How long the readiness of every node may take
    Ready_Timeout = '300s'

    # The state of a running node container
    State_Running = 'running'

# ################################################################################################################################
# ################################################################################################################################

def delete_pod(pod_name:'str') -> 'float':
    """ Deletes a pod gracefully, which its StatefulSet creates again, and returns the time it was deleted.
    """
    out = time.time()
    _ = kubectl('delete', 'pod', pod_name, '-n', ClusterCtx.Namespace, '--wait=false')

    logger.info('Deleted pod %s', pod_name)

    return out

# ################################################################################################################################

def kill_server(pod_name:'str') -> 'float':
    """ Kills the Zato server inside a pod, which the node in the pod starts again.
    """
    out = time.time()
    _ = kubectl('exec', pod_name, '-n', ClusterCtx.Namespace, '-c', ModuleCtx.Zato_Container, '--',
        'pkill', '-KILL', '-f', ModuleCtx.Server_Process)

    logger.info('Killed the server in pod %s', pod_name)

    return out

# ################################################################################################################################

def stop_node(node_name:'str') -> 'float':
    """ Stops the container of a worker node, which takes its zone away.
    """
    out = time.time()
    _ = docker('stop', node_name)

    logger.info('Stopped %s', node_name)

    return out

# ################################################################################################################################

def start_node(node_name:'str') -> 'None':
    _ = docker('start', node_name)

    logger.info('Started %s', node_name)

# ################################################################################################################################

def partition_node(node_name:'str') -> 'float':
    """ Drops every packet between a worker node, with its pods, and the other worker nodes with their pods.
    The control plane remains reachable, so the pods of the node still reach the API server.
    """
    commands:'strlist' = [f'iptables -N {ModuleCtx.Chain} 2>/dev/null || true']

    for parent in ModuleCtx.Parent_Chains:
        commands.append(f'iptables -C {parent} -j {ModuleCtx.Chain} 2>/dev/null || iptables -I {parent} 1 -j {ModuleCtx.Chain}')

    for other in ClusterCtx.Zones:
        if other == node_name:
            continue

        for address in (get_node_ip(other), get_node_pod_cidr(other)):
            commands.append(f'iptables -A {ModuleCtx.Chain} -s {address} -j DROP')
            commands.append(f'iptables -A {ModuleCtx.Chain} -d {address} -j DROP')

    out = time.time()
    _ = docker('exec', node_name, 'sh', '-c', ' && '.join(commands))

    logger.info('Partitioned %s', node_name)

    return out

# ################################################################################################################################

def heal_node(node_name:'str') -> 'None':
    """ Removes the partition of a worker node, leaving the rules of Kubernetes as they are.
    """
    _ = docker('exec', node_name, 'sh', '-c', f'iptables -F {ModuleCtx.Chain} 2>/dev/null || true')

    logger.info('Healed %s', node_name)

# ################################################################################################################################
# ################################################################################################################################

def restore_cluster() -> 'None':
    """ Starts and heals every worker node, and waits until every node is ready.
    """
    for node_name in ClusterCtx.Zones:
        state = docker('inspect', '-f', '{{.State.Status}}', node_name).stdout.strip()

        if state != ModuleCtx.State_Running:
            start_node(node_name)

        heal_node(node_name)

    _ = run(['kubectl', '--context', ClusterCtx.Context, 'wait', '--for=condition=Ready', 'node', '--all',
        f'--timeout={ModuleCtx.Ready_Timeout}'])

# ################################################################################################################################
# ################################################################################################################################
