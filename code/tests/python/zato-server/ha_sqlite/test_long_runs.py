# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The long runs - one hour of takeovers every four minutes, each followed by a rejoin, and one hour of steady traffic.
# Both runs publish paced traffic, report every minute, stop at the first minute that exceeds a bound, and end
# with the checks of every run, the bounds of the resources and the WAL, and the replication lag at zero.

# stdlib
import logging
import time

# Zato
from ha_checks import check_copies, check_publications_stored, check_scheduler, check_workload
from ha_long_run import check_replacements, ModuleCtx as LongRunCtx, run_repeated_failover, start_traffic, \
    stop_traffic, wait_until
from ha_soak import get_bound_violations, wait_for_zero_lag

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from ha_soak import MinuteReporter
    from ha_traffic import TimedPublisher
    from nodes import Node
    from workload import Workload

    MinuteReporter = MinuteReporter
    TimedPublisher = TimedPublisher
    Workload = Workload

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_sqlite.long_runs')

# ################################################################################################################################
# ################################################################################################################################

def _finish(
    env:'HAEnvironment',
    workload:'Workload',
    publisher:'TimedPublisher',
    reporter:'MinuteReporter',
    unrun_claims:'int'=0,
) -> 'Node':
    """ Stops the traffic and the reports and applies the checks of every run, the bounds and the replication lag.
    Each job may count the given number of claims that a failed active node did not run.
    """
    active = stop_traffic(env, publisher, reporter)

    violations = get_bound_violations(reporter.reports)
    assert not violations, violations

    check_workload(env, workload)
    check_publications_stored(env, active, publisher.get_msg_ids())

    wait_for_zero_lag(active)

    _ = check_scheduler(env, active, unrun_claims)
    check_copies(env, active)

    return active

# ################################################################################################################################
# ################################################################################################################################

def test_repeated_failover(ha_pair:'HAEnvironment') -> 'None':
    """ The active node fails every four minutes for one hour with each fault of the takeover suite in turn,
    and its standby takes over each time while the former active node joins again.
    """
    env = ha_pair
    workload, publisher, reporter = start_traffic(env)

    replacements = run_repeated_failover(env, workload, reporter)

    # Each failed active node may leave the claim it committed before the run began without a run.
    _ = _finish(env, workload, publisher, reporter, len(replacements))
    check_replacements(env, replacements)

# ################################################################################################################################

def test_soak(ha_pair:'HAEnvironment') -> 'None':
    """ One hour of steady traffic, with the resources of both containers and the WAL of each database within
    their bounds and the replication lag at zero once the traffic stops.
    """
    env = ha_pair
    workload, publisher, reporter = start_traffic(env)

    wait_until(reporter, time.monotonic() + LongRunCtx.Duration_Seconds)

    _ = _finish(env, workload, publisher, reporter)

# ################################################################################################################################
# ################################################################################################################################
