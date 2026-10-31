# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The per-minute measurement of the stability suites - rates, p99 latencies, table sizes, the WAL, autovacuum,
# the resources of the process and the free disk space, each minute checked against the limits of its suite.

# stdlib
import os
from dataclasses import dataclass, field
from datetime import datetime
from shutil import disk_usage
from tempfile import gettempdir
from time import monotonic

# gevent
from gevent import get_hub, sleep, spawn

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

        self._start = monotonic()
        self._minute_start = self._start
        self._process = psutil.Process()
        self._last_checkpoints = -1
        self._last_autovacuums = -1
        self._greenlet:'anylist' = []

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
                    report.failures.append(f'{table_name} has {dead} dead rows for {live} live ones')

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
            report.failures.append(f'{counters.errors} error(s): {counters.error_messages}')

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
        )

        self._read_database(report)
        self._check(report, counters)

        self.is_minute_exempt = False

        free_gb = disk_usage(gettempdir()).free / _bytes_per_gb

        if free_gb < _min_free_disk_gb:
            self.is_disk_low = True
            report.failures.append(f'free disk {free_gb:.1f} GB below {_min_free_disk_gb} GB, the run stops')

        self.reports.append(report)
        self._write(report)

        return report

# ################################################################################################################################

    def _write(self, report:'MinuteReport') -> 'None':
        result = 'failed' if report.failures else 'ok'
        details = report.details + report.failures

        line = f'{self.label} | {report.since_start} | {report.local_time} | {report.publish_rate:.1f}/s | ' + \
            f'{report.delivery_rate:.1f}/s | {report.publish_p99 * 1000:.0f} ms | {report.delivery_p99 * 1000:.0f} ms | ' + \
            f'rows {report.message_rows}/{report.delivery_rows} | WAL {report.wal_mb:.0f} MB | ' + \
            f'RSS {report.rss_mb:.0f} MB | fds {report.open_files} | threads {report.threads} | ' + \
            f'pool {report.pool_queue} | {result} | {"; ".join(details) if details else "---"}'

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

    def start(self) -> 'None':
        self.is_running = True
        self._greenlet.append(spawn(self._run))

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the measurement, checking the part of a minute that passed since the last report,
        so that nothing that happened at the end of a run goes unchecked.
        """
        self.is_running = False

        for greenlet in self._greenlet:
            greenlet.kill()

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
