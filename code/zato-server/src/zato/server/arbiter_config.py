# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The timing of the supervision of the workers and the records that the arbiter keeps of its processes.

# stdlib
from dataclasses import dataclass
from tempfile import gettempdir

# Zato
from zato.common.worker_count import ServerWorkers
from zato.server.control.hub import ModuleCtx as HubCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from socket import socket
    from zato.common.typing_ import callable_, floatnone, intnone, list_, strlist, strnone

    callable_ = callable_
    floatnone = floatnone
    intnone = intnone
    socket = socket
    strlist = strlist
    strnone = strnone

    floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The delay before the first respawn of a slot and the ceiling of its exponential growth, in seconds
    Respawn_Delay_Initial = 0.5
    Respawn_Delay_Max     = 30.0

    # A slot whose workers terminate more often than this within the window is logged at error level
    Failure_Count_Max = 5
    Failure_Window    = 60.0

    # A worker whose heartbeat is older than this is terminated with SIGKILL, in seconds
    Heartbeat_Threshold = 30.0

    # A worker that has not reported ready this long after its fork is terminated with SIGKILL, in seconds
    Startup_Timeout = 300.0

    # How long the workers have to complete their requests after a drain command, in seconds
    Grace_Period = 30.0

    # How often the arbiter checks the heartbeats and the respawns that are due, in seconds
    Loop_Interval = 0.5

    # How often the arbiter compares the sizes of the log files with their limits, in seconds
    Log_Check_Interval = 10.0

    # The size limit of each file that the REST and access log writers of zato_server_core append to,
    # and how many backups of it the arbiter keeps, as those writers keep in a server with one process
    Native_Log_Max_Bytes    = 10 * 1024 * 1024
    Native_Log_Backup_Count = 2

    Microseconds_Per_Second = 1_000_000
    Milliseconds_Per_Second = 1000
    Nanoseconds_Per_Microsecond = 1000

    # The option of prctl that delivers a signal to a process when the thread that forked it terminates
    PR_SET_PDEATHSIG = 1

    # The names that ps and top list for each role, which Linux truncates to 15 bytes
    Process_Name_Arbiter = 'zato-arbiter'
    Process_Name_Worker  = 'zato-worker-{}'
    Process_Name_Writer  = 'zato-writer'

    # How many bytes of the wake-up pipe one read drains
    Wake_Read_Size = 4096

    # The prefix of the directory under the server's tmp directory that holds the control bodies of one arbiter
    Body_Dir_Prefix = 'zato-control-'

    # The prefix of the directory that holds the listening socket of the pub/sub writer process, and the name of the socket
    Writer_Dir_Prefix  = 'zato-writer-'
    Writer_Socket_Name = 'pubsub-writer.sock'

    # The slot number by which the logs name the pub/sub writer process, which has no slot in the region
    Writer_Slot = -1

    # The slot whose worker performs the startup writes, before which no other slot starts
    First_Slot = 0

    # How long a worker waits for the reply of the writer to one item, restarts of the writer included, in seconds
    Writer_Deadline = 60.0

    # How long the trace of a fully delivered message is kept at least after its receipt, in seconds,
    # which exceeds the deadline of the writer and the duration of one commit
    Trace_Grace_Seconds = 600

    Exit_Code_OK           = 0
    Exit_Code_Worker_Error = 1
    Exit_Code_Parent_Gone  = 2

# ################################################################################################################################
# ################################################################################################################################

class ArbiterError(Exception):
    """ The arbiter or a worker it forked could not configure a process.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ArbiterConfig:
    """ The timing of the supervision of the workers.
    """
    respawn_delay_initial: 'float'
    respawn_delay_max:     'float'
    failure_count_max:     'int'
    failure_window:        'float'
    heartbeat_threshold:   'float'
    startup_timeout:       'float'
    grace_period:          'float'
    loop_interval:         'float'
    log_check_interval:    'float'
    query_timeout:         'float'
    writer_deadline:       'float'
    trace_grace_seconds:   'int'

    # The files that the REST and access log writers of zato_server_core append to in every worker,
    # each of which the arbiter renames once it reaches its limit
    native_log_files:        'strlist'
    native_log_max_bytes:    'int'
    native_log_backup_count: 'int'

    # The server's tmp directory, which holds the control bodies above the inline size
    tmp_dir: 'str'

    # The directory in which the arbiter creates the directory of the listening socket of the writer,
    # a short path by default, because the kernel limits the path of a Unix socket to 107 bytes
    socket_dir: 'str'

    # The file of cgroup v2 that holds the CPU quota of the server, which decides whether the workers are pinned to CPUs
    cpu_max_path: 'str'

    @staticmethod
    def from_defaults(tmp_dir:'str') -> 'ArbiterConfig':
        out = ArbiterConfig()

        out.respawn_delay_initial   = ModuleCtx.Respawn_Delay_Initial
        out.respawn_delay_max       = ModuleCtx.Respawn_Delay_Max
        out.failure_count_max       = ModuleCtx.Failure_Count_Max
        out.failure_window          = ModuleCtx.Failure_Window
        out.heartbeat_threshold     = ModuleCtx.Heartbeat_Threshold
        out.startup_timeout         = ModuleCtx.Startup_Timeout
        out.grace_period            = ModuleCtx.Grace_Period
        out.loop_interval           = ModuleCtx.Loop_Interval
        out.log_check_interval      = ModuleCtx.Log_Check_Interval
        out.query_timeout           = HubCtx.Query_Timeout
        out.writer_deadline         = ModuleCtx.Writer_Deadline
        out.trace_grace_seconds     = ModuleCtx.Trace_Grace_Seconds
        out.native_log_files        = []
        out.native_log_max_bytes    = ModuleCtx.Native_Log_Max_Bytes
        out.native_log_backup_count = ModuleCtx.Native_Log_Backup_Count
        out.tmp_dir                 = tmp_dir
        out.socket_dir              = gettempdir()
        out.cpu_max_path            = ServerWorkers.CPU_Max_Path

        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WorkerContext:
    """ What a forked worker receives from the arbiter.
    """
    slot:       'int'
    generation: 'int'

    # The worker's end of its control socket and the directory of the control bodies above the inline size
    control_fd: 'int'
    body_dir:   'str'

    # The address of the pub/sub writer process, if the server runs one, and how long a worker waits for its replies
    writer_address:  'strnone'
    writer_deadline: 'float'

    # The CPU to which the worker pins itself, if the workers are pinned
    cpu: 'intnone'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WorkerSlot:
    """ The arbiter's record of one slot and of the worker that runs in it.
    """
    slot: 'int'

    # The process ID of the worker, or 0 when the slot has none
    pid: 'int'

    # The moments at which the workers of the slot terminated within the failure window
    failure_times: 'floatlist'

    # When the next worker of the slot is due to start, if one is
    respawn_at: 'floatnone'

    # Whether the arbiter has sent SIGKILL to the current worker
    is_killed: 'bool'

    # How the logs name the processes of the slot
    label: 'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WriterProcess:
    """ The arbiter's record of the pub/sub writer process and of the listening socket that the writer serves.
    """
    main:     'callable_'
    address:  'str'
    listener: 'socket'

    # The private directory of the listening socket, which the arbiter removes on stop
    socket_dir: 'str'

    # The writer is supervised with the backoff of a slot
    process: 'WorkerSlot'

# ################################################################################################################################
# ################################################################################################################################

def new_worker_slot(slot:'int', label:'str') -> 'WorkerSlot':
    out = WorkerSlot()

    out.slot = slot
    out.pid = 0
    out.failure_times = []
    out.respawn_at = None
    out.is_killed = False
    out.label = label

    return out

# ################################################################################################################################
# ################################################################################################################################
