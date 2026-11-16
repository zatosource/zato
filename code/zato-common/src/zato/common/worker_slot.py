# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The role of the current process within a server that its arbiter started. The arbiter forks the worker,
# which processes the messages, and the config process, which commits the changes of configuration,
# and each of them has a slot that identifies its control channel.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intnone

    intnone = intnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The slot of the worker
    Worker_Slot = 0

    # The slot of the config process
    Config_Slot = -2

    # The generation of the first process that a slot receives after the server starts
    First_Generation = 1

# ################################################################################################################################
# ################################################################################################################################

# The slot of this process, or None in a process that no arbiter started
_slot:'intnone' = None

# The generation of this process within its slot, or None in a process that no arbiter started
_generation:'intnone' = None

# ################################################################################################################################
# ################################################################################################################################

def set_process_slot(slot:'int', generation:'int') -> 'None':
    """ Records the slot and the generation of this process, which the process does once, after the fork.
    """
    global _slot, _generation

    _slot = slot
    _generation = generation

# ################################################################################################################################

def is_worker_process() -> 'bool':
    """ Says whether this process processes messages, which the worker does, as does a process that no arbiter started.
    """
    out = _slot != ModuleCtx.Config_Slot
    return out

# ################################################################################################################################

def is_config_process() -> 'bool':
    """ Says whether this process is the config process, which commits the changes of configuration
    and processes no messages.
    """
    out = _slot == ModuleCtx.Config_Slot
    return out

# ################################################################################################################################

def is_config_owner() -> 'bool':
    """ Says whether this process runs the maintenance duties of which a server runs one instance, which the config process
    does, as does a process that no arbiter started.
    """
    out = _slot is None or _slot == ModuleCtx.Config_Slot
    return out

# ################################################################################################################################

def is_first_start() -> 'bool':
    """ Says whether this process runs the duties that a server runs once after it starts, which the first generation
    of the config process does, as does a process that no arbiter started, so that a respawned config process
    never runs them again.
    """
    if _slot is None:
        out = True
    else:
        is_config_slot = _slot == ModuleCtx.Config_Slot
        is_first_generation = _generation == ModuleCtx.First_Generation
        out = is_config_slot and is_first_generation

    return out

# ################################################################################################################################
# ################################################################################################################################
