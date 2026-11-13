# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of the Kubernetes suites. A pod is deleted, its Zato server is killed or the pod is frozen through
# the cgroup of its node container. A worker node is drained, stopped, paused, or partitioned from the other worker
# nodes while it still reaches the control plane. Every fault can be removed, and the cluster can be restored
# to the state in which every node runs and reaches every other one.

# stdlib
import logging
import time

# Zato
from kube_cluster import get_node_ip, get_node_pod_cidr, get_pod_uid, kubectl, ModuleCtx as ClusterCtx, run
from topology import docker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite_kubernetes.faults')

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

    # How long a drain and the readiness of every node may take
    Drain_Timeout = '300s'
    Ready_Timeout = '300s'

    # The states of a node container
    State_Running = 'running'
    State_Paused = 'paused'

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

def _get_pod_cgroup_command(pod_name:'str', value:'str') -> 'str':
    """ Returns the shell command that writes a value to cgroup.freeze of a pod, under the systemd driver
    of the kubelet or under its cgroupfs driver.
    """
    uid = get_pod_uid(pod_name)
    slice_uid = uid.replace('-', '_')

    find = f'find /sys/fs/cgroup -type d \\( -name "*pod{slice_uid}.slice" -o -name "pod{uid}" \\) -print -quit'

    out = f'echo {value} > "$({find})/cgroup.freeze"'
    return out

# ################################################################################################################################

def freeze_pod(pod_name:'str', node_name:'str') -> 'float':
    """ Freezes every process of a pod through its cgroup in its node container.
    """
    out = time.time()
    _ = docker('exec', node_name, 'sh', '-c', _get_pod_cgroup_command(pod_name, '1'))

    logger.info('Froze pod %s', pod_name)

    return out

# ################################################################################################################################

def thaw_pod(pod_name:'str', node_name:'str') -> 'None':
    _ = docker('exec', node_name, 'sh', '-c', _get_pod_cgroup_command(pod_name, '0'))

    logger.info('Thawed pod %s', pod_name)

# ################################################################################################################################
# ################################################################################################################################

def drain_node(node_name:'str') -> 'float':
    """ Drains a worker node, which evicts its pods gracefully and keeps new ones off it.
    """
    out = time.time()
    _ = kubectl('drain', node_name, '--ignore-daemonsets', '--delete-emptydir-data', '--force',
        f'--timeout={ModuleCtx.Drain_Timeout}')

    logger.info('Drained %s', node_name)

    return out

# ################################################################################################################################

def uncordon_node(node_name:'str') -> 'None':
    _ = kubectl('uncordon', node_name)

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

def pause_node(node_name:'str') -> 'float':
    out = time.time()
    _ = docker('pause', node_name)

    logger.info('Paused %s', node_name)

    return out

# ################################################################################################################################

def unpause_node(node_name:'str') -> 'None':
    _ = docker('unpause', node_name)

    logger.info('Resumed %s', node_name)

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
    """ Starts, resumes, uncordons and heals every worker node, and waits until every node is ready.
    """
    for node_name in ClusterCtx.Zones:
        state = docker('inspect', '-f', '{{.State.Status}}', node_name).stdout.strip()

        if state == ModuleCtx.State_Paused:
            unpause_node(node_name)

        elif state != ModuleCtx.State_Running:
            start_node(node_name)

        heal_node(node_name)
        uncordon_node(node_name)

    _ = run(['kubectl', '--context', ClusterCtx.Context, 'wait', '--for=condition=Ready', 'node', '--all',
        f'--timeout={ModuleCtx.Ready_Timeout}'])

# ################################################################################################################################
# ################################################################################################################################
