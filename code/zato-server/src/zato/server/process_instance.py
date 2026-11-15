# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The process instance of a worker, made of the start ID of its arbiter, its slot and the generation of that slot.
# The arbiter binds each worker to its instance after the fork. A record that a worker writes with its instance
# is of a live process as long as the region of the server names the same arbiter and the same generation for that slot,
# and the slot is not stopped.

# stdlib
from dataclasses import dataclass

# Zato
from zato_ipc_core.zato_ipc_core import STATE_STOPPED

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from zato_ipc_core.zato_ipc_core import SharedRegion

    SharedRegion = SharedRegion
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Key_Start_ID = 'start_id'
    Key_Slot = 'slot'
    Key_Generation = 'generation'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ProcessBinding:
    """ The region of the server of a worker and the process instance of the worker.
    """
    region: 'SharedRegion'
    instance: 'stranydict'

# ################################################################################################################################

class ProcessState:
    binding: 'ProcessBinding | None' = None

_state = ProcessState()

# ################################################################################################################################
# ################################################################################################################################

def bind_process_instance(region:'SharedRegion', slot:'int', generation:'int') -> 'None':
    """ Gives this process the instance of the worker of a slot of the region of its server.
    """
    binding = ProcessBinding()
    binding.region = region
    binding.instance = {
        ModuleCtx.Key_Start_ID: region.start_id,
        ModuleCtx.Key_Slot: slot,
        ModuleCtx.Key_Generation: generation,
    }

    _state.binding = binding

# ################################################################################################################################

def get_process_binding() -> 'ProcessBinding | None':
    """ Returns the binding of this process, or None in a process that no arbiter bound.
    """
    return _state.binding

# ################################################################################################################################

def is_process_instance_live(binding:'ProcessBinding', instance:'stranydict') -> 'bool':
    """ Whether the process of an instance still runs, as the region of the server of this process records it.
    """
    region = binding.region
    slot = instance[ModuleCtx.Key_Slot]

    # An instance of an earlier arbiter is of a process that terminated with that arbiter ..
    if instance[ModuleCtx.Key_Start_ID] != region.start_id:
        out = False

    # .. one whose slot has a newer generation is of a worker that another one replaced ..
    elif instance[ModuleCtx.Key_Generation] != region.slot_generation(slot):
        out = False

    # .. and one whose slot is stopped is of a worker that terminated and has no replacement yet.
    else:
        out = region.slot_state(slot) != STATE_STOPPED

    return out

# ################################################################################################################################
# ################################################################################################################################
