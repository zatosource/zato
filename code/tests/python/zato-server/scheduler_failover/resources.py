# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The resources of the container of the active server - its memory, its open files and its processes and threads -
# sampled at intervals over each period during which one server is active, and the bounds on their growth.

# stdlib
import re
import threading
import time
from dataclasses import dataclass, field
from subprocess import CalledProcessError

# Zato
from failover import docker

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pair import SchedulerServer
    from zato.common.typing_ import strlist

    SchedulerServer = SchedulerServer
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How often the container of the active server is sampled, in seconds.
    Sample_Interval_Seconds = 30

    # How long after a server becomes active its first sample is taken as the baseline, in seconds.
    Warm_Up_Seconds = 60

    # How much the memory may grow over a period - a factor of the baseline and a number of megabytes on top of it.
    Memory_Growth_Factor = 1.5
    Memory_Growth_MB = 100

    # How many open files and how many processes and threads may be added over a period.
    Open_Files_Growth = 50
    Tasks_Growth = 50

    # The command that counts the open files of all the processes of a container.
    Count_Open_Files = 'for fd_dir in /proc/[0-9]*/fd; do ls "$fd_dir"; done 2>/dev/null | wc -l'

# ################################################################################################################################

_bytes_per_unit = {
    'B': 1,
    'KiB': 1024,
    'MiB': 1024 ** 2,
    'GiB': 1024 ** 3,
    'kB': 1000,
    'MB': 1000 ** 2,
    'GB': 1000 ** 3,
}

_bytes_per_mb = 1024 ** 2

_memory_pattern = re.compile(r'^([\d.]+)([A-Za-z]+)')

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Sample:
    """ The resources of one container at one time.
    """
    time: 'float'
    memory_mb: 'float'
    open_files: 'int'
    tasks: 'int'

# ################################################################################################################################

@dataclass
class ActivePeriod:
    """ The samples of one period during which one server is active.
    """
    label: 'str'
    started: 'float'
    samples: 'list[Sample]' = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

def _parse_memory_mb(value:'str') -> 'float':
    """ Turns the memory usage that docker stats reports, such as 512.3MiB, into megabytes.
    """
    match = _memory_pattern.match(value)

    if not match:
        raise Exception(f'Memory usage not recognized `{value}`')

    amount = float(match.group(1))
    unit = match.group(2)

    out = amount * _bytes_per_unit[unit] / _bytes_per_mb
    return out

# ################################################################################################################################

def take_sample(server:'SchedulerServer') -> 'Sample':
    """ Returns the resources of the container of a server at this time.
    """
    container_name = server.server.container_name

    stats = docker('stats', '--no-stream', '--format', '{{.MemUsage}}|{{.PIDs}}', container_name)
    memory_usage, tasks = stats.stdout.strip().split('|')
    memory_used = memory_usage.split('/')[0].strip()

    open_files = docker('exec', container_name, 'sh', '-c', ModuleCtx.Count_Open_Files)

    out = Sample(
        time=time.time(),
        memory_mb=_parse_memory_mb(memory_used),
        open_files=int(open_files.stdout.strip()),
        tasks=int(tasks),
    )

    return out

# ################################################################################################################################
# ################################################################################################################################

class ResourceMonitor:
    """ Samples the container of whichever server is active, in a thread of its own, from one period to the next.
    """

    def __init__(self) -> 'None':
        self.periods:'list[ActivePeriod]' = []
        self.lock = threading.Lock()
        self.is_running = threading.Event()
        self._active:'SchedulerServer | None' = None
        self._thread:'threading.Thread | None' = None

    def set_active(self, server:'SchedulerServer') -> 'None':
        """ Begins the period of a server that has just become active.
        """
        with self.lock:
            self._active = server
            self.periods.append(ActivePeriod(label=server.label, started=time.time()))

    def clear_active(self) -> 'None':
        """ Ends the period of the active server, before a fault is applied to it.
        """
        with self.lock:
            self._active = None

    def start(self) -> 'None':
        self.is_running.set()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> 'None':
        self.is_running.clear()

        if self._thread:
            self._thread.join()

    def _run(self) -> 'None':

        while self.is_running.is_set():

            with self.lock:
                server = self._active

                if self.periods:
                    period = self.periods[-1]
                else:
                    period = None

            if server and period:

                # A fault may stop the container while it is sampled ..
                try:
                    sample = take_sample(server)
                except CalledProcessError:
                    sample = None

                # .. or end the period while the sample was taken, and in both cases the sample is not kept.
                with self.lock:
                    if sample and self._active is server:
                        period.samples.append(sample)

            time.sleep(ModuleCtx.Sample_Interval_Seconds)

# ################################################################################################################################
# ################################################################################################################################

def get_resource_growth(periods:'list[ActivePeriod]') -> 'strlist':
    """ Returns each resource that grew beyond its bound within a period, from the first sample after the warm-up to the last one.
    """
    out:'strlist' = []

    for period in periods:

        warm_samples:'list[Sample]' = []

        for sample in period.samples:
            if sample.time - period.started >= ModuleCtx.Warm_Up_Seconds:
                warm_samples.append(sample)

        # A period without two samples after its warm-up shows no growth.
        if len(warm_samples) < 2:
            continue

        baseline = warm_samples[0]
        last = warm_samples[-1]

        memory_limit = baseline.memory_mb * ModuleCtx.Memory_Growth_Factor + ModuleCtx.Memory_Growth_MB

        if last.memory_mb > memory_limit:
            out.append(f'Server {period.label} memory grew from {baseline.memory_mb:.0f} MB to {last.memory_mb:.0f} MB')

        if last.open_files > baseline.open_files + ModuleCtx.Open_Files_Growth:
            out.append(f'Server {period.label} open files grew from {baseline.open_files} to {last.open_files}')

        if last.tasks > baseline.tasks + ModuleCtx.Tasks_Growth:
            out.append(f'Server {period.label} processes and threads grew from {baseline.tasks} to {last.tasks}')

    return out

# ################################################################################################################################
# ################################################################################################################################
