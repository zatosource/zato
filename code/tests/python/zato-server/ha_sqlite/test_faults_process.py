# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# CPU, memory and clock faults on each node - a CPU limit and memory pressure at each severity, an OOM kill
# of the Zato server inside the active container, and offsets and rate changes of the wall clock of the standby
# during a takeover, which the timers of the node do not follow, as they use the monotonic clock.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload, watch_roles
from ha_env import ready_pair
from ha_tools import clear_cpu_limit, clear_memory_limit, limit_cpu, limit_memory, ModuleCtx as ToolsCtx, PreloadHook, \
    protect_node_from_oom_killer, read_memory_anon, read_memory_current, read_oom_kills
from nodes import ModuleCtx as NodesCtx, Timers
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from nodes import Node
    from zato.common.typing_ import any_, strlist

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.faults_process')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The node that the fault applies to
    Target_Active = 'active'
    Target_Standby = 'standby'
    Targets = [Target_Active, Target_Standby]

    # How long the traffic runs before the faults and under each severity, in seconds
    Traffic_Seconds = 10
    Window_Seconds = 30

    # The memory limits of the cgroup
    Memory_High = 'memory.high'
    Memory_Max = 'memory.max'
    Swap_Max = 'memory.swap.max'

    # The swap that the active container may use while the OOM killer is expected to act
    No_Swap = 0

    # The share of the memory of its processes that the active container may keep before the OOM killer acts
    OOM_Share = 0.5

    # How long the OOM killer may take to end a process, in seconds
    OOM_Timeout = 60

    # How often the OOM kills are read while the test waits for one, in seconds
    Poll_Interval = 0.5

    # The offsets of the wall clock, in seconds, and its rates
    Clock_Settings = [
        (120, 1.0),
        (-120, 1.0),
        (0, 2.0),
        (0, 0.5),
    ]

    # How long the standby may take to take over, the same as with a clock that is not changed, in seconds
    Takeover_Timeout = 60

    # How long the pair may take to recover, in seconds
    Recovery_Timeout = 300

    # How long a server may take to start, in seconds
    Server_Timeout = 120

    # The roles of a node that serves requests
    Active_Roles:'strlist' = list(NodesCtx.Active_Roles)

# ################################################################################################################################
# ################################################################################################################################

def _get_target(env:'HAEnvironment', target:'str') -> 'Node':
    active = env.get_active()
    assert active is not None, 'No active node'

    if target == ModuleCtx.Target_Active:
        out = active
    else:
        out = env.get_other(active)

    return out

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

@pytest.mark.parametrize('target', ModuleCtx.Targets)
def test_cpu_limit(ha_pair:'HAEnvironment', target:'str') -> 'None':
    """ One node runs on a share of one CPU at each severity, no two nodes are active at once, and nothing is lost.
    """
    env = ha_pair
    workload = _start_workload(env)

    for severity in ToolsCtx.Severities:
        node = _get_target(env, target)
        limit_cpu(node, 1 - severity)

        started = time.time()
        both_active = watch_roles(env, ModuleCtx.Window_Seconds)

        clear_cpu_limit(node)
        workload.fault_windows.append((started, time.time()))

        assert not both_active, f'Two active nodes -> {both_active}'
        _ = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

    _finish(env, workload)

# ################################################################################################################################

@pytest.mark.parametrize('target', ModuleCtx.Targets)
def test_memory_pressure(ha_pair:'HAEnvironment', target:'str') -> 'None':
    """ The memory.high of one node is set below its current memory at each severity, which makes the kernel
    reclaim and throttle it, no two nodes are active at once, and nothing is lost.
    """
    env = ha_pair
    workload = _start_workload(env)

    for severity in ToolsCtx.Severities:
        node = _get_target(env, target)

        current = read_memory_current(node)
        limit_memory(node, ModuleCtx.Memory_High, int(current * (1 - severity)))

        started = time.time()
        both_active = watch_roles(env, ModuleCtx.Window_Seconds)

        clear_memory_limit(node, ModuleCtx.Memory_High)
        workload.fault_windows.append((started, time.time()))

        assert not both_active, f'Two active nodes -> {both_active}'
        _ = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

    _finish(env, workload)

# ################################################################################################################################

def test_oom_kill_of_server(ha_pair:'HAEnvironment') -> 'None':
    """ The OOM killer ends a process of the Zato server inside the active container, the node keeps its role
    and starts the server again, and nothing is lost.
    """
    env = ha_pair
    workload = _start_workload(env)

    active = env.get_active()
    assert active is not None, 'No active node'

    protect_node_from_oom_killer(active)

    kills_before = read_oom_kills(active)
    anon = read_memory_anon(active)

    # Neither swap nor the page cache, which the kernel reclaims first, can absorb a limit below the memory of the processes.
    started = time.time()
    limit_memory(active, ModuleCtx.Swap_Max, ModuleCtx.No_Swap)
    limit_memory(active, ModuleCtx.Memory_Max, int(anon * ModuleCtx.OOM_Share))

    deadline = time.monotonic() + ModuleCtx.OOM_Timeout

    while read_oom_kills(active) == kills_before:
        assert time.monotonic() < deadline, f'No OOM kill in {active.node_name}'
        time.sleep(ModuleCtx.Poll_Interval)

    clear_memory_limit(active, ModuleCtx.Memory_Max)
    clear_memory_limit(active, ModuleCtx.Swap_Max)

    assert active.is_running(), f'{active.node_name} stopped instead of its server'

    _ = active.wait_until_server_up(ModuleCtx.Server_Timeout)
    workload.fault_windows.append((started, time.time()))

    _finish(env, workload)

# ################################################################################################################################

@pytest.mark.parametrize('clock_setting', ModuleCtx.Clock_Settings)
def test_clock_during_takeover(ha_session:'HASession', request:'any_', clock_setting:'tuple[int, float]') -> 'None':
    """ The wall clock of the standby jumps or changes its rate right before the active node fails, the standby
    takes over within the time it takes with a correct clock, and no scheduler slot runs twice.
    """
    preload = PreloadHook()
    offset_seconds, rate = clock_setting

    with ready_pair(ha_session, request.node.name, Timers(), [preload]) as env:
        workload = _start_workload(env)

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        preload.set_clock(standby, offset_seconds, rate)

        started = time.time()
        active.kill()

        _ = standby.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Takeover_Timeout)
        _ = standby.wait_until_server_up(ModuleCtx.Server_Timeout)

        active.resume()
        workload.fault_windows.append((started, time.time()))

        _finish(env, workload)

# ################################################################################################################################
# ################################################################################################################################
