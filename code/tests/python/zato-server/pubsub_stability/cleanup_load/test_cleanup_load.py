# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from pubsub_rest.monitor import Limits
from pubsub_rest.runner import run_for, start_cleanup_process, stop_cleanup_process
from pubsub_rest.suite import TrafficRun
from zato.common.test.perf_report import report_result, start_measurement

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from pubsub_rest.server import PubSubServer
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# How many times the cleanup process is killed in the middle of a sweep, and what part of the traces
# each of its lives removes before it is killed.
_kill_count = 2
_kill_after_ratio = 0.1

# How long the cleanup process stays down after it was killed, in seconds.
_restart_delay_seconds = 5

# How long another transaction holds locks during a sweep, in seconds. On PostgreSQL these are row locks on traces,
# held for less than the idle in transaction timeout of 60 seconds after which the server ends the session.
# On SQLite it is the write lock of the database, which the publications of the traffic wait for as well,
# so the hold is shorter than the limit of the publish p99 of one second.
_postgresql_lock_seconds = 10
_sqlite_lock_seconds = 0.5

# How many traces the other transaction locks on PostgreSQL.
_locked_trace_count = 10_000

# How long the traces may take to be removed in all, in seconds.
_retention_seconds = 60 * 60

# How often the traces are counted, in seconds.
_count_interval_seconds = 0.5

# How long the backlog of the traffic may take to drain after the API clients stop, in seconds.
_drain_seconds = 600

# ################################################################################################################################
# ################################################################################################################################

class _CleanupChaos:
    """ Kills the cleanup process in the middle of its sweeps and starts it again, then makes a sweep meet locks.
    """
    def __init__(self, server:'PubSubServer') -> 'None':
        self.server = server
        self.trace_topic = server.properties['trace_topic']

        if server.get_database_statistics()['is_postgresql']:
            self.lock_seconds = _postgresql_lock_seconds
        else:
            self.lock_seconds = _sqlite_lock_seconds

        self.process:'Popen[bytes]' = start_cleanup_process()
        self.kills = 0
        self.is_locked = False
        self.lock_greenlets:'anylist' = []

        self.initial = self.count_traces()
        self.removed_at_start = self.initial

        # The previous count of the traces and when it was taken, from which the rate of their removal is computed.
        self.last_count = self.initial
        self.last_count_time = monotonic()

        self.log:'strlist' = []

    def report_progress(self, count:'int') -> 'None':
        """ Logs how many traces were removed and how many are left, and the rate of their removal since the previous count.
        """
        now = monotonic()
        rate = (self.last_count - count) / (now - self.last_count_time)
        removed = self.initial - count

        logger.info('Cleanup -> removed %d of %d traces, %d left, %.0f traces/s, kills %d',
            removed, self.initial, count, rate, self.kills)

        self.last_count = count
        self.last_count_time = now

    def count_traces(self) -> 'int':
        out = self.server.get_topic_rows(self.trace_topic)['messages']
        return out

    def _hold_locks(self, count:'int') -> 'None':
        self.is_locked = True
        self.log.append(f'Locks held with {count} traces left')

        greenlet = spawn(self.server.hold_locks, self.trace_topic, _locked_trace_count, self.lock_seconds)
        self.lock_greenlets.append(greenlet)

    def release_locks(self) -> 'None':
        for greenlet in self.lock_greenlets:
            _ = greenlet.get()

    def on_count(self, count:'int') -> 'None':

        # Each life of the process removes a part of the traces and is then killed in the middle of its sweep ..
        if self.kills < _kill_count:
            if self.removed_at_start - count >= self.initial * _kill_after_ratio:
                self.process.kill()
                _ = self.process.wait()
                self.kills += 1
                self.log.append(f'Killed the cleanup process with {count} traces left')

                # .. and the sweep of its last life starts while another transaction holds locks.
                if self.kills == _kill_count:
                    self._hold_locks(count)

                sleep(_restart_delay_seconds)

                self.process = start_cleanup_process()
                self.removed_at_start = count

# ################################################################################################################################
# ################################################################################################################################

def test_cleanup_load(server:'PubSubServer') -> 'None':
    """ Retention sweeps of millions of traces run during the traffic, with the cleanup process killed and started
    again in the middle of its sweeps and with its sweeps meeting locks of other transactions. Every trace is removed,
    the traffic stays within its limits and the counts equal the rows.
    """
    trace_count = server.properties['trace_count']

    measurement = start_measurement(server.get_client(), server.get_database())
    run = TrafficRun(server, Limits())

    run.monitor.limits.max_message_rows = trace_count * 2

    # The cleanup process of this suite is the one that its chaos kills and starts again.
    run.start(starts_cleanup=False)

    chaos = _CleanupChaos(server)
    started = monotonic()

    def is_done() -> 'bool':
        count = chaos.count_traces()
        chaos.report_progress(count)
        chaos.on_count(count)
        out = count == 0
        return out

    try:
        run_for(run.monitor, _retention_seconds, is_done=is_done, is_done_interval=_count_interval_seconds)
        retention_seconds = monotonic() - started
        traces_left = chaos.count_traces()

        drained_seconds = run.drain(_drain_seconds)

    finally:
        run.stop()
        chaos.release_locks()
        stop_cleanup_process(chaos.process)

    figures = run.get_figures({
        'trace_count': trace_count,
        'seed_seconds': server.properties['seed_seconds'],
        'retention_seconds': retention_seconds,
        'chaos': chaos.log,
        'drain_seconds': drained_seconds,
    })
    _ = report_result(measurement, 'pubsub-cleanup-load', figures)

    monitor = run.monitor

    assert not monitor.is_disk_low, 'The run stopped because the disk ran low'
    assert chaos.kills == _kill_count, chaos.log
    assert chaos.is_locked, chaos.log
    assert traces_left == 0, f'{traces_left} traces left after {_retention_seconds}s'
    assert not monitor.get_failures(), monitor.get_failures()
    assert not server.get_count_mismatches(), server.get_count_mismatches()

# ################################################################################################################################
# ################################################################################################################################
