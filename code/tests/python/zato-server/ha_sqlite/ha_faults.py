# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of the active-standby suites that act on one container - a process fault applied through Docker
# and a partition from named addresses applied with iptables in the network namespace of the container,
# each recorded with the time it began and the time it was removed.

# stdlib
import logging
import time

# Zato
from topology import run_in_network_namespace

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from nodes import Node
    from zato.common.typing_ import strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.faults')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The process faults that a test may apply to a node
    Fault_Stop      = 'stop'
    Fault_Kill      = 'kill'
    Fault_Pause     = 'pause'
    Fault_Partition = 'partition'

    # The faults that end a node and the one that freezes it, which a test resumes
    Process_Faults = [Fault_Stop, Fault_Kill, Fault_Pause]

# ################################################################################################################################
# ################################################################################################################################

def partition(node:'Node', addresses:'strlist') -> 'None':
    """ Drops every packet between a node and each of the given addresses, in both directions.
    """
    commands:'strlist' = []

    for address in addresses:
        commands.append(f'iptables -I INPUT -s {address} -j DROP')
        commands.append(f'iptables -I OUTPUT -d {address} -j DROP')

    script = ' && '.join(commands)
    _ = run_in_network_namespace(node.container_name, script)

    logger.info('Partitioned %s from %s', node.node_name, addresses)

# ################################################################################################################################

def heal(node:'Node') -> 'None':
    """ Removes every partition of a node.
    """
    _ = run_in_network_namespace(node.container_name, 'iptables -F INPUT && iptables -F OUTPUT')

    logger.info('Healed %s', node.node_name)

# ################################################################################################################################

def get_isolation_addresses(peer:'Node', referee_ip:'str') -> 'strlist':
    """ Returns the addresses that cut a node off from its peer and from the referee together.
    """
    out = [peer.ip, referee_ip]
    return out

# ################################################################################################################################

def apply_fault(node:'Node', fault:'str', partition_addresses:'strlist') -> 'float':
    """ Applies a fault to a node and returns the time it began, in seconds since the epoch. A partition
    cuts the node off from the given addresses.
    """
    out = time.time()

    if fault == ModuleCtx.Fault_Stop:
        node.stop()

    elif fault == ModuleCtx.Fault_Kill:
        node.kill()

    elif fault == ModuleCtx.Fault_Pause:
        node.pause()

    elif fault == ModuleCtx.Fault_Partition:
        partition(node, partition_addresses)

    else:
        raise Exception(f'Unknown fault `{fault}`')

    logger.info('Applied %s to %s', fault, node.node_name)

    return out

# ################################################################################################################################

def remove_fault(node:'Node', fault:'str') -> 'None':
    """ Ends a fault, after which a stopped or killed node starts again with its data.
    """
    if fault == ModuleCtx.Fault_Pause:
        node.unpause()

    elif fault == ModuleCtx.Fault_Partition:
        heal(node)

    else:
        node.resume()

    logger.info('Removed %s from %s', fault, node.node_name)

# ################################################################################################################################
# ################################################################################################################################
