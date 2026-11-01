# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One fault at one severity level during the production traffic - a baseline, the fault, a bounded recovery
# and the minutes after it, which are checked as in the soak, followed by the account of every publication.

# stdlib
from dataclasses import dataclass
from time import monotonic

# gevent
from gevent import sleep

# SQLAlchemy
from sqlalchemy import text

# Zato
from expiration import ExpirationProbe, is_probe_enabled
from monitor import Limits, Monitor
from runner import get_count_mismatches, get_duration, get_report_path, run_for, start_cleanup_process, \
    stop_cleanup_process
from traffic import get_traffic_profile, Traffic
from zato.common.pubsub.sql.config import get_pubsub_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from faults import Fault
    from zato.common.typing_ import strlist

    intpair = tuple[int, int]
    process = Popen[bytes]

# ################################################################################################################################
# ################################################################################################################################

# How long each phase of a run lasts, in seconds, unless the variables of the same names say otherwise -
# the baseline, the fault, the recovery, during which the latency may still exceed its limits, and the minutes
# after it, of which at least one is checked in full.
_baseline_seconds = 60
_fault_seconds = 120
_recovery_seconds = 120
_checked_seconds = 120

# How long the backlog may take to drain once the API clients stop, and how often it is checked, in seconds.
_drain_seconds = 900
_drain_check_seconds = 1

# How often the cleanup process sweeps, in seconds.
_cleanup_interval_seconds = 60

# How many deliveries are left in the queues.
_delivery_rows_query = text('select count(*) from pubsub_delivery')

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class FaultOutcome:
    """ The account of the publications of one run.
    """
    acknowledged_partner: 'int'
    acknowledged_broadcast: 'int'
    not_pulled: 'int'
    not_pushed: 'int'
    repeated_pushes: 'int'
    delivery_rows: 'int'
    publish_errors: 'int'
    drain_seconds: 'float'

# ################################################################################################################################
# ################################################################################################################################

def _count_delivery_rows() -> 'int':
    with get_pubsub_engine().connect() as connection:
        out = connection.execute(_delivery_rows_query).scalar_one()
    return out

# ################################################################################################################################
# ################################################################################################################################

class FaultRun:
    """ Runs the traffic of one test through the phases of one fault and accounts for every publication.
    """

    def __init__(self, label:'str') -> 'None':
        self.label = label

        self.traffic = Traffic(get_traffic_profile())
        self.traffic.tracks_deliveries = True

        self.monitor:'Monitor | None' = None
        self.cleanup:'process | None' = None
        self.outcome = FaultOutcome()

        # Whether the cleanup process was still running at the end, and how many minutes were reported
        # by the time the recovery ended.
        self.is_cleanup_running = False
        self.recovered_report_count = 0

        # The expirations of the messages published during a fault of the clock of the server.
        self.probe:'ExpirationProbe | None' = None

        if is_probe_enabled():
            self.probe = ExpirationProbe(self.traffic.backend)

# ################################################################################################################################

    def get_cleanup_pid(self) -> 'int':
        cleanup = self.cleanup
        assert cleanup is not None, 'The cleanup process is not running'
        out = cleanup.pid
        return out

# ################################################################################################################################

    def _mark_fault_minute(self, elapsed:'float') -> 'None':
        """ The minutes that a fault or its recovery overlap report the latency and the errors without failing on them.
        """
        monitor = self.monitor
        assert monitor is not None

        monitor.is_minute_exempt = True
        monitor.allows_errors = True

# ################################################################################################################################

    def _get_missing(self) -> 'intpair':
        """ How many acknowledged partner messages were not pulled and how many acknowledged broadcasts
        were not pushed to every subscriber.
        """
        traffic = self.traffic
        subscriber_count = len(traffic.broadcast_sub_keys)

        with traffic.lock:
            not_pulled = len(traffic.acknowledged_partner_msg_ids - traffic.pulled_msg_ids)

            not_pushed = 0
            for key in traffic.acknowledged_broadcast_keys:
                if traffic.pushed_broadcast_keys[key] < subscriber_count:
                    not_pushed += 1

        out = not_pulled, not_pushed
        return out

# ################################################################################################################################

    def _drain(self) -> 'None':
        """ Waits until every acknowledged publication was delivered and the queues are empty, or until the time runs out.
        """
        drain_seconds = get_duration('Zato_Test_Fault_Drain_Seconds', _drain_seconds)

        start = monotonic()
        deadline = start + drain_seconds

        while True:

            not_pulled, not_pushed = self._get_missing()
            delivery_rows = _count_delivery_rows()

            # Everything was delivered once nothing is missing and the queues are empty ..
            if not_pulled == 0:
                if not_pushed == 0:
                    if delivery_rows == 0:
                        break

            # .. or the time ran out, which the checks report.
            if monotonic() >= deadline:
                break

            sleep(_drain_check_seconds)

        traffic = self.traffic
        repeated_pushes = 0

        for count in traffic.pushed_broadcast_keys.values():
            repeated_pushes += count - len(traffic.broadcast_sub_keys)

        self.outcome.acknowledged_partner = len(traffic.acknowledged_partner_msg_ids)
        self.outcome.acknowledged_broadcast = len(traffic.acknowledged_broadcast_keys)
        self.outcome.not_pulled = not_pulled
        self.outcome.not_pushed = not_pushed
        self.outcome.repeated_pushes = max(repeated_pushes, 0)
        self.outcome.delivery_rows = delivery_rows
        self.outcome.publish_errors = traffic.total_errors
        self.outcome.drain_seconds = round(monotonic() - start, 1)

# ################################################################################################################################

    def run(self, fault:'Fault', level:'int') -> 'None':
        """ Runs the phases of one fault at one severity level, removing the fault even if a phase fails.
        """
        baseline_seconds = get_duration('Zato_Test_Fault_Baseline_Seconds', _baseline_seconds)
        fault_seconds = get_duration('Zato_Test_Fault_Seconds', _fault_seconds)
        recovery_seconds = get_duration('Zato_Test_Fault_Recovery_Seconds', _recovery_seconds)
        checked_seconds = get_duration('Zato_Test_Fault_Checked_Seconds', _checked_seconds)

        fault_seconds = max(fault_seconds, fault.min_duration)

        traffic = self.traffic
        traffic.backend.take_over()
        traffic.subscribe_all()

        probe = self.probe

        if probe:
            probe.subscribe()

        cleanup = start_cleanup_process(_cleanup_interval_seconds)
        monitor = Monitor(traffic, Limits(), get_report_path(f'fault-{fault.name}'), self.label)

        self.cleanup = cleanup
        self.monitor = monitor

        try:
            traffic.start()
            monitor.start()

            # What the resource is without the fault ..
            fault.start_baseline()
            run_for(monitor, baseline_seconds)
            fault.end_baseline()

            # .. the fault itself, removed in any case ..
            try:
                fault.apply(level)

                if probe:
                    probe.start()

                run_for(monitor, fault_seconds, on_tick=self._mark_fault_minute)
            finally:
                fault.remove()

            # .. the recovery, during which the latency may still exceed its limits ..
            run_for(monitor, recovery_seconds, on_tick=self._mark_fault_minute)
            self.recovered_report_count = len(monitor.reports)

            # .. the minutes after it, checked in full ..
            run_for(monitor, checked_seconds)

            if probe:
                probe.wait()

            # .. and the account of every publication.
            traffic.stop_publishing()
            monitor.checks_rate = False
            self._drain()

            self.is_cleanup_running = cleanup.poll() is None

        finally:
            fault.remove()
            monitor.stop()
            traffic.stop()
            stop_cleanup_process(cleanup)

            # The guard of this run is detached, so that the next run of the same engine installs its own.
            guard = traffic.backend.generation_guard
            if guard:
                guard.uninstall(traffic.backend.engine)

        self._write_outcome()

# ################################################################################################################################

    def _write_outcome(self) -> 'None':
        monitor = self.monitor
        assert monitor is not None

        outcome = self.outcome

        line = f'{self.label} | outcome | partner {outcome.acknowledged_partner}, not pulled {outcome.not_pulled} | ' + \
            f'broadcast {outcome.acknowledged_broadcast}, not pushed {outcome.not_pushed}, ' + \
            f'repeated pushes {outcome.repeated_pushes} | rows left {outcome.delivery_rows} | ' + \
            f'publish errors {outcome.publish_errors} | drained in {outcome.drain_seconds}s'

        with open(monitor.report_path, 'a') as report_file:
            _ = report_file.write(line + '\n')

        print(line, flush=True)

# ################################################################################################################################

    def check(self) -> 'None':
        """ Item 15.15 - nothing acknowledged is lost, the counts equal the raw rows, no process needed a restart,
        the server remains the active one and the latency returned to its limits once the fault was removed.
        """
        monitor = self.monitor
        assert monitor is not None

        outcome = self.outcome
        backend = self.traffic.backend

        assert outcome.not_pulled == 0, outcome
        assert outcome.not_pushed == 0, outcome
        assert outcome.delivery_rows == 0, outcome

        assert not get_count_mismatches(), get_count_mismatches()
        assert self.is_cleanup_running, 'The cleanup process stopped during the run'
        assert not backend.is_replaced, 'The server was replaced during the run'

        # At least one minute after the recovery is checked in full ..
        checked:'strlist' = []

        for report in monitor.reports[self.recovered_report_count:]:
            if not report.is_exempt:
                checked.append(report.since_start)

        assert checked, 'No minute after the recovery was checked in full'

        # .. no minute failed, apart from the exempt ones, which report what the fault caused ..
        assert not monitor.get_failures(), monitor.get_failures()

        # .. and the messages published during a fault of the clock expired on time.
        probe = self.probe

        if probe:
            probe.check()

# ################################################################################################################################
# ################################################################################################################################
