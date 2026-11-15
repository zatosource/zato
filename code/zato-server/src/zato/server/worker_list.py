# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The runtime state of the worker of each slot. The worker that serves the request queries every worker through
# the control channel, and each worker answers with its process ID, its generation, the number of the subscription keys
# that its slot owns and whether it runs the duties of which a server runs one instance. The state and the heartbeat
# of each slot are read from the shared region, which also gives the process ID and the generation of a slot
# whose worker did not answer.

# stdlib
import os
from dataclasses import dataclass
from time import monotonic_ns

# Zato
from zato.common.pubsub.ownership import is_owner
from zato.common.worker_slot import is_singleton_owner
from zato.server.control.hub import EntryStatus
from zato.server.control.queries import new_query, QueryName
from zato_ipc_core.zato_ipc_core import STATE_DRAINING, STATE_EMPTY, STATE_READY, STATE_STARTING, STATE_STOPPED

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, callable_, intnone
    from zato_ipc_core.zato_ipc_core import SharedRegion

    anydict = anydict
    anylist = anylist
    callable_ = callable_
    intnone = intnone
    SharedRegion = SharedRegion

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Nanoseconds_Per_Microsecond = 1000
    Microseconds_Per_Millisecond = 1000

    # The name of each state of a slot in the shared region
    State_Names = {
        STATE_EMPTY:    'empty',
        STATE_STARTING: 'starting',
        STATE_READY:    'ready',
        STATE_DRAINING: 'draining',
        STATE_STOPPED:  'stopped',
    }

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WorkerListBinding:
    """ The region, the slot and the generation of the worker of this process, the function that queries every worker
    and the function that returns every subscription key that the worker knows.
    """
    region: 'SharedRegion'
    slot: 'int'
    generation: 'int'
    query: 'callable_'
    get_sub_keys: 'callable_'

# ################################################################################################################################

class WorkerListState:
    def __init__(self) -> 'None':
        self.binding:'WorkerListBinding | None' = None

_state = WorkerListState()

# ################################################################################################################################
# ################################################################################################################################

def bind_worker_list(region:'SharedRegion', slot:'int', generation:'int', query:'callable_', get_sub_keys:'callable_') -> 'None':
    """ Makes the worker of a slot answer the queries of the worker list and serve the list through its control client.
    """
    binding = WorkerListBinding()
    binding.region = region
    binding.slot = slot
    binding.generation = generation
    binding.query = query
    binding.get_sub_keys = get_sub_keys

    _state.binding = binding

# ################################################################################################################################

def _get_binding() -> 'WorkerListBinding':

    binding = _state.binding

    if binding is None:
        raise Exception('The worker list is available only in a worker process of a server')

    return binding

# ################################################################################################################################

def _now_us() -> 'int':
    """ Returns the monotonic time in microseconds, the clock of the heartbeats in the region.
    """
    now_ns = monotonic_ns()
    out = now_ns // ModuleCtx.Nanoseconds_Per_Microsecond
    return out

# ################################################################################################################################
# ################################################################################################################################

def answer_worker_list(_data:'None') -> 'anydict':
    """ Returns the answer of the worker of this process to a query of the worker list.
    """
    binding = _get_binding()
    slot_count = binding.region.slot_count

    sub_key_count = 0

    for sub_key in binding.get_sub_keys():
        if is_owner(sub_key, binding.slot, slot_count):
            sub_key_count += 1

    out = {
        'pid': os.getpid(),
        'generation': binding.generation,
        'sub_key_count': sub_key_count,
        'is_singleton_owner': is_singleton_owner(),
    }
    return out

# ################################################################################################################################

def build_worker_list(region:'SharedRegion', entries:'anylist', now_us:'int') -> 'anylist':
    """ Returns one row for each slot, from the entries of the query of the worker list and from the region.
    """
    out:'anylist' = []

    for entry in entries:
        slot = entry['slot']
        state = region.slot_state(slot)

        # A slot that never had a worker has no process and no heartbeat ..
        if state == STATE_EMPTY:
            heartbeat_age_ms:'intnone' = None
        else:
            heartbeat_age_us = now_us - region.slot_heartbeat(slot)
            heartbeat_age_ms = heartbeat_age_us // ModuleCtx.Microseconds_Per_Millisecond

        # .. a worker that answered describes itself ..
        if entry['status'] == EntryStatus.OK:
            answer = entry['body']
            pid = answer['pid']
            generation = answer['generation']
            sub_key_count = answer['sub_key_count']
            singleton_flag = answer['is_singleton_owner']

        # .. and the region describes the process of a slot whose worker did not answer.
        else:
            pid = region.slot_pid(slot)
            generation = region.slot_generation(slot)
            sub_key_count = None
            singleton_flag = None

        row = {
            'slot': slot,
            'pid': pid,
            'generation': generation,
            'state': ModuleCtx.State_Names[state],
            'heartbeat_age_ms': heartbeat_age_ms,
            'sub_key_count': sub_key_count,
            'is_singleton_owner': singleton_flag,
            'response': entry['status'],
        }
        out.append(row)

    return out

# ################################################################################################################################

def get_worker_list() -> 'anylist':
    """ Queries every worker and returns one row for each slot.
    """
    binding = _get_binding()

    query = new_query(QueryName.Worker_Get_List, None)
    entries = binding.query(query)

    out = build_worker_list(binding.region, entries, _now_us())
    return out

# ################################################################################################################################
# ################################################################################################################################
