# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of the Consul cluster - its leader killed, paused or partitioned from the other servers while it still
# reaches the nodes, one follower lost and the quorum lost with two followers. Each fault returns the servers
# it applied to, which its removal starts, resumes or heals again.

# stdlib
import logging
import time

# Zato
from topology import docker, run_in_network_namespace

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from consul_multi_cluster import ConsulCluster, ConsulServer
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul_multi.faults')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The faults of the cluster
    Fault_Leader_Kill      = 'leader-kill'
    Fault_Leader_Pause     = 'leader-pause'
    Fault_Leader_Partition = 'leader-partition'
    Fault_Server_Lost      = 'server-lost'
    Fault_Quorum_Lost      = 'quorum-lost'

    Faults = [Fault_Leader_Kill, Fault_Leader_Pause, Fault_Leader_Partition, Fault_Server_Lost, Fault_Quorum_Lost]

    # How many followers each fault that loses followers kills
    Lost_Followers = {
        Fault_Server_Lost: 1,
        Fault_Quorum_Lost: 2,
    }

# ################################################################################################################################
# ################################################################################################################################

def _get_followers(cluster:'ConsulCluster', leader:'ConsulServer') -> 'list[ConsulServer]':
    out:'list[ConsulServer]' = []

    for server in cluster.servers:
        if server.name != leader.name:
            out.append(server)

    return out

# ################################################################################################################################

def _partition_from(server:'ConsulServer', others:'list[ConsulServer]') -> 'None':
    """ Drops every packet between a server and the other servers, in both directions, while the nodes still reach it.
    """
    commands:'strlist' = []

    for other in others:
        commands.append(f'iptables -I INPUT -s {other.ip} -j DROP')
        commands.append(f'iptables -I OUTPUT -d {other.ip} -j DROP')

    _ = run_in_network_namespace(server.container_name, ' && '.join(commands))

# ################################################################################################################################

def apply_cluster_fault(cluster:'ConsulCluster', fault:'str') -> 'tuple[list[ConsulServer], float]':
    """ Applies a fault to the cluster and returns the servers it applied to and the time it began,
    in seconds since the epoch.
    """
    leader = cluster.get_leader()
    followers = _get_followers(cluster, leader)

    if fault in ModuleCtx.Lost_Followers:
        servers = followers[:ModuleCtx.Lost_Followers[fault]]
    else:
        servers = [leader]

    started = time.time()

    for server in servers:

        if fault == ModuleCtx.Fault_Leader_Pause:
            _ = docker('pause', server.container_name)
            cluster.unavailable.add(server.name)

        elif fault == ModuleCtx.Fault_Leader_Partition:
            _partition_from(server, followers)

        else:
            _ = docker('kill', server.container_name)
            cluster.unavailable.add(server.name)

    names:'strlist' = []

    for server in servers:
        names.append(server.name)

    logger.info('Applied %s to Consul servers %s', fault, names)

    out = (servers, started)
    return out

# ################################################################################################################################

def remove_cluster_fault(cluster:'ConsulCluster', fault:'str', servers:'list[ConsulServer]') -> 'None':
    """ Ends a fault of the cluster, after which the servers rejoin it with their data and it elects a leader.
    """
    for server in servers:

        if fault == ModuleCtx.Fault_Leader_Pause:
            _ = docker('unpause', server.container_name)

        elif fault == ModuleCtx.Fault_Leader_Partition:
            _ = run_in_network_namespace(server.container_name, 'iptables -F INPUT && iptables -F OUTPUT')

        else:
            _ = docker('start', server.container_name)

        cluster.unavailable.discard(server.name)

    cluster.wait_until_ready()

    logger.info('Removed %s from the Consul cluster', fault)

# ################################################################################################################################
# ################################################################################################################################
