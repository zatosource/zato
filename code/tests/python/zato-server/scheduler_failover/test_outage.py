# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared database is unavailable for a time, during which the active server skips its slots and after which
# it continues as the active server.

# stdlib
import time

# pytest
import pytest

# Zato
from checks import check_run_log, get_starts, ModuleCtx as ChecksCtx, read_run_log, read_skip_counts, wait_for_starts
from failover import docker, read_generation
from pair import stop_server
from zato.common.api import SCHEDULER

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pair import SchedulerPair

    SchedulerPair = SchedulerPair

# ################################################################################################################################
# ################################################################################################################################

# How long a server may take to begin the runs that a test waits for, in seconds.
_runs_timeout_seconds = 180

# How many runs of the job of every second a server begins before and after an outage.
_runs_around_outage = 10

# How long the database is unavailable in each test, in seconds.
_outage_seconds = [70]

# ################################################################################################################################
# ################################################################################################################################

def _run_database_outage(pair:'SchedulerPair', outage_seconds:'int') -> 'None':
    database = pair.database

    _ = wait_for_starts(pair, ChecksCtx.Job_Every_Second, 'a', _runs_around_outage, _runs_timeout_seconds)
    generation = read_generation(database)

    # The database stops ..
    _ = docker('stop', database.container_name)
    outage_start = time.time()

    time.sleep(outage_seconds)

    # .. and returns ..
    _ = docker('start', database.container_name)
    outage_end = time.time()

    before = get_starts(read_run_log(pair), ChecksCtx.Job_Every_Second, 'a')
    _ = wait_for_starts(pair, ChecksCtx.Job_Every_Second, 'a', len(before) + _runs_around_outage, _runs_timeout_seconds)

    stop_server(pair.a)

    # .. server A began no run while it was unavailable ..
    entries = check_run_log(pair)
    limit = outage_start + ChecksCtx.Takeover_Tolerance_Seconds

    during = []

    for entry in get_starts(entries, server_label='a'):
        if limit < entry['time'] < outage_end:
            during.append(entry)

    assert not during, during

    # .. it skipped the slots due in the meantime ..
    skip_counts = read_skip_counts(pair.a)
    assert skip_counts[SCHEDULER.OUTCOME.SKIPPED_NOT_ACTIVE] > 0, skip_counts

    # .. and it is still the active server.
    assert read_generation(database) == generation

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', _outage_seconds)
def test_database_outage(pair:'SchedulerPair', outage_seconds:'int') -> 'None':
    """ The shared database stops for a time, server A skips each slot due in the meantime as not active,
    begins no run, and continues as the active server once the database returns.
    """
    _run_database_outage(pair, outage_seconds)

# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', _outage_seconds)
def test_database_outage_over_tls(tls_pair:'SchedulerPair', outage_seconds:'int') -> 'None':
    """ The same outage with server A connected to the shared database over TLS.
    """
    _run_database_outage(tls_pair, outage_seconds)

# ################################################################################################################################
# ################################################################################################################################
