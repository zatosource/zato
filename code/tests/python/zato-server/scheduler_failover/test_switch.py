# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The active server of a pair is stopped, killed, overlapped by its replacement, frozen or cut off from its database,
# and its replacement continues each job from where it was left, with no slot run twice.

# stdlib
import time
from datetime import datetime, timezone

# pytest
import pytest

# Zato
from checks import check_run_log, get_catch_up_problems, get_starts, get_starts_after, Job_Intervals, \
    ModuleCtx as ChecksCtx, read_run_log, read_skip_counts, wait_for_starts
from failover import read_generation, wait_for_generation
from pair import cut_off_server, kill_server, pause_server, start_server, stop_server, unpause_server, wait_for_server
from zato.common.api import SCHEDULER

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pair import SchedulerPair
    from zato.common.typing_ import callable_

    SchedulerPair = SchedulerPair
    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

# How long a server may take to begin the runs that a test waits for, in seconds.
_runs_timeout_seconds = 120

# How long the new server may take to record its generation in the database, in seconds.
_takeover_timeout_seconds = 180

# How many runs of the job of every second a server begins before the test continues.
_warm_up_runs = 10

# How long the replaced server keeps running after the takeover in the tests that let it, in seconds.
_replaced_run_seconds = 10

# The jobs whose missed slots are checked after a switch.
_catch_up_jobs = [ChecksCtx.Job_Every_Second, ChecksCtx.Job_Jitter, ChecksCtx.Job_Long_Run]

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_runs(pair:'SchedulerPair', server_label:'str', long_runs:'int') -> 'None':
    """ Waits until a server began runs of the frequent jobs and the given number of runs of the long one.
    """
    _ = wait_for_starts(pair, ChecksCtx.Job_Every_Second, server_label, _warm_up_runs, _runs_timeout_seconds)
    _ = wait_for_starts(pair, ChecksCtx.Job_Jitter, server_label, 2, _runs_timeout_seconds)
    _ = wait_for_starts(pair, ChecksCtx.Job_Long_Run, server_label, long_runs, _runs_timeout_seconds)

# ################################################################################################################################

def _wait_past_two_slots(pair:'SchedulerPair') -> 'None':
    """ Waits until two slots of the long job passed since the last one that server A began, so that every job
    has missed slots by the time server B starts.
    """
    entries = read_run_log(pair)
    starts = get_starts(entries, ChecksCtx.Job_Long_Run, 'a')
    last_slot = datetime.fromisoformat(starts[-1]['slot'])

    interval = Job_Intervals[ChecksCtx.Job_Long_Run]
    wait_until = last_slot.timestamp() + 2 * interval + 1
    remaining = wait_until - datetime.now(timezone.utc).timestamp()

    if remaining > 0:
        time.sleep(remaining)

# ################################################################################################################################

def _take_over(pair:'SchedulerPair', generation:'int') -> 'float':
    """ Starts server B, which takes over, and returns the time at which its generation was observed in the database.
    """
    start_server(pair.b)
    _ = wait_for_generation(pair.database, generation + 1, _takeover_timeout_seconds)

    out = time.time()

    _ = wait_for_server(pair.b)
    return out

# ################################################################################################################################

def _check_catch_up(pair:'SchedulerPair') -> 'None':
    entries = check_run_log(pair)

    problems:'list[str]' = []

    for job in _catch_up_jobs:
        problems.extend(get_catch_up_problems(entries, job, 'a', 'b'))

    assert not problems, problems

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('stop_function', [stop_server, kill_server], ids=['stop', 'kill'])
def test_stopped_server(pair:'SchedulerPair', stop_function:'callable_') -> 'None':
    """ Server A is stopped gracefully or killed, server B starts after each job missed slots, runs one catch-up run
    of each such job and continues with the later slots, and no slot runs twice.
    """
    _wait_for_runs(pair, 'a', 1)
    generation = read_generation(pair.database)

    # Server A stops while it runs its jobs ..
    stop_function(pair.a)
    _wait_past_two_slots(pair)

    # .. server B takes over and continues each job ..
    _ = _take_over(pair, generation)
    _wait_for_runs(pair, 'b', 2)

    stop_server(pair.b)

    # .. with one catch-up run of each job, no slot run twice, and the run state in agreement with the runs.
    _check_catch_up(pair)

# ################################################################################################################################

def test_overlap(pair:'SchedulerPair') -> 'None':
    """ Server B starts while server A still runs, server A begins no run after the takeover, and each of its
    attempts is skipped as not active.
    """
    _wait_for_runs(pair, 'a', 1)
    generation = read_generation(pair.database)

    # Server B takes over with server A running throughout ..
    boundary = _take_over(pair, generation)
    _wait_for_runs(pair, 'b', 1)

    time.sleep(_replaced_run_seconds)

    stop_server(pair.a)
    stop_server(pair.b)

    # .. server A begins no run after the takeover and skips its slots instead ..
    entries = check_run_log(pair)

    late = get_starts_after(entries, 'a', boundary)
    assert not late, late

    skip_counts = read_skip_counts(pair.a)
    assert skip_counts[SCHEDULER.OUTCOME.SKIPPED_NOT_ACTIVE] > 0, skip_counts

# ################################################################################################################################

def test_frozen_server(pair:'SchedulerPair') -> 'None':
    """ Server A is frozen, server B takes over, and once server A resumes, it begins no run
    and each of its attempts is skipped as not active.
    """
    _wait_for_runs(pair, 'a', 1)
    generation = read_generation(pair.database)

    # Server A is frozen and server B takes over ..
    pause_server(pair.a)

    boundary = _take_over(pair, generation)
    _wait_for_runs(pair, 'b', 1)

    # .. server A resumes and runs for a while next to server B ..
    unpause_server(pair.a)
    time.sleep(_replaced_run_seconds)

    stop_server(pair.a)
    stop_server(pair.b)

    # .. and it begins no run after the takeover.
    entries = check_run_log(pair)

    late = get_starts_after(entries, 'a', boundary)
    assert not late, late

    skip_counts = read_skip_counts(pair.a)
    assert skip_counts[SCHEDULER.OUTCOME.SKIPPED_NOT_ACTIVE] > 0, skip_counts

# ################################################################################################################################

def test_cut_off_server(pair:'SchedulerPair') -> 'None':
    """ Server A is cut off from its database and its clients with its process running, server B takes over,
    and once the links of server A are restored, it begins no run and each of its attempts is skipped as not active.
    """
    _wait_for_runs(pair, 'a', 1)
    generation = read_generation(pair.database)

    # Server A loses its links and server B takes over ..
    cut_off_server(pair.a, 'block')

    boundary = _take_over(pair, generation)
    _wait_for_runs(pair, 'b', 1)

    # .. the links of server A are restored and it runs for a while next to server B ..
    cut_off_server(pair.a, 'unblock')
    time.sleep(_replaced_run_seconds)

    stop_server(pair.a)
    stop_server(pair.b)

    # .. and it begins no run after the takeover.
    entries = check_run_log(pair)

    late = get_starts_after(entries, 'a', boundary)
    assert not late, late

    skip_counts = read_skip_counts(pair.a)
    assert skip_counts[SCHEDULER.OUTCOME.SKIPPED_NOT_ACTIVE] > 0, skip_counts

# ################################################################################################################################
# ################################################################################################################################
