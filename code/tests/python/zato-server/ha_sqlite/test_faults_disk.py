# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Disk faults on the active node and on the standby - delayed syncs and writes, a bandwidth and IOPS limit, EIO
# and ENOSPC - during traffic, which runs long enough for the checkpoints of the node, and during a rejoin.
# EIO on the syncs of the standby leads to a mark-out, and ENOSPC on the active node returns errors to clients
# until space is available again.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_copies, check_scheduler, check_workload
from ha_env import ready_pair
from ha_tools import clear_disk_limit, limit_disk, ModuleCtx as ToolsCtx, PreloadHook
from ha_traffic import get_percentile, TimedPublisher
from nodes import Timers
from workload import Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from nodes import Node
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.faults_disk')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The node whose disk fails
    Target_Active = 'active'
    Target_Standby = 'standby'
    Targets = [Target_Active, Target_Standby]

    # The full extent of a delayed sync or write, in microseconds, and the disk of the baseline
    Max_Delay_US = 200000
    Baseline_Bytes_Per_Second = 100 * 1024 * 1024
    Baseline_Operations_Per_Second = 2000

    # How long the traffic runs before the faults and under each severity, in seconds
    Traffic_Seconds = 10
    Window_Seconds = 60

    # How long requests in flight when a fault begins may still be acknowledged, in seconds
    In_Flight_Grace = 2.0

    # How long the pair may take to recover, in seconds
    Recovery_Timeout = 300

    # How long the active node may take to mark out a standby whose syncs fail, in seconds
    Mark_Out_Timeout = 60

    # How long clients may take to be acknowledged again once space is available, in seconds
    Resume_Timeout = 120

    # How often the test checks whether clients are acknowledged again, in seconds
    Poll_Interval = 0.5

    # The percentiles of the latency that each run reports
    Percentile_50 = 0.5
    Percentile_99 = 0.99

    # The roles of the pair
    Active_Solo = ['ActiveSolo']
    Standby_In_Sync = ['StandbyInSync']

# ################################################################################################################################
# ################################################################################################################################

def _get_target(env:'HAEnvironment', target:'str') -> 'tuple[Node, Node]':
    """ Returns the node whose disk fails and the other node.
    """
    active = env.get_active()
    assert active is not None, 'No active node'

    standby = env.get_other(active)

    if target == ModuleCtx.Target_Active:
        out = (active, standby)
    else:
        out = (standby, active)

    return out

# ################################################################################################################################

def _report(publisher:'TimedPublisher', name:'str', started:'float', ended:'float') -> 'None':
    latencies = publisher.get_latencies_between(started, ended)
    rate = len(latencies) / (ended - started)
    p50 = get_percentile(latencies, ModuleCtx.Percentile_50)
    p99 = get_percentile(latencies, ModuleCtx.Percentile_99)

    logger.info('%s -> %.1f acknowledgments/s, p50 %.3fs, p99 %.3fs', name, rate, p50, p99)

# ################################################################################################################################

def _finish(env:'HAEnvironment', workload:'Workload', publisher:'TimedPublisher') -> 'None':
    """ Waits for the pair, stops the traffic and applies the checks of every run.
    """
    active = env.wait_for_pair(ModuleCtx.Recovery_Timeout)
    publisher.stop()

    check_workload(env, workload)

    _ = check_scheduler(env, active)
    check_copies(env, active)

# ################################################################################################################################

def _start_traffic(env:'HAEnvironment') -> 'tuple[Workload, TimedPublisher]':
    workload = Workload(cast_('any_', env), cast_('any_', [env.haproxy]))
    workload.start()

    publisher = TimedPublisher(env.haproxy.base_url, env.publisher_username, env.publisher_password)
    publisher.start()

    time.sleep(ModuleCtx.Traffic_Seconds)

    out = (workload, publisher)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('target', ModuleCtx.Targets)
def test_delayed_syncs(ha_session:'HASession', request:'any_', target:'str') -> 'None':
    """ Syncs and writes of one node are delayed at each severity under traffic, and the pair loses nothing.
    """
    preload = PreloadHook()

    with ready_pair(ha_session, request.node.name, Timers(), [preload]) as env:
        workload, publisher = _start_traffic(env)

        for severity in ToolsCtx.Severities:
            failing, _ = _get_target(env, target)
            delay_us = int(ModuleCtx.Max_Delay_US * severity)

            preload.set_disk_fault(failing, delay_us, 0, ToolsCtx.Errno_EIO)
            started = time.time()

            time.sleep(ModuleCtx.Window_Seconds)

            ended = time.time()
            preload.clear_disk_fault(failing)
            workload.fault_windows.append((started, ended))

            _report(publisher, f'{target} delay {delay_us}us', started, ended)
            _ = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

        _finish(env, workload, publisher)

# ################################################################################################################################

@pytest.mark.parametrize('target', ModuleCtx.Targets)
def test_disk_limit(ha_pair:'HAEnvironment', target:'str') -> 'None':
    """ The bandwidth and IOPS of one node are limited at each severity under traffic, and the pair loses nothing.
    """
    env = ha_pair
    workload, publisher = _start_traffic(env)

    for severity in ToolsCtx.Severities:
        failing, _ = _get_target(env, target)

        bytes_per_second = int(ModuleCtx.Baseline_Bytes_Per_Second * (1 - severity))
        operations_per_second = int(ModuleCtx.Baseline_Operations_Per_Second * (1 - severity))

        limit_disk(failing, bytes_per_second, operations_per_second)
        started = time.time()

        time.sleep(ModuleCtx.Window_Seconds)

        ended = time.time()
        clear_disk_limit(failing)
        workload.fault_windows.append((started, ended))

        _report(publisher, f'{target} {bytes_per_second}B/s {operations_per_second}IOPS', started, ended)
        _ = env.wait_for_pair(ModuleCtx.Recovery_Timeout)

    _finish(env, workload, publisher)

# ################################################################################################################################

@pytest.mark.parametrize('target', ModuleCtx.Targets)
def test_delayed_syncs_during_rejoin(ha_session:'HASession', request:'any_', target:'str') -> 'None':
    """ The standby rejoins under traffic while the syncs and writes of one of the two nodes are delayed.
    """
    preload = PreloadHook()

    with ready_pair(ha_session, request.node.name, Timers(), [preload]) as env:
        workload, publisher = _start_traffic(env)

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        if target == ModuleCtx.Target_Active:
            failing = active
        else:
            failing = standby

        standby.kill()
        _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)

        delay_us = int(ModuleCtx.Max_Delay_US * ToolsCtx.Severities[-1])
        preload.set_disk_fault(failing, delay_us, 0, ToolsCtx.Errno_EIO)

        started = time.time()
        standby.resume()

        _ = standby.wait_for_role(ModuleCtx.Standby_In_Sync, ModuleCtx.Recovery_Timeout)

        preload.clear_disk_fault(failing)
        workload.fault_windows.append((started, time.time()))

        _finish(env, workload, publisher)

# ################################################################################################################################

def test_standby_sync_error(ha_session:'HASession', request:'any_') -> 'None':
    """ Every sync of the standby fails with EIO, so it confirms nothing and the active node marks it out
    and continues alone until the standby can sync again.
    """
    preload = PreloadHook()

    with ready_pair(ha_session, request.node.name, Timers(), [preload]) as env:
        workload, publisher = _start_traffic(env)

        active = env.get_active()
        assert active is not None, 'No active node'

        standby = env.get_other(active)

        preload.set_disk_fault(standby, 0, 100, ToolsCtx.Errno_EIO)
        started = time.time()

        _ = active.wait_for_role(ModuleCtx.Active_Solo, ModuleCtx.Mark_Out_Timeout)
        time.sleep(ModuleCtx.Traffic_Seconds)

        acknowledged = publisher.get_acknowledged_between(started + ModuleCtx.In_Flight_Grace, time.time())
        assert acknowledged, 'No publication acknowledged by the active node alone'

        preload.clear_disk_fault(standby)
        workload.fault_windows.append((started, time.time()))

        # A standby that stopped on the error starts again.
        if not standby.is_running():
            standby.resume()

        _finish(env, workload, publisher)

# ################################################################################################################################

def test_active_disk_full(ha_session:'HASession', request:'any_') -> 'None':
    """ Every write of the active node fails with ENOSPC, so clients receive errors and no acknowledgment,
    and once space is available, clients are acknowledged again.
    """
    preload = PreloadHook()

    with ready_pair(ha_session, request.node.name, Timers(), [preload]) as env:
        workload, publisher = _start_traffic(env)

        active = env.get_active()
        assert active is not None, 'No active node'

        preload.set_disk_fault(active, 0, 100, ToolsCtx.Errno_ENOSPC)
        started = time.time()

        time.sleep(ModuleCtx.Window_Seconds)

        acknowledged = publisher.get_acknowledged_between(started + ModuleCtx.In_Flight_Grace, time.time())
        assert not acknowledged, f'Acknowledged with no space on the disk -> {acknowledged}'

        errors = publisher.count_errors_after(started)
        assert errors > 0, 'No client received an error'

        # Space is available again ..
        preload.clear_disk_fault(active)
        freed = time.time()

        deadline = time.monotonic() + ModuleCtx.Resume_Timeout

        while not publisher.get_acknowledged_between(freed, time.time()):
            assert time.monotonic() < deadline, 'No publication acknowledged once space was available'
            time.sleep(ModuleCtx.Poll_Interval)

        # .. and the pair continues with nothing lost.
        workload.fault_windows.append((started, time.time()))

        for node in env.node_list:
            if not node.is_running():
                node.resume()

        _finish(env, workload, publisher)

# ################################################################################################################################
# ################################################################################################################################
