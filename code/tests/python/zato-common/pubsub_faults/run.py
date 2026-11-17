# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One fault at one severity level during the production traffic of a server - a baseline, the fault, a bounded recovery
# and the minutes after it, which are checked as in the soak, followed by the account of every publication.

# stdlib
import logging
from dataclasses import asdict, dataclass
from time import monotonic
from typing import NamedTuple

# gevent
from gevent import sleep, spawn

# Zato
from pubsub_rest.monitor import Limits, Monitor
from pubsub_rest.runner import get_duration, run_for, start_cleanup_process, stop_cleanup_process

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from expiration import ExpirationProbe
    from faults import Fault
    from process_faults import Scope
    from pubsub_rest.server import PubSubServer
    from zato.common.typing_ import strlist, strstrdict

    intpair = tuple[int, int]
    process = Popen[bytes]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_faults')

# ################################################################################################################################
# ################################################################################################################################

class FaultPhases(NamedTuple):
    """ How long each phase of a run lasts, in seconds - the baseline, the fault, the recovery, during which the latency
    may still exceed its limits, and the minutes after it, of which at least one is checked in full.
    """
    baseline_seconds: 'int'
    fault_seconds: 'int'
    recovery_seconds: 'int'
    checked_seconds: 'int'

# ################################################################################################################################
# ################################################################################################################################

# The phases of a run unless the Zato_Test_Fault_* variables say otherwise. The fault lasts longer than the detection
# of a dead connection, three pull leases, one cleanup sweep and the late pull of the expiration probe.
Default_Phases = FaultPhases(
    baseline_seconds=30,
    fault_seconds=90,
    recovery_seconds=120,
    checked_seconds=60,
)

# How long the backlog may take to drain once the API clients stop, and how often it is checked, in seconds.
_drain_seconds = 900
_drain_check_seconds = 1

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

class FaultRun:
    """ Runs the traffic of one server through the phases of one fault and accounts for every publication.
    """

    def __init__(
        self,
        server:'PubSubServer',
        label:'str',
        phases:'FaultPhases'=Default_Phases,
        probes_expiration:'bool'=False,
        cleanup_env:'strstrdict | None'=None,
        ) -> 'None':

        self.server = server
        self.label = label
        self.phases = phases

        self.traffic = server.get_traffic()

        self.monitor:'Monitor | None' = None
        self.cleanup:'process | None' = None
        self.outcome = FaultOutcome()

        # The variables that the cleanup process runs with in addition to those of the server,
        # and the scope of the server, which the cleanup process runs in as well, if the server runs in one.
        self.cleanup_env = cleanup_env
        self.scope:'Scope | None' = server.properties['scope']

        # Whether the cleanup process was still running at the end, and how many minutes were reported
        # by the time the recovery ended.
        self.is_cleanup_running = False
        self.recovered_report_count = 0

        # The expirations of the messages published during a fault of the clock of the server.
        self.probe:'ExpirationProbe | None' = None

        if probes_expiration:
            self.probe = server.properties['probe']

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

    def _apply_fault(self, fault:'Fault', level:'int') -> 'None':
        """ Applies a fault, marking each minute that its application overlaps, because a fault such as a restart
        of the database keeps the database unavailable for as long as it is being applied.
        """
        applying = spawn(fault.apply, level)

        # Each minute that ends while the fault is being applied reports what the fault caused ..
        while not applying.ready():
            self._mark_fault_minute(0)
            sleep(1)

        # .. and an exception raised by the fault propagates to the run.
        _ = applying.get()

# ################################################################################################################################

    def _get_missing(self) -> 'intpair':
        """ How many acknowledged partner messages were not pulled and how many acknowledged broadcasts
        were not pushed to every subscriber.
        """
        traffic = self.traffic
        subscriber_count = len(traffic.broadcast_sub_keys)

        with traffic.lock:
            not_pulled = len(traffic.unpulled_partner_msg_ids)

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
            delivery_rows = self.server.get_delivery_count()

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

        self.outcome.acknowledged_partner = traffic.acknowledged_partner_count
        self.outcome.acknowledged_broadcast = len(traffic.acknowledged_broadcast_keys)
        self.outcome.not_pulled = not_pulled
        self.outcome.not_pushed = not_pushed
        self.outcome.repeated_pushes = max(repeated_pushes, 0)
        self.outcome.delivery_rows = delivery_rows
        self.outcome.publish_errors = traffic.total_errors
        self.outcome.drain_seconds = round(monotonic() - start, 1)

# ################################################################################################################################

    def _start_cleanup(self) -> 'process':
        """ Starts the cleanup process, in the scope of the server if the server runs in one.
        """
        out = start_cleanup_process(self.cleanup_env)

        if self.scope:
            self.scope.add_pid(out.pid)

        return out

# ################################################################################################################################

    def run(self, fault:'Fault', level:'int') -> 'None':
        """ Runs the phases of one fault at one severity level, removing the fault even if a phase fails.
        """
        phases = self.phases

        baseline_seconds = get_duration('Zato_Test_Fault_Baseline_Seconds', phases.baseline_seconds)
        fault_seconds = get_duration('Zato_Test_Fault_Seconds', phases.fault_seconds)
        recovery_seconds = get_duration('Zato_Test_Fault_Recovery_Seconds', phases.recovery_seconds)
        checked_seconds = get_duration('Zato_Test_Fault_Checked_Seconds', phases.checked_seconds)

        fault_seconds = max(fault_seconds, fault.min_duration)

        traffic = self.traffic
        probe = self.probe

        cleanup = self._start_cleanup()
        monitor = Monitor(self.server, traffic, Limits())

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
                self._apply_fault(fault, level)

                if probe:
                    probe.start()

                run_for(monitor, fault_seconds, on_tick=self._mark_fault_minute)
            finally:
                fault.remove()

            # .. the recovery, during which the latency may still exceed its limits, whose last minute ends with it,
            # so that the minutes after it start on a grid of their own ..
            run_for(monitor, recovery_seconds, on_tick=self._mark_fault_minute)
            monitor.end_minute()
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

        logger.info('%s -> %s', self.label, asdict(self.outcome))

# ################################################################################################################################

    def check(self) -> 'None':
        """ Item 15.15 - nothing acknowledged is lost, the counts equal the raw rows, no process needed a restart,
        the server remains the active one and the latency returned to its limits once the fault was removed.
        """
        monitor = self.monitor
        assert monitor is not None

        outcome = self.outcome
        server = self.server

        assert outcome.not_pulled == 0, outcome
        assert outcome.not_pushed == 0, outcome
        assert outcome.delivery_rows == 0, outcome

        assert not server.get_count_mismatches(), server.get_count_mismatches()
        assert self.is_cleanup_running, 'The cleanup process stopped during the run'
        assert not server.is_replaced(), 'The server was replaced during the run'

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
