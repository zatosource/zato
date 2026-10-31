# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# Zato
from monitor import Limits, Monitor
from runner import get_count_mismatches, get_duration, get_report_path, run_for, start_cleanup_process, \
    stop_cleanup_process
from traffic import get_traffic_profile, Traffic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# How long the suite runs, in seconds, unless Zato_Test_Peaks_Seconds says otherwise - three peaks.
_peaks_seconds = 30 * 60

# Each cycle is this long and its peak starts at this offset and lasts this long, in seconds.
_cycle_seconds = 10 * 60
_peak_offset_seconds = 2 * 60
_peak_seconds = 60

# How many times the steady rate a peak publishes at.
_peak_factor = 10

# How long the backlog of a peak may take to drain once the peak is over, in seconds.
_max_drain_seconds = 5 * 60

# The backlog counts as drained once it is back to this many times its size before the peak, plus the margin.
_drained_backlog_ratio = 2
_drained_backlog_margin = 1_000

# How long the remaining backlog may take to drain after the API clients stop, in seconds.
_final_drain_seconds = 600

# How often the cleanup process sweeps, in seconds.
_cleanup_interval_seconds = 60

# ################################################################################################################################
# ################################################################################################################################

class _PeakSchedule:
    """ Raises the rate for the peak of each cycle, lowers it afterwards and measures how long each backlog took to drain.
    """
    def __init__(self, traffic:'Traffic', monitor:'Monitor') -> 'None':
        self.traffic = traffic
        self.monitor = monitor
        self.steady_rate = traffic.rate

        self.is_peak = False
        self.is_draining = False
        self.backlog_before = 0
        self.drain_started = 0.0

        self.drain_seconds:'list[float]' = []
        self.failures:'strlist' = []

    def get_backlog(self) -> 'int':
        out = self.traffic.expected_deliveries() - self.traffic.delivered()
        return out

    def on_tick(self, elapsed:'float') -> 'None':

        position = elapsed % _cycle_seconds
        in_peak = _peak_offset_seconds <= position < _peak_offset_seconds + _peak_seconds

        # The peak begins ..
        if in_peak and not self.is_peak:
            self.is_peak = True
            self.backlog_before = self.get_backlog()
            self.traffic.set_rate(self.steady_rate * _peak_factor)

        # .. the peak ends and its backlog starts to drain ..
        elif self.is_peak and not in_peak:
            self.is_peak = False
            self.is_draining = True
            self.drain_started = monotonic()
            self.traffic.set_rate(self.steady_rate)

        # .. and once it drained, the steady limits apply again ..
        if self.is_draining:

            drained_backlog = self.backlog_before * _drained_backlog_ratio + _drained_backlog_margin
            draining_for = monotonic() - self.drain_started

            if self.get_backlog() <= drained_backlog:
                self.is_draining = False
                self.drain_seconds.append(draining_for)

            elif draining_for > _max_drain_seconds:
                self.is_draining = False
                self.failures.append(f'Backlog of {self.get_backlog()} not drained in {_max_drain_seconds}s')

        # .. so that each minute with any part of an overload in it is not held to the limits of the steady traffic.
        if self.is_peak or self.is_draining:
            self.monitor.is_minute_exempt = True

# ################################################################################################################################
# ################################################################################################################################

def test_peaks(stability_env:'strstrdict') -> 'None':
    """ Bursts of ten times the steady rate, one minute long, every ten minutes. Each backlog must drain
    within a fixed bound, after which the steady traffic is within its limits again.
    """
    duration = get_duration('Zato_Test_Peaks_Seconds', _peaks_seconds)

    traffic = Traffic(get_traffic_profile())
    traffic.backend.take_over()
    traffic.subscribe_all()

    cleanup = start_cleanup_process(_cleanup_interval_seconds)
    monitor = Monitor(traffic, Limits(), get_report_path('peaks'), 'peaks')
    schedule = _PeakSchedule(traffic, monitor)

    try:
        traffic.start()
        monitor.start()

        run_for(monitor, duration, schedule.on_tick)

        traffic.stop_publishing()
        monitor.checks_rate = False
        _ = traffic.wait_until_drained(_final_drain_seconds)

    finally:
        monitor.stop()
        traffic.stop()
        stop_cleanup_process(cleanup)

    print(f'Peak drain times: {schedule.drain_seconds}', flush=True)

    assert not monitor.is_disk_low, 'The run stopped because the disk ran low'
    assert schedule.drain_seconds, 'No peak completed'
    assert not schedule.failures, schedule.failures
    assert not monitor.get_failures(), monitor.get_failures()
    assert not get_count_mismatches(), get_count_mismatches()

# ################################################################################################################################
# ################################################################################################################################
