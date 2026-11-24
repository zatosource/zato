# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The per-minute measurement of a pub/sub suite - the rates and p99 latencies of the traffic, the table sizes,
# the WAL and the autovacuum of the database of the server, the resources of the processes of the server and
# the free space of the drive of the runtime data, each minute checked against the limits of its suite.

# stdlib
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from logging import getLogger
from shutil import disk_usage
from time import monotonic

# gevent
from gevent import get_hub, sleep, spawn

# psutil
import psutil

# Zato
from pubsub_rest.latency import find_stalled_seconds, get_latencies, get_percentile, get_second, get_steady_latency, \
    Max_Stalled_Share, Percentile
from zato.common.test.pubsub_database import get_runtime_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pubsub_rest.latency import int_set, latency_list
    from pubsub_rest.server import PubSubServer
    from pubsub_rest.traffic import MinuteCounters, Traffic
    from zato.common.typing_ import anydict, anylist, dictlist, strlist

    minute_report_list = list['MinuteReport']

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# How long one measured interval lasts, in seconds, unless the variable says otherwise.
Minute_Seconds = 60
_env_interval = 'Zato_Test_Stability_Interval_Seconds'

# How long the last interval of a run must be for it to be reported, in seconds.
_min_final_interval_seconds = 1

# How often the drive of the runtime data is probed with a flush of one block of its own, in seconds,
# and the size of that block, in bytes.
_drive_probe_interval = 0.1
_drive_probe_block = b'\0' * 4096

# How many milliseconds one second has, and how many bytes one gigabyte and one megabyte have.
_ms_per_second = 1000
_bytes_per_gb = 1024 ** 3
_bytes_per_mb = 1024 ** 2

# Below this much free space on the drive of the runtime data, a run stops.
_min_free_disk_gb = 20

# The fewest latencies of which the percentile is not the slowest one. Below that, the percentile is the maximum,
# as in the final part of a minute of a run, and is reported without being checked.
_min_percentile_samples = round(1 / (1 - Percentile)) + 1

# How many percent one processor used for a whole interval is.
_full_processor_percent = 100

# How long a message of a minute is at most.
_max_message_length = 300

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Limits:
    """ What each minute of a suite must stay within.
    """
    publish_p99_seconds: 'float' = 1.0
    pull_p99_seconds: 'float' = 10.0
    push_p99_seconds: 'float' = 10.0
    min_rate_ratio: 'float' = 0.9
    max_message_rows: 'int' = 2_000_000
    max_wal_bytes: 'int' = 20 * _bytes_per_gb
    max_dead_ratio: 'float' = 2.0
    min_dead_tuples: 'int' = 200_000

    # The share of the seconds of a minute in which the host may stall the publications, which are excluded
    # from the latencies and the rate that the minute is checked against.
    max_stalled_share: 'float' = Max_Stalled_Share

    # A minute in which a flush of the probe of the drive took at least this long is a minute of a stalled drive,
    # whose latencies are reported and not checked.
    drive_stall_seconds: 'float' = 0.5

# ################################################################################################################################

@dataclass(init=False)
class MinuteReport:
    """ The measurements of one minute and the checks it failed, if any.
    """
    index: 'int'
    since_start: 'str'
    local_time: 'str'
    publish_rate: 'float'
    pull_rate: 'float'
    push_rate: 'float'
    publish_p99: 'float'
    pull_p99: 'float'
    push_p99: 'float'
    message_rows: 'int' = 0
    delivery_rows: 'int' = 0
    wal_mb: 'float' = 0.0
    rss_mb: 'float' = 0.0
    open_files: 'int' = 0
    threads: 'int' = 0
    processes: 'int' = 0
    drive_flush: 'float' = 0.0
    cpu_percent: 'float' = 0.0
    stalled_seconds: 'int' = 0
    is_exempt: 'bool' = False
    allows_errors: 'bool' = False
    details: 'strlist' = field(default_factory=list)
    failures: 'strlist' = field(default_factory=list)

# ################################################################################################################################
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

def _shorten(message:'str') -> 'str':
    out = message[:_max_message_length]
    return out

# ################################################################################################################################
# ################################################################################################################################

class Monitor:
    """ Measures and checks each minute of one run of the traffic against a server.
    """

    def __init__(self, server:'PubSubServer', traffic:'Traffic', limits:'Limits') -> 'None':
        self.server = server
        self.traffic = traffic
        self.limits = limits

        self.reports:'minute_report_list' = []
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

        # How long one measured interval lasts, in seconds
        if interval := os.environ.get(_env_interval, ''):
            self.interval_seconds = int(interval)
        else:
            self.interval_seconds = Minute_Seconds

        self._start = monotonic()
        self._minute_start = self._start
        self._next_minute = self._start + self.interval_seconds

        self._last_checkpoints = -1
        self._last_autovacuums = -1
        self._greenlets:'anylist' = []

        # The processor time that the processes of the server used until the start of the current minute, by process.
        self._cpu_seconds:'anydict' = {}

        # The longest flush in the current minute of the block that the probe of the drive writes.
        self._max_drive_flush = 0.0
        self._drive_probe_path = os.path.join(get_runtime_dir(), f'zato-drive-probe-{os.getpid()}')
        self._drive_probe_fd = -1

# ################################################################################################################################

    def _get_processes(self) -> 'anylist':
        """ The processes of the server that still exist.
        """
        out:'anylist' = []

        for pid in self.server.get_pids():
            try:
                process = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue
            else:
                out.append(process)

        return out

# ################################################################################################################################

    def _read_processes(self, report:'MinuteReport', interval_seconds:'float') -> 'None':
        """ Adds the memory, the open files, the threads and the processor time of the processes of the server
        to the report of a minute.
        """
        cpu_used = 0.0
        cpu_seconds:'anydict' = {}

        for process in self._get_processes():
            try:
                with process.oneshot():
                    memory = process.memory_info()
                    open_files = process.num_fds()
                    threads = process.num_threads()
                    cpu_times = process.cpu_times()
            except psutil.NoSuchProcess:
                continue

            report.rss_mb += memory.rss / _bytes_per_mb
            report.open_files += open_files
            report.threads += threads
            report.processes += 1

            # The processor time of a process is counted from the previous minute, or from its start if it is new.
            used = cpu_times.user + cpu_times.system
            cpu_seconds[process.pid] = used

            if process.pid in self._cpu_seconds:
                used -= self._cpu_seconds[process.pid]

            cpu_used += used

        self._cpu_seconds = cpu_seconds
        report.cpu_percent = cpu_used / interval_seconds * _full_processor_percent

# ################################################################################################################################

    def _read_database(self, report:'MinuteReport') -> 'None':
        """ Adds the table sizes, the WAL, the checkpoints and the autovacuum runs to the report of a minute.
        """
        statistics = self.server.get_database_statistics()

        report.message_rows = statistics['message_rows']
        report.delivery_rows = statistics['delivery_rows']
        report.wal_mb = statistics['wal_bytes'] / _bytes_per_mb

        if not statistics['is_postgresql']:
            return

        checkpoints = statistics['checkpoints']
        autovacuums = statistics['autovacuums']

        if self._last_checkpoints >= 0 and checkpoints > self._last_checkpoints:
            report.details.append(f'{checkpoints - self._last_checkpoints} checkpoint(s)')
        self._last_checkpoints = checkpoints

        if self._last_autovacuums >= 0 and autovacuums > self._last_autovacuums:
            report.details.append(f'{autovacuums - self._last_autovacuums} autovacuum run(s)')
        self._last_autovacuums = autovacuums

        # Autovacuum keeps pace while the dead rows stay in proportion to the live ones.
        for table_name, (live, dead) in statistics['dead_tuples'].items():
            allowed = max(self.limits.min_dead_tuples, live * self.limits.max_dead_ratio)

            if dead > allowed:
                message = f'{table_name} has {dead} dead rows for {live} live ones'
                if report.allows_errors:
                    report.details.append(message)
                else:
                    report.failures.append(message)

# ################################################################################################################################

    def _check_p99(
        self,
        report:'MinuteReport',
        name:'str',
        samples:'latency_list',
        minute_start:'float',
        stalled:'int_set',
        limit:'float',
        ) -> 'None':
        """ Compares the p99 of one kind of latency, over the publications that began outside the stalled seconds,
        with its limit, unless there are too few latencies for the p99 to differ from the slowest one.
        """
        steady = get_steady_latency(samples, minute_start, stalled)

        if steady.stalled_seconds:
            report.details.append(f'{name} slowest {steady.slowest_stalled:.3f}s in {steady.stalled_seconds} ' +
                'stalled second(s), excluded')

        if steady.sample_count < _min_percentile_samples:
            report.details.append(f'{name} p99 {steady.percentile:.3f}s of {steady.sample_count} sample(s) not checked, ' +
                f'below {_min_percentile_samples} samples')

        elif steady.percentile > limit:
            report.failures.append(f'{name} p99 {steady.percentile:.3f}s above {limit}s, ' +
                f'{steady.stalled_seconds} stalled second(s) excluded')

# ################################################################################################################################

    def _check_rate(self, report:'MinuteReport', counters:'MinuteCounters', minute_start:'float',
        interval_seconds:'float', stalled:'int_set') -> 'None':
        """ Compares the rate of the publications that began outside the stalled seconds with the rate of the traffic.
        """
        published = 0

        for started, _ in counters.publish_seconds:
            if get_second(started, minute_start) not in stalled:
                published += 1

        rate = published / (interval_seconds - len(stalled))
        min_rate = self.traffic.rate * self.limits.min_rate_ratio

        if rate < min_rate:
            report.failures.append(f'publish rate {rate:.1f}/s below {min_rate:.1f}/s, ' +
                f'{len(stalled)} stalled second(s) excluded')

# ################################################################################################################################

    def _check(self, report:'MinuteReport', counters:'MinuteCounters', minute_start:'float',
        interval_seconds:'float') -> 'None':
        """ Compares the measurements of a minute with the limits of the suite.
        """
        limits = self.limits

        # The seconds in which the host stalled the publications are found once and excluded from each check ..
        stalled:'int_set' = set()

        if not report.is_exempt:
            stalled = find_stalled_seconds(counters.publish_seconds, minute_start, int(interval_seconds),
                limits.publish_p99_seconds, self.checks_rate, limits.max_stalled_share)
            report.stalled_seconds = len(stalled)

        # .. and the rest of the minute is checked against the limits.
        if report.is_exempt:
            report.details.append('overload, rate and latency not checked')

        elif report.drive_flush >= limits.drive_stall_seconds:
            report.details.append(f'drive flush stalled {report.drive_flush * _ms_per_second:.0f} ms, latency not checked')

        else:
            self._check_p99(report, 'publish', counters.publish_seconds, minute_start, stalled, limits.publish_p99_seconds)
            self._check_p99(report, 'pull', counters.pull_seconds, minute_start, stalled, limits.pull_p99_seconds)
            self._check_p99(report, 'push', counters.push_seconds, minute_start, stalled, limits.push_p99_seconds)

        if self.checks_rate and not report.is_exempt:
            self._check_rate(report, counters, minute_start, interval_seconds, stalled)

        if report.message_rows > limits.max_message_rows:
            report.failures.append(f'{report.message_rows} message rows above {limits.max_message_rows}')

        if report.wal_mb * _bytes_per_mb > limits.max_wal_bytes:
            report.failures.append(f'WAL of {report.wal_mb:.0f} MB above {limits.max_wal_bytes // _bytes_per_mb} MB')

        if counters.errors:
            message = f'{counters.errors} error(s): {counters.error_messages}'
            if report.allows_errors:
                report.details.append(message)
            else:
                report.failures.append(message)

# ################################################################################################################################

    def record_minute(self) -> 'MinuteReport':
        """ Measures the minute that ends now and checks it.
        """
        counters = self.traffic.take_minute()

        now = monotonic()
        elapsed = now - self._start

        # The last interval of a run may be shorter than a minute, so the rates are per its actual length.
        minute_start = self._minute_start
        interval_seconds = now - minute_start
        self._minute_start = now

        report = MinuteReport()
        report.index = len(self.reports) + 1
        report.since_start = _humanize_duration(elapsed)
        report.local_time = datetime.now().strftime('%H:%M:%S')
        report.publish_rate = counters.published / interval_seconds
        report.pull_rate = counters.pulled / interval_seconds
        report.push_rate = counters.pushed / interval_seconds
        report.publish_p99 = get_percentile(get_latencies(counters.publish_seconds))
        report.pull_p99 = get_percentile(get_latencies(counters.pull_seconds))
        report.push_p99 = get_percentile(get_latencies(counters.push_seconds))
        report.drive_flush = self._max_drive_flush
        report.details = []
        report.failures = []

        self._max_drive_flush = 0.0

        # The marks of the minute move to its report before the server is read, because a server that a fault
        # holds up holds up the read, and the marks that the suite sets in the meantime belong to the next minute ..
        report.is_exempt = self.is_minute_exempt
        report.allows_errors = self.allows_errors
        self.is_minute_exempt = False
        self.allows_errors = False

        self._read_processes(report, interval_seconds)

        # .. the statistics of a database that the server cannot read are reported as missing ..
        try:
            self._read_database(report)
        except Exception as e:
            message = _shorten(f'database statistics not read: {e.__class__.__name__}: {e}')
            if report.allows_errors:
                report.details.append(message)
            else:
                report.failures.append(message)

        # .. and everything else is checked as usual.
        self._check(report, counters, minute_start, interval_seconds)

        free_gb = disk_usage(get_runtime_dir()).free / _bytes_per_gb

        if free_gb < _min_free_disk_gb:
            self.is_disk_low = True
            report.failures.append(f'free disk {free_gb:.1f} GB below {_min_free_disk_gb} GB, the run stops')

        self.reports.append(report)

        logger.info('Interval %d (%s) -> published %.1f/s, pulled %.1f/s, pushed %.1f/s, publish p99 %.3f s, ' +
            'pull p99 %.3f s, push p99 %.3f s, message rows %d, failures %s', report.index, report.since_start,
            report.publish_rate, report.pull_rate, report.push_rate, report.publish_p99, report.pull_p99, report.push_p99,
            report.message_rows, report.failures)

        logger.info('Interval %d resources -> server CPU %.0f%%, server RSS %.0f MB, delivery rows %d, WAL %.0f MB, ' +
            'longest drive flush %.0f ms, stalled seconds %d, details %s', report.index, report.cpu_percent, report.rss_mb,
            report.delivery_rows, report.wal_mb, report.drive_flush * _ms_per_second, report.stalled_seconds, report.details)

        return report

# ################################################################################################################################

    def _run(self) -> 'None':
        self._next_minute = monotonic() + self.interval_seconds

        while self.is_running:
            sleep(max(self._next_minute - monotonic(), 0))
            if not self.is_running:
                break

            # A minute that the suite ended early moved the grid, so the sleep continues to the end of the new minute.
            if monotonic() < self._next_minute:
                continue

            _ = self.record_minute()
            self._next_minute += self.interval_seconds

# ################################################################################################################################

    def end_minute(self) -> 'None':
        """ Ends the current minute now and starts the grid of the minutes again from this moment. A minute too short
        to be reported continues as part of the next one, without the marks that the suite set for it.
        """
        if monotonic() - self._minute_start >= _min_final_interval_seconds:
            _ = self.record_minute()
        else:
            self.is_minute_exempt = False
            self.allows_errors = False

        self._next_minute = monotonic() + self.interval_seconds

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
        self._start = monotonic()
        self._minute_start = self._start

        # The processor time of the processes of the server is counted from now on ..
        for process in self._get_processes():
            cpu_times = process.cpu_times()
            self._cpu_seconds[process.pid] = cpu_times.user + cpu_times.system

        # .. and the drive is probed with a file of its own.
        self._drive_probe_fd = os.open(self._drive_probe_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)

        self._greenlets.append(spawn(self._run))
        self._greenlets.append(spawn(self._probe_drive))

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the measurement, checking the part of a minute that passed since the last report,
        so that nothing that happened at the end of a run goes unchecked.
        """
        self.is_running = False

        # The probe of the drive completes its current flush in the thread pool before the file is closed.
        run_greenlet, probe_greenlet = self._greenlets
        run_greenlet.kill()
        _ = probe_greenlet.join()

        self._greenlets = []

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
        """ Compares the resources of the server in the last minute with those of a baseline minute, after the warm-up,
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

        return out

# ################################################################################################################################

    def get_figures(self) -> 'dictlist':
        """ The measurements of every minute, which a suite records through the result function.
        """
        out:'dictlist' = []

        for report in self.reports:
            out.append(asdict(report))

        return out

# ################################################################################################################################
# ################################################################################################################################
