# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of the resources of the PostgreSQL container - its disk, its CPU, its memory, its network link
# and its processes. Each fault applies at a severity level, which is the percentage of the resource taken away
# from what the container used in the baseline phase, or a total loss of the resource.

# stdlib
import os
import signal
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from container import Container
from zato.common.test.pubsub_database import connect

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anylist, callable_, strfloatdict

# ################################################################################################################################
# ################################################################################################################################

# The severity levels of item 15.2 - the percentage of a resource taken away, the last one being its total loss.
Total_Loss = 100
Severity_Levels = [10, 20, 50, 90, Total_Loss]

# The smallest limits that io.max is set to, which a total loss of the disk uses as well.
_min_bytes_per_second = 4096
_min_operations_per_second = 1

# The period of cpu.max and the smallest share of one CPU that a container is limited to, in microseconds.
_cpu_period_usec = 100_000
_min_cpu_quota_usec = 1000

# How many microseconds one second has.
_usec_per_second = 1_000_000

# How long a total loss of memory waits for the OOM killer to end a process, in seconds, and how often it checks.
_oom_kill_timeout = 60
_oom_poll_seconds = 0.1

# How long one step of the delay of a packet is at each percentage of the severity, in milliseconds,
# and the delay that reordering needs.
_delay_ms_per_level = 10
_reorder_delay_ms = 10

# The application name of the sessions of the faults themselves, which keeps them out of the faults they apply.
Fault_Application_Name = 'zato-pubsub-test-fault'

# The kinds of packet faults of item 15.5.
Packet_Loss      = 'loss'
Packet_Delay     = 'delay'
Packet_Reorder   = 'reorder'
Packet_Duplicate = 'duplicate'
Packet_Corrupt   = 'corrupt'

Packet_Kinds = [Packet_Loss, Packet_Delay, Packet_Reorder, Packet_Duplicate, Packet_Corrupt]

# The processes of the PostgreSQL container that item 15.7 freezes, by the backend type that PostgreSQL reports,
# and the process of the test that it freezes as well.
Freeze_WAL_Writer           = 'walwriter'
Freeze_Autovacuum_Launcher  = 'autovacuum launcher'
Freeze_Client_Backend       = 'client backend'
Freeze_Cleanup              = 'cleanup'

# The duty cycles of the freezes - how long each period is and how long the process is frozen in it, in seconds.
Duty_Cycles = [(1, 0.2), (60, 5)]

# Where a freezing script in the container records its process identifier.
_freeze_pid_file = '/tmp/zato-pubsub-test-freeze.pid'

# ################################################################################################################################
# ################################################################################################################################

class Fault:
    """ One fault of one resource. A fault that needs no baseline ignores it, and removing a fault
    that is not applied changes nothing, so a test removes each fault in any case.
    """
    name = ''

    # The shortest time that the fault lasts once applied, in seconds.
    min_duration = 0

# ################################################################################################################################

    def start_baseline(self) -> 'None':
        pass

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        pass

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        raise Exception(f'Fault {self.name} does not implement apply')

# ################################################################################################################################

    def remove(self) -> 'None':
        raise Exception(f'Fault {self.name} does not implement remove')

# ################################################################################################################################
# ################################################################################################################################

def get_label(fault_name:'str', level:'int') -> 'str':
    """ What the reports of a run name the fault and its severity level with.
    """
    if level == Total_Loss:
        out = f'{fault_name} total loss'
    else:
        out = f'{fault_name} {level}%'

    return out

# ################################################################################################################################

def _remaining(level:'int') -> 'float':
    """ The share of a resource that is left at a severity level.
    """
    out = (Total_Loss - level) / Total_Loss
    return out

# ################################################################################################################################
# ################################################################################################################################

class DiskFault(Fault):
    """ Item 15.3 - io.max limits the bandwidth and the operations per second of the container on its disk.
    """
    name = 'disk'

    def __init__(self, container:'Container', device:'str') -> 'None':
        self.container = container
        self.device = device
        self.baseline:'strfloatdict' = {}
        self._baseline_started = 0.0
        self._baseline_stat:'any_' = None

# ################################################################################################################################

    def start_baseline(self) -> 'None':
        self._baseline_started = monotonic()
        self._baseline_stat = self.container.read_io_stat(self.device)

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        elapsed = monotonic() - self._baseline_started
        stat = self.container.read_io_stat(self.device)

        for name, value in stat.items():
            used = value - self._baseline_stat[name]
            self.baseline[name] = used / elapsed

# ################################################################################################################################

    def _get_limit(self, name:'str', remaining:'float', minimum:'int') -> 'int':
        limit = int(self.baseline[name] * remaining)

        out = max(limit, minimum)
        return out

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':

        # A total loss leaves the smallest limits there are ..
        if level == Total_Loss:
            read_bytes = _min_bytes_per_second
            write_bytes = _min_bytes_per_second
            read_operations = _min_operations_per_second
            write_operations = _min_operations_per_second

        # .. and each other level takes away its share of what the baseline used.
        else:
            remaining = _remaining(level)
            read_bytes = self._get_limit('rbytes', remaining, _min_bytes_per_second)
            write_bytes = self._get_limit('wbytes', remaining, _min_bytes_per_second)
            read_operations = self._get_limit('rios', remaining, _min_operations_per_second)
            write_operations = self._get_limit('wios', remaining, _min_operations_per_second)

        value = f'{self.device} rbps={read_bytes} wbps={write_bytes} riops={read_operations} wiops={write_operations}'
        self.container.write_cgroup('io.max', value)

# ################################################################################################################################

    def remove(self) -> 'None':
        self.container.write_cgroup('io.max', f'{self.device} rbps=max wbps=max riops=max wiops=max')

# ################################################################################################################################
# ################################################################################################################################

class CPUFault(Fault):
    """ Item 15.7 - cpu.max limits the container to a share of the CPU time it used in the baseline,
    and a total loss freezes all of its processes.
    """
    name = 'cpu'

    def __init__(self, container:'Container') -> 'None':
        self.container = container
        self.baseline_cpus = 0.0
        self._baseline_started = 0.0
        self._baseline_usage = 0

# ################################################################################################################################

    def start_baseline(self) -> 'None':
        self._baseline_started = monotonic()
        self._baseline_usage = self.container.read_cpu_usage_usec()

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        elapsed = monotonic() - self._baseline_started
        used_usec = self.container.read_cpu_usage_usec() - self._baseline_usage
        used_seconds = used_usec / _usec_per_second

        self.baseline_cpus = used_seconds / elapsed

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':

        if level == Total_Loss:
            self.container.pause()

        else:
            quota = int(self.baseline_cpus * _remaining(level) * _cpu_period_usec)
            quota = max(quota, _min_cpu_quota_usec)
            self.container.write_cgroup('cpu.max', f'{quota} {_cpu_period_usec}')

# ################################################################################################################################

    def remove(self) -> 'None':

        if self.container.is_paused():
            self.container.unpause()

        self.container.write_cgroup('cpu.max', f'max {_cpu_period_usec}')

# ################################################################################################################################
# ################################################################################################################################

class MemoryFault(Fault):
    """ Item 15.8 - memory.high below what the container uses causes reclaim stalls, and a total loss sets memory.max
    below it for as long as it takes the OOM killer to end one backend, after which PostgreSQL ends every backend
    and runs crash recovery.
    """
    name = 'memory'

    def __init__(self, container:'Container') -> 'None':
        self.container = container
        self.baseline_bytes = 0
        self.oom_kills = 0

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        self.baseline_bytes = self.container.read_memory_current()

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':

        # The OOM killer ends a backend and never the postmaster, which would take the container with it ..
        if level == Total_Loss:
            self.container.protect_from_oom_killer()
            kills_before = self.container.read_oom_kills()

            limit = self.baseline_bytes // 2
            self.container.write_cgroup('memory.max', f'{limit}')

            # .. the limit stays only until a process is ended, since the shared memory alone
            # .. would keep the container above it after the crash recovery ..
            deadline = monotonic() + _oom_kill_timeout

            while self.container.read_oom_kills() == kills_before:
                assert monotonic() < deadline, f'No OOM kill in {self.container.name} after {_oom_kill_timeout}s'
                sleep(_oom_poll_seconds)

            self.oom_kills = self.container.read_oom_kills() - kills_before
            self.container.write_cgroup('memory.max', 'max')

        # .. whereas the other levels keep the container short of memory for the whole duration of the fault.
        else:
            limit = int(self.baseline_bytes * _remaining(level))
            self.container.write_cgroup('memory.high', f'{limit}')

# ################################################################################################################################

    def remove(self) -> 'None':
        self.container.write_cgroup('memory.high', 'max')
        self.container.write_cgroup('memory.max', 'max')

# ################################################################################################################################
# ################################################################################################################################

def _get_netem_parameters(kind:'str', level:'int') -> 'str':
    """ The netem parameters of one kind of packet fault at one severity level.
    """
    if level == Total_Loss:
        out = 'loss 100%'

    elif kind == Packet_Loss:
        out = f'loss {level}%'

    elif kind == Packet_Delay:
        delay = level * _delay_ms_per_level
        out = f'delay {delay}ms {level}ms distribution normal'

    elif kind == Packet_Reorder:
        out = f'delay {_reorder_delay_ms}ms reorder {level}% 50%'

    elif kind == Packet_Duplicate:
        out = f'duplicate {level}%'

    elif kind == Packet_Corrupt:
        out = f'corrupt {level}%'

    # .. anything else is not a kind of packet fault.
    else:
        raise Exception(f'Unknown packet fault `{kind}`')

    return out

# ################################################################################################################################
# ################################################################################################################################

class PacketFault(Fault):
    """ Item 15.5 - netem on the interface of the container, in both directions - on what leaves the container
    and, through an ifb device, on what enters it.
    """

    def __init__(self, container:'Container', kind:'str') -> 'None':
        self.container = container
        self.kind = kind
        self.name = f'packet-{kind}'

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        parameters = _get_netem_parameters(self.kind, level)

        script = '; '.join([
            'set -e',
            f'tc qdisc add dev eth0 root netem {parameters}',
            'ip link add ifb0 type ifb',
            'ip link set ifb0 up',
            'tc qdisc add dev eth0 handle ffff: ingress',
            'tc filter add dev eth0 parent ffff: matchall action mirred egress redirect dev ifb0',
            f'tc qdisc add dev ifb0 root netem {parameters}',
        ])

        _ = self.container.run_tc(script)

# ################################################################################################################################

    def remove(self) -> 'None':
        script = '; '.join([
            'tc qdisc del dev eth0 root 2>/dev/null',
            'tc qdisc del dev eth0 ingress 2>/dev/null',
            'ip link del ifb0 2>/dev/null',
            'true',
        ])

        _ = self.container.run_tc(script)

# ################################################################################################################################
# ################################################################################################################################

def _find_backend_pid(database:'PubSubDatabase', backend_type:'str') -> 'int':
    """ The process identifier of one process of the database of the given backend type, as the container sees it.
    """
    query = 'select pid from pg_stat_activity where backend_type = %s and pid <> pg_backend_pid() ' + \
        'and coalesce(application_name, %s) <> %s order by pid limit 1'

    connection = connect(database)

    try:
        cursor = connection.cursor()
        cursor.execute(query, (backend_type, '', Fault_Application_Name))
        row = cursor.fetchone()
    finally:
        connection.close()

    assert row, f'No process of type `{backend_type}` in the database'

    out = row[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class FreezeFault(Fault):
    """ Item 15.7 - one process is stopped with SIGSTOP and resumed with SIGCONT in a duty cycle, for frozen_seconds
    in each period_seconds - a process of the PostgreSQL container or the cleanup process of the test.
    """

    def __init__(
        self,
        database:'PubSubDatabase',
        container:'Container',
        target:'str',
        period_seconds:'float',
        frozen_seconds:'float',
        get_cleanup_pid:'callable_',
        ) -> 'None':
        self.database = database
        self.container = container
        self.target = target
        self.period_seconds = period_seconds
        self.frozen_seconds = frozen_seconds
        self.get_cleanup_pid = get_cleanup_pid

        target_name = target.replace(' ', '-')
        self.name = f'freeze-{target_name}-{frozen_seconds:g}s-every-{period_seconds:g}s'

        self.pid = 0
        self._greenlets:'anylist' = []

# ################################################################################################################################

    def _freeze_cleanup(self) -> 'None':
        """ The duty cycle of the cleanup process, which runs in the test process.
        """
        running_seconds = self.period_seconds - self.frozen_seconds

        while True:
            os.kill(self.pid, signal.SIGSTOP)
            sleep(self.frozen_seconds)
            os.kill(self.pid, signal.SIGCONT)
            sleep(running_seconds)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        running_seconds = self.period_seconds - self.frozen_seconds

        # The cleanup process is a child of the test ..
        if self.target == Freeze_Cleanup:
            self.pid = self.get_cleanup_pid()
            greenlet = spawn(self._freeze_cleanup)
            self._greenlets.append(greenlet)

        # .. whereas the processes of PostgreSQL are frozen by a script in their container,
        # .. which records its own process identifier so that the fault can be removed.
        else:
            self.pid = _find_backend_pid(self.database, self.target)

            script = f'echo $$ > {_freeze_pid_file}; while true; do kill -STOP {self.pid}; ' + \
                f'sleep {self.frozen_seconds}; kill -CONT {self.pid}; sleep {running_seconds}; done'

            _ = self.container.start_script(script)

# ################################################################################################################################

    def remove(self) -> 'None':

        if not self.pid:
            return

        if self.target == Freeze_Cleanup:
            for greenlet in self._greenlets:
                greenlet.kill()
            self._greenlets = []
            os.kill(self.pid, signal.SIGCONT)

        # A backend that the fault froze may have ended in the meantime, which is why its resumption may fail.
        else:
            script = f'kill $(cat {_freeze_pid_file}) 2>/dev/null; kill -CONT {self.pid} 2>/dev/null; true'
            _ = self.container.execute(script)

        self.pid = 0

# ################################################################################################################################
# ################################################################################################################################
