# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of the Kubernetes suites. A pod is deleted, its Zato server is killed or frozen, or the configuration
# of its server is made unreadable. A worker node is stopped, partitioned from the other worker nodes while it still
# reaches the control plane, or isolated from every other node. Every fault can be removed, and the cluster can be
# restored to the state in which every node runs and reaches every other one.

# stdlib
import logging
import time

# Zato
from kube_cluster import cluster, get_node_ip, get_node_pod_cidr, kubectl, ModuleCtx as ClusterCtx
from topology import docker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intset, strlist

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

    # The pattern of the process of the Zato server that pgrep receives from a shell
    Server_Process_Pattern = 'zato[.]server[.]main'

    # The name of the worker process of the Zato server
    Worker_Process = 'zato-worker'

    # The scopes of a freeze - the process group of the command of the server that the node started, which holds
    # the arbiter, the worker and the scheduler, or the worker alone
    Scope_Group = 'group'
    Scope_Worker = 'worker'

    # The configuration file of the Zato server, under the directory of the server in a pod
    Server_Conf = '"$Zato_Test_Server_Directory/config/repo/server.conf"'

    # The mode that makes a file unreadable to its owner
    Unreadable_Mode = '000'

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

def _exec_shell(pod_name:'str', command:'str', check:'bool'=True) -> 'str':
    """ Runs a shell command in the Zato container of a pod and returns its output.
    """
    result = kubectl('exec', pod_name, '-n', ClusterCtx.Namespace, '-c', ModuleCtx.Zato_Container, '--',
        'sh', '-c', command, check=check)

    out = result.stdout.strip()
    return out

# ################################################################################################################################

def freeze_server(pod_name:'str', scope:'str') -> 'float':
    """ Stops the Zato server of a pod with SIGSTOP and returns the time of the freeze. The group scope stops the process
    group of the command that the node started, which the worker belongs to, and the worker scope stops the worker alone.
    """
    worker = ModuleCtx.Worker_Process

    if scope == ModuleCtx.Scope_Group:
        command = f'pid=$(pgrep -x {worker} | head -n 1) && pgid=$(cut -d " " -f 5 /proc/$pid/stat) && kill -STOP -$pgid'
    else:
        command = f'pkill -STOP -x {worker}'

    out = time.time()
    _ = _exec_shell(pod_name, command)

    logger.info('Froze the server in pod %s, scope %s', pod_name, scope)

    return out

# ################################################################################################################################

def thaw_server(pod_name:'str') -> 'None':
    """ Resumes every stopped process of the Zato container of a pod with SIGCONT, which a running process ignores.
    """
    _ = _exec_shell(pod_name, 'kill -CONT -1')

    logger.info('Thawed the server in pod %s', pod_name)

# ################################################################################################################################

def get_server_pids(pod_name:'str') -> 'intset':
    """ Returns the PIDs of the processes of the Zato server that run in a pod, the warm server of a standby included.
    """
    # pgrep exits with a non-zero code and prints nothing when it finds no process. The pattern does not match itself,
    # so the shell that runs pgrep, whose command line holds the pattern, is not listed.
    output = _exec_shell(pod_name, f'pgrep -f {ModuleCtx.Server_Process_Pattern}', check=False)

    out = {int(line) for line in output.split()}
    return out

# ################################################################################################################################

def break_server_config(pod_name:'str') -> 'str':
    """ Makes the configuration of the Zato server of a pod unreadable, so that each start of the server exits at once,
    and returns the mode that the file had.
    """
    path = ModuleCtx.Server_Conf
    out = _exec_shell(pod_name, f'stat -c %a {path} && chmod {ModuleCtx.Unreadable_Mode} {path}')

    logger.info('Made the server configuration of pod %s unreadable, mode was %s', pod_name, out)

    return out

# ################################################################################################################################

def restore_server_config(pod_name:'str', mode:'str') -> 'None':
    """ Gives the configuration of the Zato server of a pod its mode again.
    """
    _ = _exec_shell(pod_name, f'chmod {mode} {ModuleCtx.Server_Conf}')

    logger.info('Restored the server configuration of pod %s to mode %s', pod_name, mode)

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

def _get_chain_commands() -> 'strlist':
    """ Returns the commands that create the chain of the faults in a node container and make its parent chains
    jump to it first.
    """
    out:'strlist' = [f'iptables -N {ModuleCtx.Chain} 2>/dev/null || true']

    for parent in ModuleCtx.Parent_Chains:
        out.append(f'iptables -C {parent} -j {ModuleCtx.Chain} 2>/dev/null || iptables -I {parent} 1 -j {ModuleCtx.Chain}')

    return out

# ################################################################################################################################

def isolate_node(node_name:'str') -> 'float':
    """ Drops every packet to and from a worker node and its pods, the control plane included, as of a node
    that stopped responding, and returns the time of the isolation. The loopback interface of the node remains,
    so the processes of the node still reach one another.
    """
    commands = _get_chain_commands()

    commands.append(f'iptables -A {ModuleCtx.Chain} -i lo -j RETURN')
    commands.append(f'iptables -A {ModuleCtx.Chain} -o lo -j RETURN')
    commands.append(f'iptables -A {ModuleCtx.Chain} -j DROP')

    out = time.time()
    _ = docker('exec', node_name, 'sh', '-c', ' && '.join(commands))

    logger.info('Isolated %s', node_name)

    return out

# ################################################################################################################################

def partition_node(node_name:'str') -> 'float':
    """ Drops every packet between a worker node, with its pods, and the other worker nodes with their pods.
    The control plane remains reachable, so the pods of the node still reach the API server.
    """
    commands = _get_chain_commands()

    for other in cluster.zones:
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
    """ Removes the partition or the isolation of a worker node, leaving the rules of Kubernetes as they are.
    """
    _ = docker('exec', node_name, 'sh', '-c', f'iptables -F {ModuleCtx.Chain} 2>/dev/null || true')

    logger.info('Healed %s', node_name)

# ################################################################################################################################
# ################################################################################################################################

def restore_cluster() -> 'None':
    """ Starts and heals every worker node, and waits until every node is ready.
    """
    for node_name in cluster.zones:
        state = docker('inspect', '-f', '{{.State.Status}}', node_name).stdout.strip()

        if state != ModuleCtx.State_Running:
            start_node(node_name)

        heal_node(node_name)

    _ = kubectl('wait', '--for=condition=Ready', 'node', '--all', f'--timeout={ModuleCtx.Ready_Timeout}')

# ################################################################################################################################
# ################################################################################################################################
