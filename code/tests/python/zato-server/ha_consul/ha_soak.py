# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The per-minute reports of the long runs. Each minute records the publications and deliveries per second,
# the publish and barrier latencies, the generation, and for each node its role, the memory, open files and tasks
# of its container, the size of the WAL of each database and the replication lag. Each minute also checks the free
# space of the root file system, and the run ends with the bounds that the resources and the WAL remain within.

# stdlib
import logging
import os
import shutil
import socket
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from subprocess import CalledProcessError

# Zato
from container import Container
from ha_traffic import get_percentile
from topology import docker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from ha_env import HAEnvironment
    from ha_traffic import TimedPublisher
    from nodes import Node
    from workload import Workload
    from zato.common.typing_ import anydict, strintdict, strlist

    HAEnvironment = HAEnvironment
    TimedPublisher = TimedPublisher
    Workload = Workload

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.ha_consul.soak')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often a report is produced, in seconds, and how many of the latest reports each table shows
    Report_Interval = 60
    Table_Reports = 10

    # How many reports after the start of a run are not compared with the bounds of growth
    Warm_Up_Reports = 2

    # How much the memory of a container may grow over a run, a factor of the baseline and a number of megabytes on top
    Memory_Growth_Factor = 1.5
    Memory_Growth_MB = 100

    # How many open files and how many processes and threads may be added over a run
    Open_Files_Growth = 50
    Tasks_Growth = 50

    # The size that the WAL of a database never exceeds, twice the size at which the node checkpoints it
    WAL_Bound_Bytes = 128 * 1024 * 1024

    # The free space of the root file system below which a run stops, in bytes
    Min_Free_Bytes = 20 * 1024 * 1024 * 1024

    # How long the replication lag may take to return to zero once the traffic stops, and how often it is read, in seconds
    Lag_Timeout = 60
    Poll_Interval = 0.5

    # How often the barrier is probed, and how long a probe waits for its answer, in seconds
    Probe_Interval = 0.1
    Probe_Timeout = 30.0

    # The database whose barrier is probed, the file name of the socket and the answer of a barrier that completed
    Probe_Database = 'pubsub'
    Barrier_Socket_Name = 'ha-barrier.sock'
    Barrier_OK = b'ok\n'

    # The databases whose WAL is measured
    Database_Files = ['pubsub.db', 'common.db']

    # The percentile of the latency that each report contains
    Percentile_99 = 0.99

    # The number of bytes in one megabyte
    Bytes_Per_MB = 1024 * 1024

    # The command that counts the open files of all the processes of a container
    Count_Open_Files = 'for fd_dir in /proc/[0-9]*/fd; do ls "$fd_dir"; done 2>/dev/null | wc -l'

    # The results of a minute
    Result_OK = 'ok'
    Result_Error = 'error'

    # The columns of the table of reports, where the roles, lags, WAL sizes and memory list each node in turn
    Table_Columns = ['Since start', 'Local time', 'Publishes/s', 'Deliveries/s', 'Publish p99', 'Barrier p99',
        'Generation', 'Roles', 'Lag', 'WAL MB', 'Memory MB', 'Result', 'Details']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class NodeSample:
    """ The state and resources of one node at one time.
    """
    node_name: 'str'
    role: 'str'
    memory_mb: 'float'
    open_files: 'int'
    tasks: 'int'
    wal_bytes: 'strintdict'
    lag_frames: 'int'

# ################################################################################################################################

@dataclass(init=False)
class MinuteReport:
    """ What one minute of a long run consisted of.
    """
    minute: 'int'
    since_start: 'str'
    local_time: 'str'
    publishes_per_second: 'float'
    deliveries_per_second: 'float'
    publish_p99: 'float'
    barrier_p99: 'float'
    generation: 'int'
    result: 'str'
    details: 'strlist'
    nodes: 'list[NodeSample]'

# ################################################################################################################################
# ################################################################################################################################

def get_lag_frames(report:'anydict') -> 'int':
    """ Returns how many frames the node scanned and the standby has not confirmed yet, across all the databases.
    """
    out = 0

    for database in report['databases']:
        scanned = database['scanned']
        confirmed = database['confirmed']

        # A new cycle of the WAL begins at its first frame, so every frame of the cycle scanned is unconfirmed.
        if scanned['cycle'] == confirmed['cycle']:
            out += scanned['frame'] - confirmed['frame']
        else:
            out += scanned['frame']

    return out

# ################################################################################################################################

def read_wal_bytes(node:'Node') -> 'strintdict':
    out:'strintdict' = {}

    for file_name in ModuleCtx.Database_Files:
        wal_path = node.db_path(file_name) + '-wal'

        # A database without a writer since its last checkpoint has no WAL.
        if os.path.exists(wal_path):
            out[file_name] = os.path.getsize(wal_path)
        else:
            out[file_name] = 0

    return out

# ################################################################################################################################

def take_node_sample(node:'Node') -> 'NodeSample':
    container = Container(node.container_name)

    report = node.read_role()

    out = NodeSample()
    out.node_name = node.node_name
    out.memory_mb = container.read_memory_current() / ModuleCtx.Bytes_Per_MB
    out.tasks = int(container.read_cgroup('pids.current'))
    out.wal_bytes = read_wal_bytes(node)

    open_files = docker('exec', node.container_name, 'sh', '-c', ModuleCtx.Count_Open_Files)
    out.open_files = int(open_files.stdout.strip())

    # A node that does not answer has no role and reports no lag.
    if report is None:
        out.role = '-'
        out.lag_frames = 0
    else:
        out.role = report['role']
        out.lag_frames = get_lag_frames(report)

    return out

# ################################################################################################################################

def humanize_duration(seconds:'float') -> 'str':
    """ Returns a duration as hours and minutes, such as 1 min or 1 hour 8 min.
    """
    minutes = int(seconds // 60)
    hours, minutes = divmod(minutes, 60)

    if not hours:
        out = f'{minutes} min'
    elif hours == 1:
        out = f'1 hour {minutes} min'
    else:
        out = f'{hours} hours {minutes} min'

    return out

# ################################################################################################################################

def _format_row(report:'MinuteReport') -> 'str':
    roles:'strlist' = []
    lags:'strlist' = []
    wal:'strlist' = []
    memory:'strlist' = []

    for sample in report.nodes:
        roles.append(sample.role)
        lags.append(str(sample.lag_frames))
        memory.append(f'{sample.memory_mb:.0f}')
        wal.append(f'{max(sample.wal_bytes.values()) / ModuleCtx.Bytes_Per_MB:.1f}')

    cells = [
        report.since_start,
        report.local_time,
        f'{report.publishes_per_second:.1f}',
        f'{report.deliveries_per_second:.1f}',
        f'{report.publish_p99:.3f}s',
        f'{report.barrier_p99:.3f}s',
        str(report.generation),
        ' / '.join(roles),
        ' / '.join(lags),
        ' / '.join(wal),
        ' / '.join(memory),
        report.result,
        ', '.join(report.details),
    ]

    out = '| ' + ' | '.join(cells) + ' |'
    return out

# ################################################################################################################################

def format_table(reports:'list[MinuteReport]') -> 'str':
    """ Returns the latest reports as a table, followed by each report whose result is an error,
    or by a single row of dashes if there is none.
    """
    separator = '|' + ' --- |' * len(ModuleCtx.Table_Columns)
    lines = ['| ' + ' | '.join(ModuleCtx.Table_Columns) + ' |', separator]

    for report in reports[-ModuleCtx.Table_Reports:]:
        lines.append(_format_row(report))

    error_rows:'strlist' = []

    for report in reports:
        if report.result == ModuleCtx.Result_Error:
            error_rows.append(_format_row(report))

    if error_rows:
        lines.extend(error_rows)
    else:
        lines.append(separator)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################
# ################################################################################################################################

class BarrierProbe:
    """ Requests the barrier of each node in a thread of its own, one request after another, and records how long
    each request that completed took. A node that is not active answers that it was replaced, which is not recorded.
    """

    def __init__(self, env:'HAEnvironment') -> 'None':
        self.env = env
        self.lock = threading.Lock()
        self.is_running = threading.Event()
        self.latencies:'list[tuple[float, float]]' = []
        self._threads:'list[threading.Thread]' = []

    def start(self) -> 'None':
        self.is_running.set()

        for node in self.env.node_list:
            thread = threading.Thread(target=self._run, args=(node,), daemon=True)
            thread.start()
            self._threads.append(thread)

    def stop(self) -> 'None':
        self.is_running.clear()

        for thread in self._threads:
            thread.join()

    def get_latencies_between(self, start:'float', end:'float') -> 'list[float]':
        out:'list[float]' = []

        with self.lock:
            for sent, latency in self.latencies:
                if sent >= start and sent + latency <= end:
                    out.append(latency)

        out.sort()
        return out

    def _request(self, path:'str') -> 'bool':
        """ Requests one barrier and tells whether it completed.
        """
        request = ModuleCtx.Probe_Database.encode('utf8') + b'\n'

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(ModuleCtx.Probe_Timeout)
            connection.connect(path)
            connection.sendall(request)
            answer = connection.recv(len(ModuleCtx.Barrier_OK))

        out = answer == ModuleCtx.Barrier_OK
        return out

    def _run(self, node:'Node') -> 'None':
        path = os.path.join(node.data_dir, ModuleCtx.Barrier_Socket_Name)

        while self.is_running.is_set():
            sent = time.time()

            # A node that is stopped, frozen or starting has no socket that answers.
            try:
                completed = self._request(path)
            except OSError:
                completed = False

            if completed:
                with self.lock:
                    self.latencies.append((sent, time.time() - sent))

            time.sleep(ModuleCtx.Probe_Interval)

# ################################################################################################################################
# ################################################################################################################################

class MinuteReporter:
    """ Produces a report every minute of a long run, in a thread of its own, and stops the run when the root
    file system runs out of space.
    """

    def __init__(self, env:'HAEnvironment', workload:'Workload', publisher:'TimedPublisher') -> 'None':
        self.env = env
        self.workload = workload
        self.publisher = publisher
        self.probe = BarrierProbe(env)
        self.lock = threading.Lock()
        self.reports:'list[MinuteReport]' = []
        self.is_running = threading.Event()
        self.failure = ''
        self._events:'strlist' = []
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> 'None':
        self.is_running.set()
        self.probe.start()
        self._thread.start()

    def stop(self) -> 'None':
        self.is_running.clear()
        self._thread.join()
        self.probe.stop()

    def add_event(self, event:'str') -> 'None':
        """ Records an event of the run, such as a fault, in the details of the current minute.
        """
        with self.lock:
            self._events.append(event)

    def check(self) -> 'None':
        """ Raises an exception if the run must stop.
        """
        if self.failure:
            raise Exception(self.failure)

    def _count_workload(self) -> 'tuple[int, int]':
        with self.workload.lock:
            out = (len(self.workload.acknowledged), len(self.workload.pulled))
        return out

    def _build_report(self, minute:'int', run_started:'float', started:'float', ended:'float',
        counts_before:'tuple[int, int]', counts_after:'tuple[int, int]') -> 'MinuteReport':

        elapsed = ended - started

        publish_latencies = self.publisher.get_latencies_between(started, ended)
        barrier_latencies = self.probe.get_latencies_between(started, ended)
        errors = self.publisher.count_errors_after(started) - self.publisher.count_errors_after(ended)

        published = counts_after[0] - counts_before[0] + len(publish_latencies)
        delivered = counts_after[1] - counts_before[1]

        record = self.env.consul.read_record()

        out = MinuteReport()
        out.minute = minute
        out.since_start = humanize_duration(ended - run_started)
        out.local_time = datetime.now().strftime('%H:%M:%S')
        out.publishes_per_second = published / elapsed
        out.deliveries_per_second = delivered / elapsed
        out.publish_p99 = get_percentile(publish_latencies, ModuleCtx.Percentile_99)
        out.barrier_p99 = get_percentile(barrier_latencies, ModuleCtx.Percentile_99)
        out.result = ModuleCtx.Result_OK
        out.nodes = []

        assert record is not None, 'No referee record'
        out.generation = record['generation']

        with self.lock:
            out.details = self._events
            self._events = []

        if errors:
            out.details.append(f'{errors} publish errors')

        active_count = 0

        for node in self.env.node_list:

            # A node stopped by a fault in this minute has no resources to report.
            try:
                sample = take_node_sample(node)
            except CalledProcessError:
                out.details.append(f'{node.node_name} not sampled')
                continue

            out.nodes.append(sample)

            if sample.role.startswith('Active'):
                active_count += 1

            for file_name, size in sample.wal_bytes.items():
                if size > ModuleCtx.WAL_Bound_Bytes:
                    out.result = ModuleCtx.Result_Error
                    out.details.append(f'{sample.node_name} {file_name} WAL {size} bytes')

        if active_count > 1:
            out.result = ModuleCtx.Result_Error
            out.details.append('two active nodes')

        free = shutil.disk_usage('/').free

        if free < ModuleCtx.Min_Free_Bytes:
            out.result = ModuleCtx.Result_Error
            out.details.append(f'free space of / is {free} bytes')
            self.failure = f'Free space of / is {free} bytes, below {ModuleCtx.Min_Free_Bytes}'

        return out

    def _run(self) -> 'None':

        minute = 0
        run_started = time.time()
        started = run_started
        counts_before = self._count_workload()

        while self.is_running.is_set():

            # The thread ends within one poll of a stop rather than one whole minute.
            deadline = started + ModuleCtx.Report_Interval

            while self.is_running.is_set() and time.time() < deadline:
                time.sleep(ModuleCtx.Poll_Interval)

            ended = time.time()
            counts_after = self._count_workload()
            minute += 1

            report = self._build_report(minute, run_started, started, ended, counts_before, counts_after)
            self.reports.append(report)

            logger.info('Minute %d\n%s', minute, format_table(self.reports))

            started = ended
            counts_before = counts_after

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class _NodeSeries:
    samples: 'list[NodeSample]' = field(default_factory=list)

# ################################################################################################################################

def get_bound_violations(reports:'list[MinuteReport]') -> 'strlist':
    """ Returns each minute whose result is an error, and each resource of a node container that grew beyond
    its bound from the first report after the warm-up to the last one.
    """
    out:'strlist' = []
    series:'dict[str, _NodeSeries]' = {}

    for report in reports:

        if report.result == ModuleCtx.Result_Error:
            out.append(f'Minute {report.minute} -> {"; ".join(report.details)}')

        if report.minute > ModuleCtx.Warm_Up_Reports:
            for sample in report.nodes:
                if sample.node_name not in series:
                    series[sample.node_name] = _NodeSeries()
                series[sample.node_name].samples.append(sample)

    for node_name, node_series in series.items():

        # A node without two samples after the warm-up shows no growth.
        if len(node_series.samples) < 2:
            continue

        baseline = node_series.samples[0]
        last = node_series.samples[-1]

        memory_limit = baseline.memory_mb * ModuleCtx.Memory_Growth_Factor + ModuleCtx.Memory_Growth_MB

        if last.memory_mb > memory_limit:
            out.append(f'{node_name} memory grew from {baseline.memory_mb:.0f} MB to {last.memory_mb:.0f} MB')

        if last.open_files > baseline.open_files + ModuleCtx.Open_Files_Growth:
            out.append(f'{node_name} open files grew from {baseline.open_files} to {last.open_files}')

        if last.tasks > baseline.tasks + ModuleCtx.Tasks_Growth:
            out.append(f'{node_name} processes and threads grew from {baseline.tasks} to {last.tasks}')

    return out

# ################################################################################################################################

def wait_for_zero_lag(node:'Node') -> 'None':
    """ Waits until the standby confirmed every frame that the active node scanned.
    """
    deadline = time.monotonic() + ModuleCtx.Lag_Timeout
    lag_frames = -1

    while time.monotonic() < deadline:
        report = node.read_role()

        if report is not None:
            lag_frames = get_lag_frames(report)

            if lag_frames == 0:
                return

        time.sleep(ModuleCtx.Poll_Interval)

    raise Exception(f'Replication lag of {node.node_name} still {lag_frames} frames after {ModuleCtx.Lag_Timeout}s')

# ################################################################################################################################
# ################################################################################################################################
