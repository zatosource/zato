# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The per-minute measurement of the stability suites - rates, p99 latencies, table sizes, the WAL, autovacuum,
# the resources of the process and the free disk space, each minute checked against the limits of its suite.

# stdlib
import gc
import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from shutil import disk_usage
from tempfile import gettempdir
from time import monotonic
from types import FrameType

# gevent
from gevent import get_hub, sleep, spawn
from gevent.socket import socket as GeventSocket

# psutil
import psutil

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.db_env.common import Type_PostgreSQL
from zato.common.pubsub.sql.config import get_pubsub_db_path, get_pubsub_engine

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from traffic import MinuteCounters, Traffic
    from zato.common.typing_ import anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

# How long one measured interval lasts, in seconds.
Minute_Seconds = 60

# How long the last interval of a run must be for it to be reported, in seconds.
_min_final_interval_seconds = 1

# How often the event loop is probed for how late it resumes a sleeping greenlet, in seconds.
_loop_lag_interval = 0.1

# How often the drive of the runtime data is probed with a flush of one block of its own, in seconds,
# and the size of that block, in bytes.
_drive_probe_interval = 0.1
_drive_probe_block = b'\0' * 4096

# How many milliseconds one second has.
_ms_per_second = 1000

# How many bytes one gigabyte and one megabyte have.
_bytes_per_gb = 1024 ** 3
_bytes_per_mb = 1024 ** 2

# Below this much free space on the drive of the runtime data, a run stops.
_min_free_disk_gb = 20

# The tables whose sizes each minute reports.
_message_table = 'pubsub_message'
_delivery_table = 'pubsub_delivery'

# The PostgreSQL statistics of the two tables, the WAL and the background writer.
_pg_tables_query = text("""
    select relname, n_live_tup, n_dead_tup, autovacuum_count from pg_stat_user_tables
    where relname in ('pubsub_message', 'pubsub_delivery')
""")

# The environment variable that turns on the census of live objects, how many minutes pass between two censuses,
# how many object types with the largest growth each one reports, and for how many open sockets without a peer
# it reports what holds them.
_env_object_census = 'Zato_Test_Object_Census'
_object_census_minutes = 5
_object_census_types = 15
_object_census_sockets = 5

_pg_wal_query = text('select coalesce(sum(size), 0) from pg_ls_waldir()')
_pg_checkpoints_query = text('select checkpoints_timed + checkpoints_req from pg_stat_bgwriter')

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Limits:
    """ What each minute of a suite must stay within.
    """
    publish_p99_seconds: 'float' = 1.0
    delivery_p99_seconds: 'float' = 10.0
    min_rate_ratio: 'float' = 0.9
    max_message_rows: 'int' = 2_000_000
    max_wal_bytes: 'int' = 20 * _bytes_per_gb
    max_dead_ratio: 'float' = 2.0
    min_dead_tuples: 'int' = 200_000

    # A minute in which a flush of the probe of the drive took at least this long is a minute of a stalled drive,
    # whose latencies are reported and not checked.
    drive_stall_seconds: 'float' = 0.5

# ################################################################################################################################

@dataclass
class MinuteReport:
    """ The measurements of one minute and the checks it failed, if any.
    """
    index: 'int'
    since_start: 'str'
    local_time: 'str'
    publish_rate: 'float'
    delivery_rate: 'float'
    publish_p99: 'float'
    delivery_p99: 'float'
    message_rows: 'int'
    delivery_rows: 'int'
    wal_mb: 'float'
    rss_mb: 'float'
    open_files: 'int'
    threads: 'int'
    pool_queue: 'int'
    loop_lag: 'float' = 0.0
    gc_pause: 'float' = 0.0
    gc_generation: 'int' = 0
    drive_flush: 'float' = 0.0
    cpu_percent: 'float' = 0.0
    is_exempt: 'bool' = False
    details: 'strlist' = field(default_factory=list)
    failures: 'strlist' = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

def _p99(values:'list[float]') -> 'float':
    if not values:
        return 0.0

    ordered = sorted(values)
    index = int(len(ordered) * 0.99)
    index = min(index, len(ordered) - 1)

    out = ordered[index]
    return out

# ################################################################################################################################

def _humanize_duration(seconds:'float') -> 'str':
    minutes = int(seconds // 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        out = f'{hours} hour {minutes} min'
    else:
        out = f'{minutes} min'

    return out

# ################################################################################################################################
# ################################################################################################################################

class Monitor:
    """ Measures and checks each minute of one run and writes the reports to a file of the run.
    """

    def __init__(self, traffic:'Traffic', limits:'Limits', report_path:'str', label:'str') -> 'None':
        self.traffic = traffic
        self.limits = limits
        self.report_path = report_path
        self.label = label

        self.reports:'list[MinuteReport]' = []
        self.is_running = False
        self.is_disk_low = False

        # Whether each minute is checked against the rate, which a suite turns off while it changes the rate itself.
        self.checks_rate = True

        # Whether the current minute overlaps an overload that a suite causes, which exempts it from the rate
        # and latency checks, and which is cleared once the minute is recorded.
        self.is_minute_exempt = False

        # Whether the current minute overlaps a fault that a suite injects, which reports the errors of the minute
        # and the database statistics it could not read rather than failing the minute, and which is cleared
        # once the minute is recorded.
        self.allows_errors = False

        self._start = monotonic()
        self._minute_start = self._start
        self._process = psutil.Process()
        self._last_checkpoints = -1
        self._last_autovacuums = -1
        self._greenlet:'anylist' = []

        # The longest time in the current minute for which the event loop resumed a sleeping greenlet late,
        # and the longest garbage collection, both of which hold up every greenlet of the process.
        self._max_loop_lag = 0.0
        self._max_gc_pause = 0.0
        self._max_gc_generation = 0
        self._gc_started = 0.0

        # The longest flush in the current minute of the block that the probe of the drive writes.
        self._max_drive_flush = 0.0

        # Whether the census of live objects runs, and the number of live objects of each type at the previous one.
        self._takes_object_census = os.environ.get(_env_object_census, '') == '1'
        self._object_counts:'Counter[str]' = Counter()
        self._drive_probe_path = os.path.join(gettempdir(), f'zato-drive-probe-{os.getpid()}')
        self._drive_probe_fd = -1
        self._drive_probe_greenlet:'anylist' = []

        # The processor time the process used until the start of the current minute, in seconds.
        self._cpu_seconds = 0.0

        self._is_postgresql = get_pubsub_engine().dialect.name == Type_PostgreSQL

# ################################################################################################################################

    def _read_database(self, report:'MinuteReport') -> 'None':
        """ Adds the table sizes, the WAL, the checkpoints and the autovacuum runs to the report of a minute.
        """
        engine = get_pubsub_engine()

        if self._is_postgresql:
            with engine.connect() as connection:

                autovacuums = 0
                dead_tuples:'anydict' = {}

                for row in connection.execute(_pg_tables_query):
                    if row.relname == _message_table:
                        report.message_rows = row.n_live_tup
                    else:
                        report.delivery_rows = row.n_live_tup
                    autovacuums += row.autovacuum_count
                    dead_tuples[row.relname] = (row.n_live_tup, row.n_dead_tup)

                wal_bytes = connection.execute(_pg_wal_query).scalar_one()
                checkpoints = connection.execute(_pg_checkpoints_query).scalar_one()

            report.wal_mb = wal_bytes / _bytes_per_mb

            if self._last_checkpoints >= 0 and checkpoints > self._last_checkpoints:
                report.details.append(f'{checkpoints - self._last_checkpoints} checkpoint(s)')
            self._last_checkpoints = checkpoints

            if self._last_autovacuums >= 0 and autovacuums > self._last_autovacuums:
                report.details.append(f'{autovacuums - self._last_autovacuums} autovacuum run(s)')
            self._last_autovacuums = autovacuums

            # Autovacuum keeps pace while the dead rows stay in proportion to the live ones.
            for table_name, (live, dead) in dead_tuples.items():
                allowed = max(self.limits.min_dead_tuples, live * self.limits.max_dead_ratio)
                if dead > allowed:
                    message = f'{table_name} has {dead} dead rows for {live} live ones'
                    if self.allows_errors:
                        report.details.append(message)
                    else:
                        report.failures.append(message)

        else:
            with engine.connect() as connection:
                report.message_rows = connection.execute(text(f'select count(*) from {_message_table}')).scalar_one()
                report.delivery_rows = connection.execute(text(f'select count(*) from {_delivery_table}')).scalar_one()

            wal_path = get_pubsub_db_path() + '-wal'

            if os.path.exists(wal_path):
                report.wal_mb = os.path.getsize(wal_path) / _bytes_per_mb

# ################################################################################################################################

    def _check(self, report:'MinuteReport', counters:'MinuteCounters') -> 'None':
        """ Compares the measurements of a minute with the limits of the suite.
        """
        limits = self.limits

        if self.is_minute_exempt:
            report.details.append('overload, rate and latency not checked')

        elif report.drive_flush >= limits.drive_stall_seconds:
            report.details.append(f'drive flush stalled {report.drive_flush * _ms_per_second:.0f} ms, latency not checked')

        else:

            if report.publish_p99 > limits.publish_p99_seconds:
                report.failures.append(f'publish p99 {report.publish_p99:.3f}s above {limits.publish_p99_seconds}s')

            if report.delivery_p99 > limits.delivery_p99_seconds:
                report.failures.append(f'delivery p99 {report.delivery_p99:.3f}s above {limits.delivery_p99_seconds}s')

        if self.checks_rate and not self.is_minute_exempt:
            min_rate = self.traffic.rate * limits.min_rate_ratio
            if report.publish_rate < min_rate:
                report.failures.append(f'publish rate {report.publish_rate:.1f}/s below {min_rate:.1f}/s')

        if report.message_rows > limits.max_message_rows:
            report.failures.append(f'{report.message_rows} message rows above {limits.max_message_rows}')

        if report.wal_mb * _bytes_per_mb > limits.max_wal_bytes:
            report.failures.append(f'WAL of {report.wal_mb:.0f} MB above {limits.max_wal_bytes // _bytes_per_mb} MB')

        if counters.errors:
            message = f'{counters.errors} error(s): {counters.error_messages}'
            if self.allows_errors:
                report.details.append(message)
            else:
                report.failures.append(message)

# ################################################################################################################################

    def record_minute(self) -> 'MinuteReport':
        """ Measures the minute that ends now, checks it and writes its report.
        """
        counters = self.traffic.take_minute()

        now = monotonic()
        elapsed = now - self._start

        # The last interval of a run may be shorter than a minute, so the rates are per its actual length.
        interval_seconds = now - self._minute_start
        self._minute_start = now

        memory = self._process.memory_info()

        # The share of one processor that the process used during the minute.
        cpu_times = self._process.cpu_times()
        cpu_seconds = cpu_times.user + cpu_times.system
        cpu_used = cpu_seconds - self._cpu_seconds
        self._cpu_seconds = cpu_seconds

        report = MinuteReport(
            index=len(self.reports) + 1,
            since_start=_humanize_duration(elapsed),
            local_time=datetime.now().strftime('%H:%M:%S'),
            publish_rate=counters.published / interval_seconds,
            delivery_rate=(counters.pulled + counters.pushed) / interval_seconds,
            publish_p99=_p99(counters.publish_seconds),
            delivery_p99=_p99(counters.delivery_seconds),
            message_rows=0,
            delivery_rows=0,
            wal_mb=0.0,
            rss_mb=memory.rss / _bytes_per_mb,
            open_files=self._process.num_fds(),
            threads=self._process.num_threads(),
            pool_queue=len(get_hub().threadpool),
            loop_lag=self._max_loop_lag,
            gc_pause=self._max_gc_pause,
            gc_generation=self._max_gc_generation,
            drive_flush=self._max_drive_flush,
            cpu_percent=cpu_used / interval_seconds * 100,
        )

        self._max_loop_lag = 0.0
        self._max_gc_pause = 0.0
        self._max_gc_generation = 0
        self._max_drive_flush = 0.0

        # The statistics of a database that a fault keeps unavailable are reported as missing ..
        try:
            self._read_database(report)
        except Exception as e:
            message = f'database statistics not read: {e.__class__.__name__}: {e}'[:300]
            if self.allows_errors:
                report.details.append(message)
            else:
                report.failures.append(message)

        # .. and everything else is checked as usual.
        self._check(report, counters)

        report.is_exempt = self.is_minute_exempt
        self.is_minute_exempt = False
        self.allows_errors = False

        free_gb = disk_usage(gettempdir()).free / _bytes_per_gb

        if free_gb < _min_free_disk_gb:
            self.is_disk_low = True
            report.failures.append(f'free disk {free_gb:.1f} GB below {_min_free_disk_gb} GB, the run stops')

        self.reports.append(report)
        self._write(report)

        if self._takes_object_census and report.index % _object_census_minutes == 0:
            self._write_object_census()

        return report

# ################################################################################################################################

    def _describe_holders(self, item:'object', census_list:'anylist') -> 'str':
        """ Returns the types of the objects that refer to an object, and for each dictionary among them,
        the types of the objects that refer to that dictionary, apart from the census itself.
        """
        out:'strlist' = []

        for holder in gc.get_referrers(item):

            # The list of the census and the frame that walks it refer to every socket in it.
            if holder is census_list or isinstance(holder, FrameType):
                continue

            description = type(holder).__qualname__

            if isinstance(holder, dict):
                owners = [type(owner).__qualname__ for owner in gc.get_referrers(holder)]
                description += f' of {owners}'

            out.append(description)

        return ', '.join(out)

# ################################################################################################################################

    def _write_object_census(self) -> 'None':
        """ Writes the object types whose number of live instances grew the most since the previous census,
        and what holds each open socket that has no peer.
        """
        counts:'Counter[str]' = Counter()
        unconnected:'anylist' = []

        for item in gc.get_objects():
            item_type = type(item)
            counts[f'{item_type.__module__}.{item_type.__qualname__}'] += 1

            # A socket with a descriptor and no peer is either a listening one or one whose connection has ended.
            if isinstance(item, GeventSocket) and item.fileno() != -1:
                try:
                    _ = item.getpeername()
                except OSError:
                    unconnected.append(item)

        growth = counts.copy()
        growth.subtract(self._object_counts)
        self._object_counts = counts

        types = [f'{name} {counts[name]} (+{delta})' for name, delta in growth.most_common(_object_census_types)]
        lines = [f'{self.label} | objects | {", ".join(types)}']
        lines.append(f'{self.label} | sockets without a peer | {len(unconnected)}')

        for sock in unconnected[:_object_census_sockets]:
            lines.append(f'{self.label} | socket {sock!r} | held by {self._describe_holders(sock, unconnected)}')

        with open(self.report_path, 'a') as report_file:
            for line in lines:
                _ = report_file.write(line + '\n')

        for line in lines:
            print(line, flush=True)

# ################################################################################################################################

    def _write(self, report:'MinuteReport') -> 'None':
        result = 'failed' if report.failures else 'ok'
        details = report.details + report.failures

        line = f'{self.label} | {report.since_start} | {report.local_time} | {report.publish_rate:.1f}/s | ' + \
            f'{report.delivery_rate:.1f}/s | {report.publish_p99 * 1000:.0f} ms | {report.delivery_p99 * 1000:.0f} ms | ' + \
            f'rows {report.message_rows}/{report.delivery_rows} | WAL {report.wal_mb:.0f} MB | ' + \
            f'RSS {report.rss_mb:.0f} MB | fds {report.open_files} | threads {report.threads} | ' + \
            f'pool {report.pool_queue} | lag {report.loop_lag * _ms_per_second:.0f} ms | ' + \
            f'GC {report.gc_pause * _ms_per_second:.0f} ms gen {report.gc_generation} | ' + \
            f'flush {report.drive_flush * _ms_per_second:.0f} ms | CPU {report.cpu_percent:.0f}% | {result} | {"; ".join(details) if details else "---"}'

        with open(self.report_path, 'a') as report_file:
            _ = report_file.write(line + '\n')

        print(line, flush=True)

# ################################################################################################################################

    def _run(self) -> 'None':
        next_minute = monotonic() + Minute_Seconds

        while self.is_running:
            sleep(max(next_minute - monotonic(), 0))
            if not self.is_running:
                break
            _ = self.record_minute()
            next_minute += Minute_Seconds

# ################################################################################################################################

    def _probe_loop_lag(self) -> 'None':
        """ Measures how much later than requested the event loop resumes a sleeping greenlet.
        """
        while self.is_running:
            started = monotonic()
            sleep(_loop_lag_interval)
            lag = monotonic() - started - _loop_lag_interval
            if lag > self._max_loop_lag:
                self._max_loop_lag = lag

# ################################################################################################################################

    def _on_gc(self, phase:'str', info:'anydict') -> 'None':
        """ Measures each garbage collection of the process.
        """
        if phase == 'start':
            self._gc_started = monotonic()
            return

        pause = monotonic() - self._gc_started

        if pause > self._max_gc_pause:
            self._max_gc_pause = pause
            self._max_gc_generation = info['generation']

# ################################################################################################################################

    def _flush_drive_once(self) -> 'float':
        """ Writes and flushes the block of the probe, in a thread of the pool, and returns how long the flush took.
        """
        _ = os.pwrite(self._drive_probe_fd, _drive_probe_block, 0)

        started = monotonic()
        os.fdatasync(self._drive_probe_fd)

        out = monotonic() - started
        return out

# ################################################################################################################################

    def _probe_drive(self) -> 'None':
        """ Measures how long the drive of the runtime data takes to flush one block, independently of the database.
        """
        pool = get_hub().threadpool

        while self.is_running:
            elapsed = pool.apply(self._flush_drive_once)
            if elapsed > self._max_drive_flush:
                self._max_drive_flush = elapsed
            sleep(_drive_probe_interval)

# ################################################################################################################################

    def start(self) -> 'None':
        self.is_running = True

        cpu_times = self._process.cpu_times()
        self._cpu_seconds = cpu_times.user + cpu_times.system

        self._drive_probe_fd = os.open(self._drive_probe_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        gc.callbacks.append(self._on_gc)
        self._greenlet.append(spawn(self._run))
        self._greenlet.append(spawn(self._probe_loop_lag))
        self._drive_probe_greenlet.append(spawn(self._probe_drive))

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the measurement, checking the part of a minute that passed since the last report,
        so that nothing that happened at the end of a run goes unchecked.
        """
        self.is_running = False
        gc.callbacks.remove(self._on_gc)

        for greenlet in self._greenlet:
            greenlet.kill()

        # The probe of the drive completes its current flush in the thread pool before the file is closed.
        for greenlet in self._drive_probe_greenlet:
            greenlet.join()

        os.close(self._drive_probe_fd)
        os.remove(self._drive_probe_path)

        if monotonic() - self._minute_start >= _min_final_interval_seconds:
            _ = self.record_minute()

# ################################################################################################################################

    def get_failures(self) -> 'strlist':
        out:'strlist' = []

        for report in self.reports:
            for failure in report.failures:
                out.append(f'minute {report.index}: {failure}')

        return out

# ################################################################################################################################

    def get_resource_growth(self, baseline_minute:'int') -> 'strlist':
        """ Compares the resources of the last minute with those of a baseline minute, after the warm-up,
        and returns the ones that grew beyond their bounds.
        """
        out:'strlist' = []

        if len(self.reports) <= baseline_minute:
            return out

        baseline = self.reports[baseline_minute - 1]
        last = self.reports[-1]

        if last.rss_mb > baseline.rss_mb * 1.5 + 100:
            out.append(f'RSS grew from {baseline.rss_mb:.0f} MB to {last.rss_mb:.0f} MB')

        if last.open_files > baseline.open_files + 50:
            out.append(f'Open files grew from {baseline.open_files} to {last.open_files}')

        if last.threads > baseline.threads + 20:
            out.append(f'Threads grew from {baseline.threads} to {last.threads}')

        if last.pool_queue > 1000:
            out.append(f'Thread pool queue holds {last.pool_queue} tasks')

        return out

# ################################################################################################################################
# ################################################################################################################################
