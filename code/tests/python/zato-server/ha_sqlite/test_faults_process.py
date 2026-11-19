# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# CPU, memory and clock faults on each node - a CPU limit and memory pressure at each severity, an OOM kill
# of the Zato server inside the active container, offsets of the wall clock of the standby during a takeover,
# which the timers of the node do not follow, as they use the monotonic clock, skews of the wall clock of the standby
# below and above the bound at which it is in sync, and a takeover by a node whose wall clock is behind the floor
# of the time of the Zato database.

# stdlib
import json
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload, ModuleCtx as ChecksCtx, read_rows, watch_roles
from ha_env import ModuleCtx as EnvCtx, ready_pair
from ha_tools import clear_cpu_limit, clear_memory_limit, limit_cpu, limit_memory, ModuleCtx as ToolsCtx, PreloadHook, \
    protect_node_from_oom_killer, read_memory_anon, read_memory_current, read_oom_kills
from nodes import ModuleCtx as NodesCtx, Timers
from workload import Topic_Name, Workload
from zato.common.pubsub.sql.clock import Floor_Key, Floor_Object_Name, Floor_Object_Type
from zato.common.test.client import PublishClient
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from nodes import Node
    from zato.common.typing_ import any_, strlist, strset

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
    Traffic_Seconds = 5
    Window_Seconds = 15

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

    # The offsets of the wall clock, in seconds, and its rate
    Clock_Settings = [
        (120, 1.0),
        (-120, 1.0),
    ]

    # The rate of a wall clock that runs as the clock of the host does
    Clock_Rate = 1.0

    # The offset of a wall clock that agrees with the clock of the host, in seconds
    No_Clock_Offset = 0

    # The skews of the wall clock of the standby beyond and within the default bound of one second, in seconds
    Skew_Beyond_Bound_Seconds = 5
    Skew_Within_Bound_Seconds = 0.2

    # How far behind the wall clock of the node that takes over is, in seconds
    Clock_Behind_Seconds = -120

    # How long the active node may take to mark out a standby whose clock moved beyond the bound, which covers
    # the heartbeats that the estimate of the skew is taken from and the write of the referee, in seconds
    Skew_Mark_Out_Timeout = 30

    # The role of an active node without a standby in sync, and the role of the standby in sync
    Role_Active_Solo = 'ActiveSolo'
    Role_Standby_In_Sync = EnvCtx.Role_Standby_In_Sync

    # The prefix of the message ID published after a takeover by a node whose clock is behind
    Clock_Behind_Msg_Id_Prefix = 'zpsm.ha.clock-behind'

    # The query of the floor of the time of the Zato database
    Floor_Query = 'select data from zato_shared_object where object_type = ? and name = ?'

    # The query of the time at which the dedup record of a message was written
    Received_Query = 'select received_ms from zato_message_dedup where message_id = ?'

    # How long the standby with a changed clock may take to take over, which exceeds the takeover timer of the node
    # with a margin for the start of its role and stays well below any wait that a wall-clock timer would cause, in seconds
    Clock_Takeover_Timeout = 15

    # How long the pair may take to recover, in seconds
    Recovery_Timeout = 300

    # How long a server may take to start, in seconds
    Server_Timeout = 120

    # The roles of a node that serves requests
    Active_Roles:'strlist' = list(NodesCtx.Active_Roles)

    # How many claims of each scheduler job a server killed between a claim and its run may leave without a run
    Unrun_Claims_After_Kill = 1

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

def _finish(env:'HAEnvironment', workload:'Workload', unrun_claims:'int'=0) -> 'None':
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

    check_workload(env, workload)

    _ = check_scheduler(env, active, unrun_claims)
    check_copies(env, active)

# ################################################################################################################################

def _watch_node_roles(node:'Node', seconds:'float') -> 'strset':
    """ Returns every role that a node reports during the given number of seconds.
    """
    out:'strset' = set()
    deadline = time.monotonic() + seconds

    while time.monotonic() < deadline:
        report = node.read_role()

        if report is not None:
            out.add(report['role'])

        time.sleep(ModuleCtx.Poll_Interval)

    return out

# ################################################################################################################################

def _read_floor_ms(node:'Node') -> 'int':
    """ Returns the floor of the time of the Zato database of a node.
    """
    params = [Floor_Object_Type, Floor_Object_Name]
    rows = read_rows(node.db_path(ChecksCtx.Database_File), ModuleCtx.Floor_Query, params)
    assert rows, f'No floor in {node.node_name}'

    data = json.loads(rows[0][0])

    out = data[Floor_Key]
    return out

# ################################################################################################################################

def _read_received_ms(node:'Node', msg_id:'str') -> 'int':
    """ Returns the time at which the dedup record of a message was written in the Zato database of a node.
    """
    rows = read_rows(node.db_path(ChecksCtx.Database_File), ModuleCtx.Received_Query, [msg_id])
    assert rows, f'No dedup record of {msg_id} in {node.node_name}'

    out = rows[0][0]
    return out

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

        started = time.time()
        active.kill()

        # The clock of the standby changes once the active node no longer runs, as a standby whose clock moved away
        # from that of a running active node is marked out instead.
        preload.set_clock(standby, offset_seconds, rate)

        _ = standby.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Clock_Takeover_Timeout)
        _ = standby.wait_until_server_up(ModuleCtx.Server_Timeout)

        # The node that failed returns with the clock of the node that took over, so that it is admitted in sync.
        preload.set_clock(active, offset_seconds, rate)
        active.resume()
        workload.fault_windows.append((started, time.time()))

        # An active node that is killed leaves the claim it committed before the run began
        # in the copy of the standby without a run.
        _finish(env, workload, ModuleCtx.Unrun_Claims_After_Kill)

# ################################################################################################################################

def test_clock_skew_beyond_bound(ha_session:'HASession', request:'any_') -> 'None':
    """ The wall clock of the standby moves beyond the bound of the skew, the active node marks it out and admits it
    again only once its clock agrees, and nothing is lost.
    """
    preload = PreloadHook()

    with ready_pair(ha_session, request.node.name, Timers(), [preload]) as env:
        workload = _start_workload(env)

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        started = time.time()
        preload.set_clock(standby, ModuleCtx.Skew_Beyond_Bound_Seconds, ModuleCtx.Clock_Rate)

        # The active node marks the standby out ..
        _ = active.wait_for_role([ModuleCtx.Role_Active_Solo], ModuleCtx.Skew_Mark_Out_Timeout)

        # .. and does not admit it again for as long as its clock is skewed ..
        roles = _watch_node_roles(standby, ModuleCtx.Window_Seconds)
        assert ModuleCtx.Role_Standby_In_Sync not in roles, f'{standby.node_name} admitted with a skew -> {roles}'

        # .. until its clock agrees again.
        preload.set_clock(standby, ModuleCtx.No_Clock_Offset, ModuleCtx.Clock_Rate)
        workload.fault_windows.append((started, time.time()))

        _finish(env, workload)

# ################################################################################################################################

def test_clock_skew_within_bound(ha_session:'HASession', request:'any_') -> 'None':
    """ The wall clock of the standby moves within the bound of the skew, the standby stays in sync and takes over
    once the active node fails, and nothing is lost.
    """
    preload = PreloadHook()

    with ready_pair(ha_session, request.node.name, Timers(), [preload]) as env:
        workload = _start_workload(env)

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        preload.set_clock(standby, ModuleCtx.Skew_Within_Bound_Seconds, ModuleCtx.Clock_Rate)

        # The standby stays in sync with its clock skewed ..
        roles = _watch_node_roles(standby, ModuleCtx.Window_Seconds)
        assert roles == {ModuleCtx.Role_Standby_In_Sync}, f'{standby.node_name} left the sync -> {roles}'

        # .. and takes over once the active node fails.
        started = time.time()
        active.kill()

        _ = standby.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Clock_Takeover_Timeout)
        _ = standby.wait_until_server_up(ModuleCtx.Server_Timeout)

        active.resume()
        workload.fault_windows.append((started, time.time()))

        _finish(env, workload, ModuleCtx.Unrun_Claims_After_Kill)

# ################################################################################################################################

def test_clock_behind_after_takeover(ha_session:'HASession', request:'any_') -> 'None':
    """ The node that takes over has a wall clock behind the floor of the time of the Zato database that the failed
    active node persisted, and the time it issues does not fall below that floor.
    """
    preload = PreloadHook()

    with ready_pair(ha_session, request.node.name, Timers(), [preload]) as env:
        workload = _start_workload(env)

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        floor_ms = _read_floor_ms(active)

        started = time.time()
        active.kill()

        # The clock of the standby falls behind once the active node no longer runs ..
        preload.set_clock(standby, ModuleCtx.Clock_Behind_Seconds, ModuleCtx.Clock_Rate)

        _ = standby.wait_for_role(ModuleCtx.Active_Roles, ModuleCtx.Clock_Takeover_Timeout)
        _ = standby.wait_until_server_up(ModuleCtx.Server_Timeout)

        # .. and a message published after the takeover receives a time at or above the floor.
        client = PublishClient(env.haproxy.base_url, env.publisher_username, env.publisher_password)

        msg_id = f'{ModuleCtx.Clock_Behind_Msg_Id_Prefix}.{time.time_ns()}'
        data = {'clock_behind_after_takeover': msg_id}

        result = client.publish(Topic_Name, data, msg_id=msg_id)
        assert result['msg_id'] == msg_id, result

        received_ms = _read_received_ms(standby, msg_id)
        assert received_ms >= floor_ms, f'Time {received_ms} of {msg_id} below the floor {floor_ms}'

        # The node that failed returns with the clock of the node that took over, so that it is admitted in sync.
        preload.set_clock(active, ModuleCtx.Clock_Behind_Seconds, ModuleCtx.Clock_Rate)
        active.resume()
        workload.fault_windows.append((started, time.time()))

        _finish(env, workload, ModuleCtx.Unrun_Claims_After_Kill)

# ################################################################################################################################
# ################################################################################################################################
