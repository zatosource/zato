# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# For twenty minutes, the active server is replaced every four minutes, in turn after a graceful stop, a SIGKILL,
# a pause and a cut-off, while the jobs run and the pub/sub workload publishes, pulls and receives pushes.

# stdlib
import logging
import time

# Zato
from checks import check_run_log, get_starts, ModuleCtx as ChecksCtx
from failover import read_generation, wait_for_generation
from pair import cut_off_server, kill_server, pause_server, start_server, stop_server, unpause_server, wait_for_server
from resources import get_resource_growth, ResourceMonitor
from workload import get_count_mismatches, get_repeats_not_in_flight, Topic_Name, Workload
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pair import SchedulerPair, SchedulerServer
    from zato.common.typing_ import any_

    SchedulerPair = SchedulerPair
    SchedulerServer = SchedulerServer
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.scheduler_failover.repeated')

# How long the scenario runs and how often the active server is replaced, in seconds.
_duration_seconds = 20 * 60
_switch_interval_seconds = 4 * 60

# The faults applied to the active server, in turn.
_fault_stop = 'stop'
_fault_kill = 'kill'
_fault_pause = 'pause'
_fault_cut_off = 'cut-off'

_faults = [_fault_stop, _fault_kill, _fault_pause, _fault_cut_off]

# How long the new server may take to record its generation in the database, in seconds.
_takeover_timeout_seconds = 180

# ################################################################################################################################
# ################################################################################################################################

def _apply_fault(server:'SchedulerServer', fault:'str') -> 'None':
    if fault == _fault_stop:
        stop_server(server)
    elif fault == _fault_kill:
        kill_server(server)
    elif fault == _fault_pause:
        pause_server(server)
    else:
        cut_off_server(server, 'block')

# ################################################################################################################################

def _end_fault(server:'SchedulerServer', fault:'str') -> 'None':
    """ Stops a replaced server that is still running, which a frozen server resumes for and a cut-off one has its links restored for.
    """
    if fault == _fault_pause:
        unpause_server(server)
        stop_server(server)

    elif fault == _fault_cut_off:
        cut_off_server(server, 'unblock')
        stop_server(server)

# ################################################################################################################################
# ################################################################################################################################

def test_repeated_failover(workload_pair:'SchedulerPair') -> 'None':
    """ No slot runs twice across the servers, no replaced server begins a run until it starts again, the run counts
    equal the run state, the pub/sub workload loses nothing, and the resources of each active server remain bounded.
    """
    pair = workload_pair

    workload = Workload(cast_('any_', pair), [pair.a.server, pair.b.server])

    monitor = ResourceMonitor()
    monitor.set_active(pair.a)
    monitor.start()

    workload.start()

    active = pair.a
    standby = pair.b

    # Each replaced server with the time of its takeover, and each start of a server with its time.
    takeovers:'list[tuple[str, float]]' = []
    restarts:'list[tuple[str, float]]' = []

    switch_count = _duration_seconds // _switch_interval_seconds - 1
    started = time.monotonic()

    try:
        for index in range(switch_count):
            time.sleep(_switch_interval_seconds)

            fault = _faults[index % len(_faults)]
            generation = read_generation(pair.database)

            logger.info('Switch %d - %s of server %s', index + 1, fault, active.label)

            # The active server fails ..
            monitor.clear_active()
            fault_started = time.time()
            _apply_fault(active, fault)

            # .. the standby starts and takes over ..
            restarts.append((standby.label, time.time()))
            start_server(standby)

            _ = wait_for_generation(pair.database, generation + 1, _takeover_timeout_seconds)
            takeovers.append((active.label, time.time()))

            _ = wait_for_server(standby)
            monitor.set_active(standby)

            # .. and the old server stops for good, which ends the fault.
            _end_fault(active, fault)
            workload.fault_windows.append((fault_started, time.time()))

            active, standby = standby, active

        remaining = _duration_seconds - (time.monotonic() - started)

        if remaining > 0:
            time.sleep(remaining)

    finally:
        workload.is_publishing.clear()
        monitor.stop()

    # The pull subscriber took every acknowledged publication, and each push that the receiver received more than once
    # was in progress during a fault. The publishers produce more than one push subscriber receives in the same time,
    # so the pushes still queued at the end are not waited for ..
    workload.drain_pulls()

    unexpected = workload.get_unexpected_repeated_pulls()
    assert not unexpected, sorted(unexpected)[:10]

    records = pair.receivers[Topic_Name].get_request_records()
    not_in_flight = get_repeats_not_in_flight(records, workload.fault_windows)
    assert not not_in_flight, not_in_flight[:10]

    stop_server(active)

    # .. with the stored counts equal to the rows ..
    mismatches = get_count_mismatches(cast_('any_', pair))
    assert not mismatches, mismatches

    # .. no slot ran twice and the run counts equal the run state ..
    entries = check_run_log(pair)

    # .. no replaced server began a run between its takeover and its next start ..
    late:'list[dict]' = []

    for label, boundary in takeovers:

        next_start = float('inf')

        for restart_label, restart_time in restarts:
            if restart_label == label and restart_time > boundary:
                next_start = restart_time
                break

        limit = boundary + ChecksCtx.Takeover_Tolerance_Seconds

        for entry in get_starts(entries, server_label=label):
            if limit < entry['time'] < next_start:
                late.append(entry)

    assert not late, late[:10]

    # .. and the resources of each active server remained within their bounds.
    growth = get_resource_growth(monitor.periods)
    assert not growth, growth

# ################################################################################################################################
# ################################################################################################################################
