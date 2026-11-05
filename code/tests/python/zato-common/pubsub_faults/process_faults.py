# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults of a single process - one Zato server with its cleanup process in a transient systemd scope
# of the user, whose CPU, memory, processes and file descriptors are limited, which is frozen in a duty cycle,
# whose file system calls are delayed and failed, and whose clock is skewed.

# stdlib
import os
import resource
import signal
import subprocess
from time import monotonic

# gevent
from gevent import sleep, spawn

# Zato
from faults import Fault, Total_Loss
from remote import write_control_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, intlist, strlist

    intpair  = tuple[int, int]
    pathpair = tuple[str, str]
    pathlist = list[pathpair]
    limitmap = dict[int, intpair]

# ################################################################################################################################
# ################################################################################################################################

# The root of the cgroup hierarchy.
_cgroup_root = '/sys/fs/cgroup'

# The period of cpu.max and the smallest share of one CPU that a scope is limited to, in microseconds.
_cpu_period_usec = 100_000
_min_cpu_quota_usec = 1000
_usec_per_second = 1_000_000

# How many file descriptors a process may open beyond those it has open when the fault is applied.
_fd_headroom = 4

# How long each step of the delay of a file system call is at each percentage of the severity,
# and how long a call is delayed at a total loss, in microseconds.
_fs_delay_usec_per_level = 1000
_fs_total_loss_delay_usec = 10_000_000

# The kinds of file system faults of item 15.4.
Filesystem_Delay  = 'delay'
Filesystem_EIO    = 'eio'
Filesystem_ENOSPC = 'enospc'

Filesystem_Kinds = [Filesystem_Delay, Filesystem_EIO, Filesystem_ENOSPC]

# The kinds of clock faults of item 15.9, with the offsets that libfaketime reads from its timestamp file.
Clock_Ahead  = 'ahead'
Clock_Behind = 'behind'
Clock_Jumps  = 'jumps'
Clock_Slow   = 'slow'

Clock_Kinds = [Clock_Ahead, Clock_Behind, Clock_Jumps, Clock_Slow]

Clock_No_Offset = '+0'

_clock_offsets = {
    Clock_Ahead: '+120',
    Clock_Behind: '-120',
    Clock_Slow: '+0 x0.8',
}

# How often a clock that jumps changes its direction, in seconds.
_clock_jump_seconds = 20

# ################################################################################################################################
# ################################################################################################################################

def _remaining(level:'int') -> 'float':
    """ The share of a resource that is left at a severity level.
    """
    out = (Total_Loss - level) / Total_Loss
    return out

# ################################################################################################################################

def _get_parent_pid(pid:'int') -> 'int':

    with open(f'/proc/{pid}/stat') as stat_file:
        stat = stat_file.read()

    # The name of the process is in parentheses and may contain spaces, which is why the fields are read after it.
    name_end = stat.rindex(')')
    fields = stat[name_end + 2:].split()

    out = int(fields[1])
    return out

# ################################################################################################################################
# ################################################################################################################################

class Scope:
    """ The transient systemd scope of the user that one Zato server runs in, with its cgroup.
    """

    def __init__(self, unit:'str') -> 'None':
        self.unit = unit
        self.unit_name = f'{unit}.scope'
        self._cgroup_dir = ''

# ################################################################################################################################

    @property
    def cgroup_dir(self) -> 'str':
        if not self._cgroup_dir:
            command = ['systemctl', '--user', 'show', '--property=ControlGroup', '--value', self.unit_name]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            control_group = result.stdout.strip()
            self._cgroup_dir = _cgroup_root + control_group

        return self._cgroup_dir

# ################################################################################################################################

    def get_command_prefix(self) -> 'strlist':
        """ What starts a process in the scope - the CPU weight enables the cpu controller, whose cpu.max
        the faults write to, and the other two properties account for the memory and the processes of the scope.
        """
        out = [
            'systemd-run', '--user', '--scope', '--quiet', '--collect', f'--unit={self.unit}',
            '--property=CPUWeight=100', '--property=MemoryAccounting=yes', '--property=TasksAccounting=yes',
        ]
        return out

# ################################################################################################################################

    def read(self, name:'str') -> 'str':
        path = os.path.join(self.cgroup_dir, name)

        with open(path) as cgroup_file:
            out = cgroup_file.read().strip()

        return out

# ################################################################################################################################

    def write(self, name:'str', value:'str') -> 'None':
        path = os.path.join(self.cgroup_dir, name)

        with open(path, 'w') as cgroup_file:
            _ = cgroup_file.write(value)

# ################################################################################################################################

    def read_cpu_usage_usec(self) -> 'int':
        stat = self.read('cpu.stat')

        for line in stat.splitlines():
            name, value = line.split()
            if name == 'usage_usec':
                out = int(value)
                break
        else:
            raise Exception(f'No usage_usec in cpu.stat of {self.unit}')

        return out

# ################################################################################################################################

    def get_pids(self) -> 'intlist':
        out:'intlist' = []
        procs = self.read('cgroup.procs')

        for line in procs.splitlines():
            out.append(int(line))

        return out

# ################################################################################################################################

    def is_active(self) -> 'bool':
        command = ['systemctl', '--user', 'is-active', '--quiet', self.unit_name]
        result = subprocess.run(command, check=False)

        out = result.returncode == 0
        return out

# ################################################################################################################################

    def stop(self) -> 'None':
        if self.is_active():
            _ = subprocess.run(['systemctl', '--user', 'stop', self.unit_name], check=False)

# ################################################################################################################################
# ################################################################################################################################

class ScopeCPUFault(Fault):
    """ Item 15.7 - cpu.max limits the scope of the server to a share of the CPU time it used in the baseline,
    and a total loss freezes the scope.
    """
    name = 'server-cpu'

    def __init__(self, scope:'Scope') -> 'None':
        self.scope = scope
        self.baseline_cpus = 0.0
        self._baseline_started = 0.0
        self._baseline_usage = 0

# ################################################################################################################################

    def start_baseline(self) -> 'None':
        self._baseline_started = monotonic()
        self._baseline_usage = self.scope.read_cpu_usage_usec()

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        elapsed = monotonic() - self._baseline_started
        used_usec = self.scope.read_cpu_usage_usec() - self._baseline_usage
        used_seconds = used_usec / _usec_per_second

        self.baseline_cpus = used_seconds / elapsed

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':

        if level == Total_Loss:
            self.scope.write('cgroup.freeze', '1')

        else:
            quota = int(self.baseline_cpus * _remaining(level) * _cpu_period_usec)
            quota = max(quota, _min_cpu_quota_usec)
            self.scope.write('cpu.max', f'{quota} {_cpu_period_usec}')

# ################################################################################################################################

    def remove(self) -> 'None':
        if self.scope.is_active():
            self.scope.write('cgroup.freeze', '0')
            self.scope.write('cpu.max', f'max {_cpu_period_usec}')

# ################################################################################################################################
# ################################################################################################################################

class ServerFreezeFault(Fault):
    """ Item 15.7 - the server, without its cleanup process, is stopped with SIGSTOP and resumed with SIGCONT
    in a duty cycle, for frozen_seconds in each period_seconds.
    """

    def __init__(self, scope:'Scope', period_seconds:'float', frozen_seconds:'float') -> 'None':
        self.scope = scope
        self.period_seconds = period_seconds
        self.frozen_seconds = frozen_seconds
        self.name = f'freeze-server-{frozen_seconds:g}s-every-{period_seconds:g}s'

        self.pid = 0
        self._greenlets:'anylist' = []

# ################################################################################################################################

    def _get_server_pid(self) -> 'int':
        """ The server is the process of the scope whose parent is outside of it.
        """
        pids = self.scope.get_pids()

        for pid in pids:
            parent_pid = _get_parent_pid(pid)
            if parent_pid not in pids:
                out = pid
                break
        else:
            raise Exception(f'No server process in {self.scope.unit}')

        return out

# ################################################################################################################################

    def _freeze(self) -> 'None':
        running_seconds = self.period_seconds - self.frozen_seconds

        while True:
            os.kill(self.pid, signal.SIGSTOP)
            sleep(self.frozen_seconds)
            os.kill(self.pid, signal.SIGCONT)
            sleep(running_seconds)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        self.pid = self._get_server_pid()

        greenlet = spawn(self._freeze)
        self._greenlets.append(greenlet)

# ################################################################################################################################

    def remove(self) -> 'None':

        if not self.pid:
            return

        for greenlet in self._greenlets:
            greenlet.kill()

        self._greenlets = []
        os.kill(self.pid, signal.SIGCONT)
        self.pid = 0

# ################################################################################################################################
# ################################################################################################################################

class ScopeMemoryFault(Fault):
    """ Item 15.8 - memory.high below what the scope of the server uses causes reclaim stalls. Its total loss,
    in which the OOM killer ends the server, is what the crash suite covers with SIGKILL.
    """
    name = 'server-memory'

    def __init__(self, scope:'Scope') -> 'None':
        self.scope = scope
        self.baseline_bytes = 0

# ################################################################################################################################

    def end_baseline(self) -> 'None':
        current = self.scope.read('memory.current')
        self.baseline_bytes = int(current)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        limit = int(self.baseline_bytes * _remaining(level))
        self.scope.write('memory.high', f'{limit}')

# ################################################################################################################################

    def remove(self) -> 'None':
        if self.scope.is_active():
            self.scope.write('memory.high', 'max')

# ################################################################################################################################
# ################################################################################################################################

class TasksFault(Fault):
    """ Item 15.10 - pids.max at the number of tasks the scope has, so that the server can start no thread
    and no process.
    """
    name = 'server-tasks'

    def __init__(self, scope:'Scope') -> 'None':
        self.scope = scope

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        current = self.scope.read('pids.current')
        self.scope.write('pids.max', current)

# ################################################################################################################################

    def remove(self) -> 'None':
        if self.scope.is_active():
            self.scope.write('pids.max', 'max')

# ################################################################################################################################
# ################################################################################################################################

class FileDescriptorFault(Fault):
    """ Item 15.10 - the soft limit of the file descriptors of each process of the scope a few above
    the number it has open, so that the processes can open almost no file and no connection.
    The hard limit stays, which is what lets the soft limit return to what it was.
    """
    name = 'server-file-descriptors'

    def __init__(self, scope:'Scope') -> 'None':
        self.scope = scope
        self.limits:'limitmap' = {}

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':

        for pid in self.scope.get_pids():
            soft, hard = resource.prlimit(pid, resource.RLIMIT_NOFILE)
            self.limits[pid] = (soft, hard)

            open_fds = os.listdir(f'/proc/{pid}/fd')
            limit = len(open_fds) + _fd_headroom

            _ = resource.prlimit(pid, resource.RLIMIT_NOFILE, (limit, hard))

# ################################################################################################################################

    def remove(self) -> 'None':

        for pid, limits in self.limits.items():
            if os.path.exists(f'/proc/{pid}'):
                _ = resource.prlimit(pid, resource.RLIMIT_NOFILE, limits)

        self.limits = {}

# ################################################################################################################################
# ################################################################################################################################

class FilesystemFault(Fault):
    """ Item 15.4 - the preloaded library delays the writes and the fsync calls on the files under a prefix,
    or fails a percentage of them with EIO or ENOSPC. Each target is one control file that the library
    of one or more processes reads, with the prefix of the files that the fault applies to.
    """

    def __init__(self, kind:'str', targets:'pathlist') -> 'None':
        self.kind = kind
        self.targets = targets
        self.name = f'filesystem-{kind}'

# ################################################################################################################################

    def _write_controls(self, settings:'str') -> 'None':
        for control_path, prefix in self.targets:
            write_control_file(control_path, f'prefix={prefix}\n{settings}')

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':

        # A delay grows with the level and is the longest at a total loss ..
        if self.kind == Filesystem_Delay:
            if level == Total_Loss:
                delay_usec = _fs_total_loss_delay_usec
            else:
                delay_usec = level * _fs_delay_usec_per_level
            settings = f'delay_us={delay_usec}\n'

        # .. whereas an error is returned by that percentage of the calls.
        else:
            error_name = self.kind.upper()
            settings = f'error_percent={level}\nerrno={error_name}\n'

        self._write_controls(settings)

# ################################################################################################################################

    def remove(self) -> 'None':
        self._write_controls('')

# ################################################################################################################################
# ################################################################################################################################

class ClockFault(Fault):
    """ Item 15.9 - libfaketime in the processes of the scope reads its offset from a file, which moves their clock
    ahead, behind, back and forth, or slows it down, while their monotonic clock stays as it is.
    """

    def __init__(self, kind:'str', timestamp_file:'str') -> 'None':
        self.kind = kind
        self.timestamp_file = timestamp_file
        self.name = f'clock-{kind}'
        self._greenlets:'anylist' = []

# ################################################################################################################################

    def _jump(self) -> 'None':
        offsets = [_clock_offsets[Clock_Ahead], _clock_offsets[Clock_Behind]]
        index = 0

        while True:
            offset = offsets[index]
            write_control_file(self.timestamp_file, offset)

            index = 1 - index
            sleep(_clock_jump_seconds)

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':

        if self.kind == Clock_Jumps:
            greenlet = spawn(self._jump)
            self._greenlets.append(greenlet)

        else:
            offset = _clock_offsets[self.kind]
            write_control_file(self.timestamp_file, offset)

# ################################################################################################################################

    def remove(self) -> 'None':

        for greenlet in self._greenlets:
            greenlet.kill()

        self._greenlets = []
        write_control_file(self.timestamp_file, Clock_No_Offset)

# ################################################################################################################################
# ################################################################################################################################
