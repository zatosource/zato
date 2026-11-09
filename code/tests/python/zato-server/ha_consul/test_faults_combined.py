# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Combined faults - a slow standby disk with loss on the replication link during a retention sweep, CPU starvation
# of the standby during a takeover, and memory pressure on the active node during a rejoin.

# stdlib
import logging
import time

# Zato
from ha_checks import check_copies, check_scheduler, check_workload
from ha_env import ready_pair
from ha_tools import clear_cpu_limit, clear_memory_limit, degrade_link, limit_cpu, limit_memory, ModuleCtx as ToolsCtx, \
    PreloadHook, read_memory_current, restore_link
from nodes import ModuleCtx as NodesCtx, Timers
from workload import Topic_Name, Workload
from zato.common.test.client import PublishClient
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from zato.common.typing_ import any_, strlist

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.faults_combined')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the traffic runs before the faults, in seconds
    Traffic_Seconds = 10

    # The delay of each sync and write of the standby, in microseconds, and the loss on the replication link
    Standby_Delay_US = 20000
    Link_Loss = 'loss 10%'

    # How many messages expire before the sweep, and how long they live, in seconds
    Expiring_Count = 2000
    Expiration_Seconds = 1

    # The share of one CPU that the standby keeps during the takeover
    Starved_CPU_Share = 0.05

    # The share of its current memory that the active node may keep before the kernel reclaims and throttles it
    Memory_Share = 0.5
    Memory_High = 'memory.high'

    # How long the standby may take to take over or to join again, and the pair to recover, in seconds
    Takeover_Timeout = 180
    Mark_Out_Timeout = 60
    Recovery_Timeout = 300

    # How long a server may take to start, in seconds
    Server_Timeout = 120

    # The roles of the pair
    Active_Roles:'strlist' = list(NodesCtx.Active_Roles)
    Active_Solo = ['ActiveSolo']
    Standby_In_Sync = ['StandbyInSync']

# ################################################################################################################################
# ################################################################################################################################

def _finish(env:'HAEnvironment', workload:'Workload') -> 'None':
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

    check_workload(env, workload)

    _ = check_scheduler(env, active)
    check_copies(env, active)

# ################################################################################################################################

def _start_workload(env:'HAEnvironment') -> 'Workload':
    out = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    out.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_slow_standby_and_lossy_link_during_sweep(ha_session:'HASession', request:'any_') -> 'None':
    """ With the disk of the standby slow and 10 percent of the packets of the replication link lost, a retention sweep
    deletes the expired messages through the barrier, and the copies remain equal.
    """
    preload = PreloadHook()

    with ready_pair(ha_session, request.node.name, Timers(), [preload]) as env:
        workload = _start_workload(env)

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        # Messages that expire at once give the sweep rows to delete ..
        client = PublishClient(env.haproxy.base_url, env.publisher_username, env.publisher_password)

        for index in range(ModuleCtx.Expiring_Count):
            _ = client.publish(Topic_Name, {'expiring_index': index}, expiration=ModuleCtx.Expiration_Seconds)

        time.sleep(ModuleCtx.Expiration_Seconds * 2)

        # .. and the sweep runs while the standby is slow and the link loses packets.
        preload.set_disk_fault(standby, ModuleCtx.Standby_Delay_US, 0, ToolsCtx.Errno_EIO)
        degrade_link(active, [standby.ip], ModuleCtx.Link_Loss)
        degrade_link(standby, [active.ip], ModuleCtx.Link_Loss)

        started = time.time()
        result = active.run_retention_sweep()

        restore_link(active)
        restore_link(standby)
        preload.clear_disk_fault(standby)

        workload.fault_windows.append((started, time.time()))

        assert result.returncode == 0, f'Sweep failed:\n{result.stdout}{result.stderr}'

        _finish(env, workload)

# ################################################################################################################################

def test_starved_standby_during_takeover(ha_pair:'HAEnvironment') -> 'None':
    """ The standby runs on a twentieth of one CPU when the active node fails, and it still takes over.
    """
    env = ha_pair
    workload = _start_workload(env)

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    limit_cpu(standby, ModuleCtx.Starved_CPU_Share)

    started = time.time()
    active.kill()

    _ = standby.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Takeover_Timeout)

    clear_cpu_limit(standby)
    _ = standby.wait_until_server_up(ModuleCtx.Server_Timeout)

    active.resume()
    workload.fault_windows.append((started, time.time()))

    _finish(env, workload)

# ################################################################################################################################

def test_memory_pressure_during_rejoin(ha_pair:'HAEnvironment') -> 'None':
    """ The active node is under memory pressure while it sends its backup and frames to the rejoining standby.
    """
    env = ha_pair
    workload = _start_workload(env)

    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    standby.kill()
    _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

    current = read_memory_current(active)
    limit_memory(active, ModuleCtx.Memory_High, int(current * ModuleCtx.Memory_Share))

    started = time.time()
    standby.resume()

    _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Recovery_Timeout)

    clear_memory_limit(active, ModuleCtx.Memory_High)
    workload.fault_windows.append((started, time.time()))

    _finish(env, workload)

# ################################################################################################################################
# ################################################################################################################################
