# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Jobs with a limited number of runs, one-time jobs and runs in progress keep their run state when the server
# that runs them is replaced.

# stdlib
import time
from datetime import datetime, timezone

# Zato
from checks import check_run_log, get_starts, ModuleCtx as ChecksCtx, read_run_log, read_run_states, wait_for_starts
from failover import read_generation, wait_for_generation
from pair import start_server, stop_server, wait_for_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pair import SchedulerPair
    from zato.common.typing_ import anydict

    SchedulerPair = SchedulerPair
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

# How long a server may take to begin the runs that a test waits for, in seconds.
_runs_timeout_seconds = 120

# How long the new server may take to record its generation in the database, in seconds.
_takeover_timeout_seconds = 180

# How many runs of the job with a limited number of runs server A begins before it is replaced.
_repeats_before_switch = 5

# How long the servers keep running after the last expected run, so that an extra run would be observed, in seconds.
_settle_seconds = 10

# How long before the one-time job of the gap is due server A stops, and how long after it server B starts, in seconds.
_gap_margin_seconds = 20

# How recently a run of the long job must have begun for the takeover to take place while it is in progress, in seconds.
_in_flight_window_seconds = 5

# How often the run logs are read while a test waits for a run in progress, in seconds.
_poll_seconds = 0.2

# ################################################################################################################################
# ################################################################################################################################

def _take_over(pair:'SchedulerPair') -> 'float':
    """ Starts server B, which takes over, and returns the time at which its generation was observed in the database.
    """
    generation = read_generation(pair.database)

    start_server(pair.b)
    _ = wait_for_generation(pair.database, generation + 1, _takeover_timeout_seconds)

    out = time.time()

    _ = wait_for_server(pair.b)
    return out

# ################################################################################################################################

def _sleep_until(moment:'datetime') -> 'None':
    remaining = moment.timestamp() - datetime.now(timezone.utc).timestamp()

    if remaining > 0:
        time.sleep(remaining)

# ################################################################################################################################
# ################################################################################################################################

def test_repeats(pair:'SchedulerPair') -> 'None':
    """ A job with a limited number of runs begins some of them on server A and the rest on server B,
    and it runs as many times in total as it is defined to.
    """
    _ = wait_for_starts(pair, ChecksCtx.Job_Repeats, 'a', _repeats_before_switch, _runs_timeout_seconds)

    # Server A stops after some of the runs ..
    stop_server(pair.a)

    # .. server B runs the remaining ones ..
    _ = _take_over(pair)
    _ = wait_for_starts(pair, ChecksCtx.Job_Repeats, 'b', 1, _runs_timeout_seconds)

    total_timeout = ChecksCtx.Repeats * 2 + _runs_timeout_seconds
    _ = wait_for_starts(pair, ChecksCtx.Job_Repeats, '', ChecksCtx.Repeats, total_timeout)

    time.sleep(_settle_seconds)
    stop_server(pair.b)

    # .. and no more than that.
    entries = check_run_log(pair)
    starts = get_starts(entries, ChecksCtx.Job_Repeats)

    assert len(starts) == ChecksCtx.Repeats, len(starts)

    states = read_run_states(pair)
    assert states[ChecksCtx.Job_Repeats]['run_count'] == ChecksCtx.Repeats, states[ChecksCtx.Job_Repeats]

# ################################################################################################################################

def test_one_time_jobs(pair:'SchedulerPair') -> 'None':
    """ A one-time job that ran on server A does not run again on server B, and a one-time job that was due
    while neither server ran runs once when server B starts.
    """

    # Server A ran the one-time job that was due before it started ..
    _ = wait_for_starts(pair, ChecksCtx.Job_One_Time_Past, 'a', 1, _runs_timeout_seconds)

    stop_at = pair.gap_start.timestamp() - _gap_margin_seconds
    assert time.time() < stop_at, f'Server A started too late for the one-time job of the gap at {pair.gap_start}'

    # .. it stops before the other one-time job is due ..
    _sleep_until(datetime.fromtimestamp(stop_at, timezone.utc))
    stop_server(pair.a)

    # .. server B starts after it was due ..
    _sleep_until(datetime.fromtimestamp(pair.gap_start.timestamp() + _gap_margin_seconds, timezone.utc))

    _ = _take_over(pair)
    _ = wait_for_starts(pair, ChecksCtx.Job_One_Time_Gap, 'b', 1, _runs_timeout_seconds)

    time.sleep(_settle_seconds)
    stop_server(pair.b)

    # .. and each of the jobs ran once, the one of the gap with its own due time as its slot.
    entries = check_run_log(pair)

    past_starts = get_starts(entries, ChecksCtx.Job_One_Time_Past)
    gap_starts = get_starts(entries, ChecksCtx.Job_One_Time_Gap)

    assert len(past_starts) == 1, past_starts
    assert len(gap_starts) == 1, gap_starts

    gap_slot = datetime.fromisoformat(gap_starts[0]['slot'])
    assert gap_slot == pair.gap_start, gap_starts

# ################################################################################################################################

def _wait_for_run_in_progress(pair:'SchedulerPair') -> 'anydict':
    """ Waits until server A has just begun a run of the long job and returns its start.
    """
    deadline = time.monotonic() + _runs_timeout_seconds

    while True:
        starts = get_starts(read_run_log(pair), ChecksCtx.Job_Long_Run, 'a')

        if starts:
            latest = starts[-1]
            if time.time() - latest['time'] < _in_flight_window_seconds:
                return latest

        if time.monotonic() > deadline:
            raise Exception(f'Server A began no run of {ChecksCtx.Job_Long_Run} in {_runs_timeout_seconds}s')

        time.sleep(_poll_seconds)

# ################################################################################################################################

def test_run_in_progress(pair:'SchedulerPair') -> 'None':
    """ Server B takes over while a run of the long job is in progress on server A, server A completes it,
    and server B does not run its slot again but continues with the next one.
    """
    in_flight = _wait_for_run_in_progress(pair)

    # Server B takes over while the run is in progress ..
    boundary = _take_over(pair)
    assert boundary < in_flight['time'] + ChecksCtx.Long_Run_Seconds, 'The run was no longer in progress at the takeover'

    # .. server B begins the next slot of the long job ..
    _ = wait_for_starts(pair, ChecksCtx.Job_Long_Run, 'b', 1, _runs_timeout_seconds)

    stop_server(pair.a)
    stop_server(pair.b)

    entries = check_run_log(pair)

    # .. server A completed the run that was in progress ..
    ends = []

    for entry in entries:
        if entry['phase'] == ChecksCtx.Phase_End and entry['job'] == ChecksCtx.Job_Long_Run and entry['server'] == 'a':
            if entry['slot'] == in_flight['slot']:
                ends.append(entry)

    assert len(ends) == 1, ends

    # .. and server B did not run its slot.
    b_starts = get_starts(entries, ChecksCtx.Job_Long_Run, 'b')
    in_flight_slot = datetime.fromisoformat(in_flight['slot'])

    for entry in b_starts:
        assert datetime.fromisoformat(entry['slot']) > in_flight_slot, entry

# ################################################################################################################################
# ################################################################################################################################
