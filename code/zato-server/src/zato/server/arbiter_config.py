# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The timing of the supervision of the worker and the config process, and the records that the arbiter keeps of them.

# stdlib
from dataclasses import dataclass

# Zato
from zato.server.control.hub import ModuleCtx as HubCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import floatnone, list_, strlist

    floatnone = floatnone
    strlist = strlist

    floatlist = list_[float]

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The delay before the first respawn of a process and the ceiling of its exponential growth, in seconds
    Respawn_Delay_Initial = 0.5
    Respawn_Delay_Max     = 30.0

    # A process that terminates more often than this within the window is logged at error level
    Failure_Count_Max = 5
    Failure_Window    = 60.0

    # A worker whose heartbeat is older than this is terminated with SIGKILL, in seconds
    Heartbeat_Threshold = 30.0

    # A worker that has not reported ready this long after its fork is terminated with SIGKILL, in seconds
    Startup_Timeout = 300.0

    # How long an active-standby node waits for its server to exit before it sends SIGKILL to the process group,
    # STOP_GRACE of supervisor.rs in zato_ha_core, and how much earlier than that every drain completes, in seconds
    HA_Stop_Grace  = 10.0
    HA_Stop_Margin = 2.0

    # How long a process has to drain after a drain command, in seconds
    Grace_Period = HA_Stop_Grace - HA_Stop_Margin

    # How long of the grace period a draining worker waits for the requests in progress, and how long it then waits
    # for each subscriber to pause between two batches
    Request_Drain_Period  = 4.0
    Delivery_Pause_Period = 2.0

    # How often a worker records its heartbeat, well below the threshold, in seconds
    Heartbeat_Interval = 1.0

    # How often the arbiter checks the heartbeats and the respawns that are due, in seconds
    Loop_Interval = 0.5

    # How often the arbiter compares the sizes of the log files with their limits, in seconds
    Log_Check_Interval = 10.0

    # The size limit of each file that the REST and access log writers of zato_server_core append to,
    # and how many backups of it the arbiter keeps, as those writers keep in a process that no arbiter started
    Native_Log_Max_Bytes    = 10 * 1024 * 1024
    Native_Log_Backup_Count = 2

    Microseconds_Per_Second = 1_000_000
    Milliseconds_Per_Second = 1000
    Nanoseconds_Per_Microsecond = 1000

    # The option of prctl that delivers a signal to a process when the thread that forked it terminates
    PR_SET_PDEATHSIG = 1

    # The names that ps and top list for each role, which Linux truncates to 15 bytes
    Process_Name_Arbiter = 'zato-arbiter'
    Process_Name_Worker  = 'zato-worker'

    # How many bytes of the wake-up pipe one read drains
    Wake_Read_Size = 4096

    # The prefix of the directory under the server's tmp directory that holds the control bodies of one arbiter
    Body_Dir_Prefix = 'zato-control-'

    Exit_Code_OK           = 0
    Exit_Code_Worker_Error = 1
    Exit_Code_Parent_Gone  = 2

# ################################################################################################################################
# ################################################################################################################################

class ArbiterError(Exception):
    """ The arbiter or a process it forked could not configure a process.
    """

# ################################################################################################################################
# ################################################################################################################################

class WorkerState:
    """ The state of the worker, which the arbiter records.
    """

    # The worker loads its configuration
    Starting = 'starting'

    # The worker serves requests
    Ready = 'ready'

    # The worker completes its requests before it exits
    Draining = 'draining'

    # No worker runs
    Stopped = 'stopped'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ArbiterConfig:
    """ The timing of the supervision of the worker and the config process.
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

    # The files that the REST and access log writers of zato_server_core append to in the worker,
    # each of which the arbiter renames once it reaches its limit
    native_log_files:        'strlist'
    native_log_max_bytes:    'int'
    native_log_backup_count: 'int'

    # The server's tmp directory, which holds the control bodies above the inline size
    tmp_dir: 'str'

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
        out.native_log_files        = []
        out.native_log_max_bytes    = ModuleCtx.Native_Log_Max_Bytes
        out.native_log_backup_count = ModuleCtx.Native_Log_Backup_Count
        out.tmp_dir                 = tmp_dir

        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WorkerContext:
    """ What a forked worker or config process receives from the arbiter.
    """
    slot:       'int'
    generation: 'int'

    # The process's end of its control socket and the directory of the control bodies above the inline size
    control_fd: 'int'
    body_dir:   'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WorkerSlot:
    """ The arbiter's record of the worker or of the config process.
    """
    slot: 'int'

    # The process ID, or 0 when no process runs
    pid: 'int'

    # The moments at which the processes terminated within the failure window
    failure_times: 'floatlist'

    # When the next process is due to start, if one is
    respawn_at: 'floatnone'

    # Whether the arbiter has sent SIGKILL to the current process
    is_killed: 'bool'

    # How the logs name the processes
    label: 'str'

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
