# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The operations through which a worker process states to its arbiter that it is alive, follows the log files
# that the arbiter renamed, and terminates together with the arbiter.

# stdlib
import ctypes
import os
import signal
from time import monotonic_ns

# Zato
from zato.common.util.log_rotation import reopen_worker_handlers
from zato.server.arbiter_config import ArbiterError, ModuleCtx
from zato_server_core.zato_server_core import reopen_logs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato_ipc_core.zato_ipc_core import SharedRegion

    SharedRegion = SharedRegion

# ################################################################################################################################
# ################################################################################################################################

_libc = ctypes.CDLL(None, use_errno=True)

# ################################################################################################################################
# ################################################################################################################################

def now_us() -> 'int':
    """ Returns the monotonic time in microseconds, which the arbiter and its workers read from one system clock.
    """
    now_ns = monotonic_ns()
    out = now_ns // ModuleCtx.Nanoseconds_Per_Microsecond
    return out

# ################################################################################################################################

def write_heartbeat(region:'SharedRegion') -> 'None':
    """ Records in the region that the worker is alive.
    """
    heartbeat = now_us()
    region.set_heartbeat(heartbeat)

# ################################################################################################################################

def reopen_worker_logs() -> 'None':
    """ Opens the log files that the arbiter renamed under their names again, those of the Python handlers
    and those of the REST and access log writers of zato_server_core, which a worker does on the command of the arbiter.
    """
    reopen_worker_handlers()
    reopen_logs()

# ################################################################################################################################

def set_parent_death_signal() -> 'None':
    """ Makes the kernel terminate the calling process with SIGKILL when the arbiter terminates.
    """
    result = _libc.prctl(ModuleCtx.PR_SET_PDEATHSIG, signal.SIGKILL)

    if result != 0:
        error_number = ctypes.get_errno()
        error_text = os.strerror(error_number)
        raise ArbiterError(f'Could not set the parent death signal of PID {os.getpid()}: {error_text}')

# ################################################################################################################################
# ################################################################################################################################
