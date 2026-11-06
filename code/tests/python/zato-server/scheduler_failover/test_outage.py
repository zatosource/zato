# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared database is unavailable for a time, during which the active server skips its slots and after which
# it continues as the active server, and a server whose common database is not the pub/sub database does not start.

# stdlib
import time

# pytest
import pytest

# Zato
from checks import check_run_log, get_starts, ModuleCtx as ChecksCtx, read_run_log, read_skip_counts, wait_for_starts
from failover import create_container, docker, read_generation
from pair import start_server, stop_server
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
_outage_seconds = [10, 120]

# How long a server whose configuration is refused may take to report it, in seconds.
_refusal_timeout_seconds = 120

# How often the log of a server is read while a test waits for the refusal, in seconds.
_poll_seconds = 1.0

# The name of a database other than the pub/sub one.
_other_db_name = 'zato_common_other'

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.parametrize('outage_seconds', _outage_seconds)
def test_database_outage(pair:'SchedulerPair', outage_seconds:'int') -> 'None':
    """ The shared database stops for a time, server A skips each slot due in the meantime as not active,
    begins no run, and continues as the active server once the database returns.
    """
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

def _read_container_logs(container_name:'str') -> 'str':
    result = docker('logs', container_name, check=False)
    out = result.stdout + result.stderr
    return out

# ################################################################################################################################

def test_refused_configuration(pair:'SchedulerPair') -> 'None':
    """ Server B, whose common database on PostgreSQL is not the pub/sub database, does not take over,
    its log names both databases, and server A remains the active server.
    """
    database = pair.database
    server_b = pair.b.server

    _ = wait_for_starts(pair, ChecksCtx.Job_Every_Second, 'a', _runs_around_outage, _runs_timeout_seconds)
    generation = read_generation(database)

    # Server B points its common database at another database on the same PostgreSQL ..
    for name, value in list(server_b.env.items()):
        if name.startswith('Zato_PubSub_DB_'):
            common_name = name.replace('Zato_PubSub_DB_', 'Zato_Common_DB_')
            server_b.env[common_name] = value

    server_b.env['Zato_Common_DB_Name'] = _other_db_name
    create_container(server_b)

    # .. and it starts ..
    start_server(pair.b)

    pubsub_db_name = server_b.env['Zato_PubSub_DB_Name']
    expected = [f'/{_other_db_name}`', f'/{pubsub_db_name}`']

    deadline = time.monotonic() + _refusal_timeout_seconds

    while True:
        logs = _read_container_logs(server_b.container_name)

        if 'must be the pub/sub database' in logs:
            break

        if time.monotonic() > deadline:
            raise Exception(f'Server B did not refuse its configuration in {_refusal_timeout_seconds}s:\n{logs[-5000:]}')

        time.sleep(_poll_seconds)

    # .. its log names both databases ..
    for name in expected:
        assert name in logs, name

    # .. and server A is still the active server, running its jobs.
    assert read_generation(database) == generation

    before = get_starts(read_run_log(pair), ChecksCtx.Job_Every_Second, 'a')
    _ = wait_for_starts(pair, ChecksCtx.Job_Every_Second, 'a', len(before) + _runs_around_outage, _runs_timeout_seconds)

    stop_server(pair.b)
    stop_server(pair.a)

    entries = check_run_log(pair)
    assert not get_starts(entries, server_label='b')

# ################################################################################################################################
# ################################################################################################################################
