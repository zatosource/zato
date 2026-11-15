# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared region of the workers of a server, as the MLLP channels and outgoing connections of one worker use it.
# The arbiter binds each worker to its slot after the fork, and the control IDs of the channels, the circuit breakers
# of the outgoing connections and the pool sizes of those connections then cover every worker of the server.
# A process that no arbiter bound keeps the state of its channels and connections in its own memory.

# stdlib
from dataclasses import dataclass
from time import monotonic_ns

# Zato
from zato_ipc_core.zato_ipc_core import LockOwner

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato_ipc_core.zato_ipc_core import SharedRegion

    SharedRegion = SharedRegion

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a check of a control ID waits before it checks again while another worker holds the table, in seconds
    Busy_Interval = 0.0005

    # The fewest connections that each worker keeps in the pool of an outgoing connection
    Min_Pool_Size_Per_Worker = 1

    # The kinds of the series of the channels in the series table, apart from the kinds of the metrics of the server,
    # so the reset of the gauges of a slot at the binding of its worker leaves the time of the last message in place
    Kind_Channel_Counter = 101
    Kind_Channel_Time    = 102

    # The first part of the key of a series of a channel, followed by the name of the channel and the name of the value
    Channel_Key_Prefix    = 'zato.hl7.mllp.channel'
    Channel_Key_Separator = '\x00'

    Nanos_Per_Micro = 1000
    Micros_Per_Second = 1_000_000

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MLLPBinding:
    """ The region of the server of a worker and the identity under which the worker takes the lock of its table.
    """
    region: 'SharedRegion'
    slot: 'int'
    owner: 'LockOwner'

# ################################################################################################################################

class MLLPState:
    binding: 'MLLPBinding | None' = None

_state = MLLPState()

# ################################################################################################################################
# ################################################################################################################################

def bind_mllp(region:'SharedRegion', slot:'int', generation:'int') -> 'None':
    """ Makes the MLLP channels and outgoing connections of this process use the region of its server.
    """
    binding = MLLPBinding()
    binding.region = region
    binding.slot = slot
    binding.owner = LockOwner(slot, generation)

    _state.binding = binding

# ################################################################################################################################

def get_mllp_binding() -> 'MLLPBinding | None':
    """ Returns the binding of this process, or None in a process that no arbiter bound.
    """
    return _state.binding

# ################################################################################################################################

def get_now_us() -> 'int':
    """ Returns the monotonic clock in microseconds, which every process of the host reads alike.
    """
    out = monotonic_ns() // ModuleCtx.Nanos_Per_Micro
    return out

# ################################################################################################################################

def seconds_to_us(seconds:'float') -> 'int':
    out = int(seconds * ModuleCtx.Micros_Per_Second)
    return out

# ################################################################################################################################

def get_worker_pool_size(pool_size:'int') -> 'int':
    """ Returns the share of each worker of the pool size of an outgoing connection, so the workers together
    keep the configured number of connections, and each worker keeps at least one.
    """
    binding = _state.binding

    if binding is None:
        return pool_size

    worker_count = binding.region.slot_count

    out = max(ModuleCtx.Min_Pool_Size_Per_Worker, pool_size // worker_count)
    return out

# ################################################################################################################################
# ################################################################################################################################
