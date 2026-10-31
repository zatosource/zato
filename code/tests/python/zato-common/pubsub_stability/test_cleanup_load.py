# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from time import monotonic

# gevent
from gevent import get_hub, sleep, spawn

# SQLAlchemy
from sqlalchemy import text

# Zato
from monitor import Limits, Monitor
from runner import get_count_mismatches, get_duration, get_report_path, run_for, start_cleanup_process, \
    stop_cleanup_process
from seeding import connect_native, seed_aged_queue
from traffic import get_traffic_profile, Traffic
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.pubsub.sql.config import get_pubsub_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from subprocess import Popen
    from zato.common.typing_ import anylist, strlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

# How many delivered-message traces past their retention the cleanup removes during the traffic,
# unless Zato_Test_Retention_Messages says otherwise.
_trace_count = 5_000_000

# How old the traces are, which is past the retention by age.
_trace_age_days = 30

# The topic the traces belong to.
_trace_topic = 'stability.retention'

# How many times the cleanup process is killed in the middle of a sweep, and what part of the traces
# each of its lives removes before it is killed.
_kill_count = 3
_kill_after_ratio = 0.1

# How long the cleanup process stays down after it was killed, in seconds.
_restart_delay_seconds = 5

# How long another transaction holds locks during a sweep, in seconds. On PostgreSQL these are row locks on traces.
# On SQLite it is the write lock of the database, which every writer waits for up to the busy timeout of 5 seconds,
# so the hold is shorter than that.
_postgresql_lock_seconds = 60
_sqlite_lock_seconds = 2

# How many traces the other transaction locks on PostgreSQL.
_locked_trace_count = 10_000

# How long the traces may take to be removed in all, in seconds.
_retention_seconds = 60 * 60

# How often the traces are counted, in seconds.
_count_interval_seconds = 10

# How often the cleanup process sweeps, in seconds.
_cleanup_interval_seconds = 60

# How long the backlog of the traffic may take to drain after the API clients stop, in seconds.
_drain_seconds = 600

_trace_count_query = text('select count(*) from pubsub_message where topic_name = :topic_name')

# ################################################################################################################################
# ################################################################################################################################

def _count_traces() -> 'int':
    with get_pubsub_engine().connect() as connection:
        out = connection.execute(_trace_count_query, {'topic_name': _trace_topic}).scalar_one()
    return out

# ################################################################################################################################

def _hold_locks(is_postgresql:'bool') -> 'None':
    """ Holds locks that a sweep meets, in a thread of its own so that the traffic keeps running.
    """
    connection, placeholder = connect_native()
    cursor = connection.cursor()

    if is_postgresql:
        _ = cursor.execute(
            f'select id from pubsub_message where topic_name = {placeholder} order by id limit {_locked_trace_count} for update',
            (_trace_topic,))
        hold_seconds = _postgresql_lock_seconds
    else:
        _ = cursor.execute('begin immediate')
        hold_seconds = _sqlite_lock_seconds

    time.sleep(hold_seconds)

    connection.rollback()
    connection.close()

# ################################################################################################################################
# ################################################################################################################################

class _CleanupChaos:
    """ Kills the cleanup process in the middle of its sweeps and starts it again, then makes a sweep meet locks.
    """
    def __init__(self) -> 'None':
        self.is_postgresql = get_pubsub_engine().dialect.name == Type_PostgreSQL

        self.process:'Popen[bytes]' = start_cleanup_process(_cleanup_interval_seconds)
        self.kills = 0
        self.is_locked = False
        self.lock_greenlets:'anylist' = []

        self.initial = _count_traces()
        self.removed_at_start = self.initial

        self.log:'strlist' = []

    def _hold_locks(self, count:'int') -> 'None':
        self.is_locked = True
        self.log.append(f'Locks held with {count} traces left')

        threadpool = get_hub().threadpool
        self.lock_greenlets.append(spawn(threadpool.apply, _hold_locks, (self.is_postgresql,)))

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

                self.process = start_cleanup_process(_cleanup_interval_seconds)
                self.removed_at_start = count

# ################################################################################################################################
# ################################################################################################################################

def test_cleanup_load(stability_env:'strstrdict') -> 'None':
    """ Retention sweeps of millions of traces run during the traffic, with the cleanup process killed and started
    again in the middle of its sweeps and with its sweeps meeting locks of other transactions. Every trace is removed,
    the traffic stays within its limits and the counts equal the rows.
    """
    trace_count = get_duration('Zato_Test_Retention_Messages', _trace_count)

    seed_seconds = seed_aged_queue(
        topic_name=_trace_topic,
        sub_keys=[],
        delivery_sub_keys=[],
        message_count=trace_count,
        aged_days=_trace_age_days,
        is_delivered=True,
    )
    print(f'Seeded {trace_count} traces in {seed_seconds:.0f}s', flush=True)

    traffic = Traffic(get_traffic_profile())
    traffic.backend.take_over()
    traffic.subscribe_all()

    monitor = Monitor(traffic, Limits(max_message_rows=trace_count * 2), get_report_path('cleanup-load'), 'cleanup-load')

    traffic.start()
    monitor.start()

    chaos = _CleanupChaos()
    started = monotonic()

    def is_done() -> 'bool':
        count = _count_traces()
        chaos.on_count(count)
        out = count == 0
        return out

    try:
        run_for(monitor, _retention_seconds, is_done=is_done, is_done_interval=_count_interval_seconds)
        retention_seconds = monotonic() - started
        traces_left = _count_traces()

        traffic.stop_publishing()
        monitor.checks_rate = False
        _ = traffic.wait_until_drained(_drain_seconds)

    finally:
        monitor.stop()
        traffic.stop()
        chaos.release_locks()
        stop_cleanup_process(chaos.process)

    for line in chaos.log:
        print(line, flush=True)

    print(f'Removed {trace_count} traces in {retention_seconds:.0f}s', flush=True)

    assert not monitor.is_disk_low, 'The run stopped because the disk ran low'
    assert chaos.kills == _kill_count, chaos.log
    assert chaos.is_locked, chaos.log
    assert traces_left == 0, f'{traces_left} traces left after {_retention_seconds}s'
    assert not monitor.get_failures(), monitor.get_failures()
    assert not get_count_mismatches(), get_count_mismatches()

# ################################################################################################################################
# ################################################################################################################################
