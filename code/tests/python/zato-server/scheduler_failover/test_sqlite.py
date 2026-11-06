# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A single server on SQLite keeps the run state of its jobs in the file of pub/sub across a restart.

# stdlib
import time

# Zato
from checks import check_run_log, get_starts, ModuleCtx as ChecksCtx, read_run_states, wait_for_starts
from pair import start_server, stop_server, wait_for_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pair import SchedulerPair

    SchedulerPair = SchedulerPair

# ################################################################################################################################
# ################################################################################################################################

# How long the server may take to begin the runs that the test waits for, in seconds.
_runs_timeout_seconds = 180

# How many runs of the job with a limited number of runs the server begins before its restart.
_repeats_before_restart = 5

# How long the server keeps running after the last expected run, so that an extra run would be observed, in seconds.
_settle_seconds = 10

# ################################################################################################################################
# ################################################################################################################################

def test_restart(sqlite_server:'SchedulerPair') -> 'None':
    """ The server restarts, the one-time job that it ran does not run again, and the job with a limited number
    of runs continues from where it was and runs as many times in total as it is defined to.
    """
    pair = sqlite_server

    _ = wait_for_starts(pair, ChecksCtx.Job_One_Time_Past, 'a', 1, _runs_timeout_seconds)
    _ = wait_for_starts(pair, ChecksCtx.Job_Repeats, 'a', _repeats_before_restart, _runs_timeout_seconds)

    # The server restarts ..
    stop_server(pair.a)
    start_server(pair.a)
    _ = wait_for_server(pair.a)

    # .. and runs the remaining runs of the job with a limited number of runs ..
    total_timeout = ChecksCtx.Repeats * 2 + _runs_timeout_seconds
    _ = wait_for_starts(pair, ChecksCtx.Job_Repeats, 'a', ChecksCtx.Repeats, total_timeout)

    time.sleep(_settle_seconds)
    stop_server(pair.a)

    # .. and no more than that, with the one-time job not run again.
    entries = check_run_log(pair)

    assert len(get_starts(entries, ChecksCtx.Job_Repeats)) == ChecksCtx.Repeats
    assert len(get_starts(entries, ChecksCtx.Job_One_Time_Past)) == 1

    states = read_run_states(pair)
    assert states[ChecksCtx.Job_Repeats]['run_count'] == ChecksCtx.Repeats, states[ChecksCtx.Job_Repeats]

# ################################################################################################################################
# ################################################################################################################################
