# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from pubsub_rest.monitor import Limits
from pubsub_rest.runner import get_duration, run_for
from pubsub_rest.suite import TrafficRun
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.server import PubSubServer

# ################################################################################################################################
# ################################################################################################################################

# How long the soak runs, in seconds, unless Zato_Test_Soak_Seconds says otherwise.
_soak_seconds = 2 * 60 * 60

# The minute after the warm-up, whose resources the last minute is compared with.
_baseline_minute = 5

# How long the backlog may take to drain after the API clients stop, in seconds.
_drain_seconds = 600

# ################################################################################################################################
# ################################################################################################################################

@pytest.mark.soak
def test_soak(server:'PubSubServer') -> 'None':
    """ Steady production traffic for two hours. Every minute must stay within the p99 limits, the table sizes
    that the retention bounds, the WAL and the pace of autovacuum, and the resources of the server must remain bounded.
    """
    duration = get_duration('Zato_Test_Soak_Seconds', _soak_seconds)
    drain_seconds = get_duration('Zato_Test_Drain_Seconds', _drain_seconds)

    measurement = start_measurement(server.get_client(), server.get_database())
    run = TrafficRun(server, Limits())

    try:
        run.start()
        run_for(run.monitor, duration)
        drained_seconds = run.drain(drain_seconds)

    finally:
        run.stop()

    figures = run.get_figures({'duration_seconds': duration, 'drain_seconds': drained_seconds})
    _ = report_result(measurement, 'pubsub-soak', figures)

    monitor = run.monitor

    assert not monitor.is_disk_low, 'The run stopped because the disk ran low'
    assert not monitor.get_failures(), monitor.get_failures()
    assert not monitor.get_resource_growth(_baseline_minute), monitor.get_resource_growth(_baseline_minute)
    assert not server.get_count_mismatches(), server.get_count_mismatches()

# ################################################################################################################################
# ################################################################################################################################
