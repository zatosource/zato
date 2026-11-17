# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The long runs on the database both nodes share - one takeover with each fault of the takeover suite, each followed
# by a rejoin, and one hour of steady traffic. Both runs publish paced traffic, report every minute, stop at the first minute
# that exceeds a bound, and end with the checks of every run and the bounds of the resources.

# stdlib
import logging
import time

# pytest
import pytest

# Zato
from ha_checks import check_publications_stored, check_scheduler, check_workload
from ha_long_run import check_replacements, ModuleCtx as LongRunCtx, run_repeated_failover, start_traffic, \
    stop_traffic, wait_until
from ha_soak import get_bound_violations, get_report_figures
from postgresql_checks import check_active_server
from zato.common.test.client import AdminClient
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment, HASession
    from nodes import Node
    from ha_soak import MinuteReporter
    from ha_traffic import TimedPublisher
    from workload import Workload

    MinuteReporter = MinuteReporter
    TimedPublisher = TimedPublisher
    Workload = Workload

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_postgresql.long_runs')

# ################################################################################################################################
# ################################################################################################################################

def _finish(
    env:'HAEnvironment',
    workload:'Workload',
    publisher:'TimedPublisher',
    reporter:'MinuteReporter',
    unrun_claims:'int'=0,
) -> 'Node':
    """ Stops the traffic and the reports and applies the checks of every run and the bounds.
    Each job may count the given number of claims that a failed active node did not run.
    """
    active = stop_traffic(env, publisher, reporter)

    violations = get_bound_violations(reporter.reports)
    assert not violations, violations

    check_workload(env, workload)
    check_publications_stored(env, active, publisher.get_msg_ids())

    _ = check_scheduler(env, active, unrun_claims)
    check_active_server(env, active)

    return active

# ################################################################################################################################
# ################################################################################################################################

def test_repeated_failover(ha_pair:'HAEnvironment') -> 'None':
    """ The active node fails once with each fault of the takeover suite in turn, and its standby takes over
    each time while the former active node joins again.
    """
    env = ha_pair
    workload, publisher, reporter = start_traffic(env)

    replacements = run_repeated_failover(env, workload, reporter)

    # Each failed active node may leave the claim it committed before the run began without a run.
    _ = _finish(env, workload, publisher, reporter, len(replacements))
    check_replacements(env, replacements)

# ################################################################################################################################

@pytest.mark.soak
def test_soak(ha_session:'HASession', ha_production_pair:'HAEnvironment') -> 'None':
    """ One hour of steady traffic on a pair with the settings of a production installation, with the resources
    of both containers within their bounds. The figures of each minute are recorded with the settings
    of the active node and of the database that both nodes share.
    """
    env = ha_production_pair

    measured = env.wait_for_pair(LongRunCtx.Recovery_Timeout)
    client = AdminClient(measured.server_url, ha_session.invoke_password)
    measurement = start_measurement(client, env.database)

    workload, publisher, reporter = start_traffic(env)

    wait_until(reporter, time.monotonic() + LongRunCtx.Duration_Seconds)

    active = _finish(env, workload, publisher, reporter)
    assert active is measured, (active.node_name, measured.node_name)

    _ = report_result(measurement, 'ha-postgresql-soak', {'minutes': get_report_figures(reporter.reports)})

# ################################################################################################################################
# ################################################################################################################################
