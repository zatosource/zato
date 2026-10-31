# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from monitor import Limits, Monitor
from runner import get_count_mismatches, get_duration, get_report_path, run_for, start_cleanup_process, \
    stop_cleanup_process
from traffic import get_traffic_profile, Traffic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strstrdict

# ################################################################################################################################
# ################################################################################################################################

# How long the soak runs, in seconds, unless Zato_Test_Soak_Seconds says otherwise.
_soak_seconds = 2 * 60 * 60

# The minute after the warm-up, whose resources the last minute is compared with.
_baseline_minute = 5

# How long the backlog may take to drain after the API clients stop, in seconds.
_drain_seconds = 600

# How often the cleanup process sweeps, in seconds.
_cleanup_interval_seconds = 60

# ################################################################################################################################
# ################################################################################################################################

def test_soak(stability_env:'strstrdict') -> 'None':
    """ Steady production traffic for two hours. Every minute must stay within the p99 limits, the table sizes
    that the retention bounds, the WAL and the pace of autovacuum, and the resources of the process must remain bounded.
    """
    duration = get_duration('Zato_Test_Soak_Seconds', _soak_seconds)
    drain_seconds = get_duration('Zato_Test_Drain_Seconds', _drain_seconds)

    traffic = Traffic(get_traffic_profile())
    traffic.backend.take_over()
    traffic.subscribe_all()

    cleanup = start_cleanup_process(_cleanup_interval_seconds)
    monitor = Monitor(traffic, Limits(), get_report_path('soak'), 'soak')

    try:
        traffic.start()
        monitor.start()

        run_for(monitor, duration)

        traffic.stop_publishing()
        monitor.checks_rate = False
        _ = traffic.wait_until_drained(drain_seconds)

    finally:
        monitor.stop()
        traffic.stop()
        stop_cleanup_process(cleanup)

    assert not monitor.is_disk_low, 'The run stopped because the disk ran low'
    assert not monitor.get_failures(), monitor.get_failures()
    assert not monitor.get_resource_growth(_baseline_minute), monitor.get_resource_growth(_baseline_minute)
    assert not get_count_mismatches(), get_count_mismatches()

# ################################################################################################################################
# ################################################################################################################################
