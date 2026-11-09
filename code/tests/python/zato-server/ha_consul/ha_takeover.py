# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The takeover of a failed active node by its standby under traffic, shared by the takeover suite and the long runs.

# stdlib
import logging
import time

# Zato
from ha_faults import apply_fault, get_isolation_addresses, ModuleCtx as FaultsCtx, remove_fault
from nodes import ModuleCtx as NodesCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from nodes import Node
    from workload import Workload
    from zato.common.typing_ import strlist

    Workload = Workload

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.ha_takeover')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before the fault and after the takeover, in seconds
    Traffic_Seconds = 15

    # How long the standby may take to become active after the fault, in seconds
    Takeover_Timeout = 60

    # How long the server of the new active node may take to start, in seconds
    Server_Timeout = 120

    # How long the former active node may take to join again as the standby in sync, in seconds
    Rejoin_Timeout = 300

    # The roles of a node that serves requests and of a standby in sync
    Active_Roles:'strlist' = list(NodesCtx.Active_Roles)
    Standby_In_Sync = ['StandbyInSync']

    # What the log of a node that resumed after a takeover contains
    Fencing_Text = 'fencing'

    # The faults after which the former active node resumes with its process intact, and is fenced as it does
    Resuming_Faults = (FaultsCtx.Fault_Pause, FaultsCtx.Fault_Partition)

    # The faults of the takeover
    Faults = [FaultsCtx.Fault_Stop, FaultsCtx.Fault_Kill, FaultsCtx.Fault_Pause, FaultsCtx.Fault_Partition]

# ################################################################################################################################
# ################################################################################################################################

def take_over(env:'HAEnvironment', fault:'str', workload:'Workload') -> 'tuple[Node, Node, float]':
    """ Applies a fault to the active node under traffic, waits for its standby to take over and for the former
    active node to join again, and returns the new active node, the former one and the time of the takeover.
    """
    old_active = env.get_active()
    assert old_active is not None, 'No active node'

    new_active = env.get_other(old_active)

    record = env.consul.read_record()
    assert record is not None
    generation_before = record['generation']

    # The traffic reaches the active node ..
    time.sleep(ModuleCtx.Traffic_Seconds)

    # .. which fails, and its standby takes over ..
    addresses = get_isolation_addresses(new_active)
    fault_started = apply_fault(old_active, fault, addresses)

    _ = new_active.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Takeover_Timeout)
    takeover_time = time.time()

    record = env.consul.read_record()
    assert record is not None
    assert record['active_node'] == new_active.node_name, record
    assert record['generation'] > generation_before, record

    _ = new_active.wait_until_server_up(ModuleCtx.Server_Timeout)
    env.point_database_at(new_active)

    # .. the traffic reaches the new active node ..
    time.sleep(ModuleCtx.Traffic_Seconds)

    # .. the former active node resumes and is fenced, if its process remained ..
    remove_fault(old_active, fault)
    workload.fault_windows.append((fault_started, time.time()))

    # .. and it joins again as the standby.
    _ = old_active.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Rejoin_Timeout)

    if fault in ModuleCtx.Resuming_Faults:
        logs = old_active.read_logs()
        assert ModuleCtx.Fencing_Text in logs, f'{old_active.node_name} was not fenced'

    out = (new_active, old_active, takeover_time)
    return out

# ################################################################################################################################
# ################################################################################################################################
