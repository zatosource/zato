# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared region of a server with worker processes, which the arbiter creates before it forks the first worker.
# Each table of the region has a fixed capacity, chosen here for every server.

# stdlib
from time import time_ns

# Zato
from zato_ipc_core.zato_ipc_core import SharedRegion

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The subscription keys whose wake-up counters the workers exchange
    Wake_Capacity = 65_536

    # The keys of the rate limiting counters of every channel and security definition
    Cell_Capacity = 65_536

    # The counters that each worker adds to in its own row, by their positions in the row
    Metric_Rate_Limit_Table_Full = 0
    Metric_Count = 1

    # The series of the metrics of the server and the bytes of their keys
    Series_Capacity  = 16_384
    Series_Key_Bytes = Series_Capacity * 256

    # The control IDs of the MLLP messages that the workers deduplicate together
    Dedup_Capacity = 65_536

    # The circuit breakers of the outgoing MLLP connections
    Breaker_Capacity = 1024

    # The keyed locks and counters of the outgoing queues and the file transfer runs
    Lock_Capacity = 4096

    Nanoseconds_Per_Microsecond = 1000

# ################################################################################################################################
# ################################################################################################################################

def new_start_id() -> 'int':
    """ Returns the ID of this start of the server, a time in microseconds, which no earlier start of the server had,
    so that a record written by a process of an earlier start is never taken for one of a live process.
    """
    now_ns = time_ns()
    out = now_ns // ModuleCtx.Nanoseconds_Per_Microsecond
    return out

# ################################################################################################################################

def new_server_region(worker_count:'int', queue_count:'int') -> 'SharedRegion':
    """ Returns the region of a server with the given number of workers and of queues of its SQLite files.
    """
    start_id = new_start_id()

    out = SharedRegion({
        'slot_count': worker_count,
        'wake_capacity': ModuleCtx.Wake_Capacity,
        'cell_capacity': ModuleCtx.Cell_Capacity,
        'queue_count': queue_count,
        'metric_count': ModuleCtx.Metric_Count,
        'series_capacity': ModuleCtx.Series_Capacity,
        'series_key_bytes': ModuleCtx.Series_Key_Bytes,
        'dedup_capacity': ModuleCtx.Dedup_Capacity,
        'breaker_capacity': ModuleCtx.Breaker_Capacity,
        'lock_capacity': ModuleCtx.Lock_Capacity,
        'start_id': start_id,
    })

    return out

# ################################################################################################################################
# ################################################################################################################################
