# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The slot of the worker process that the current process runs. Every log record that a worker creates
# and every audit event that it writes carry the slot in an attribute, so that the records of the workers
# of one server can be told apart.

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intnone

    any_ = any_
    intnone = intnone

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The attribute of a log record and of an audit event that holds the slot
    Attr_Name = 'worker_slot'

    # The slot whose worker runs the duties of which a server runs one instance
    Singleton_Slot = 0

    # The slot that a process which is not a worker uses wherever a slot is named, as the one process of its server
    Single_Process_Slot = 0

    # The slot of the config process of a multi-process server, which is no slot of the shared region
    Config_Slot = -2

    # The generation of the first worker that a slot receives after the server starts
    First_Generation = 1

# ################################################################################################################################
# ################################################################################################################################

# The slot of the worker that this process runs, or None in a process that is not a worker of a multi-process server
_worker_slot:'intnone' = None

# The generation of the worker that this process runs within its slot, or None in a process that is not a worker
_worker_generation:'intnone' = None

# ################################################################################################################################
# ################################################################################################################################

def set_worker_slot(slot:'int') -> 'None':
    """ Records the slot of the worker that this process runs, which a worker does once, after the fork.
    """
    global _worker_slot
    _worker_slot = slot

    # Every log record that the process creates from now on carries the slot, as the records with extra values do
    new_base_record = logging.getLogRecordFactory()

    def new_record(*args:'any_', **kwargs:'any_') -> 'logging.LogRecord':
        out = new_base_record(*args, **kwargs)
        out.__dict__[ModuleCtx.Attr_Name] = slot
        return out

    logging.setLogRecordFactory(new_record)

# ################################################################################################################################

def set_worker_generation(generation:'int') -> 'None':
    """ Records the generation of the worker that this process runs within its slot, which a worker does once, after the fork.
    """
    global _worker_generation
    _worker_generation = generation

# ################################################################################################################################

def get_worker_slot() -> 'intnone':
    """ Returns the slot of the worker that this process runs, or None if the process is not a worker.
    """
    return _worker_slot

# ################################################################################################################################

def get_slot_or_single() -> 'int':
    """ Returns the slot of the worker that this process runs, or the slot of a server with one process
    if the process is not a worker.
    """
    if _worker_slot is None:
        out = ModuleCtx.Single_Process_Slot
    else:
        out = _worker_slot

    return out

# ################################################################################################################################

def is_config_process() -> 'bool':
    """ Says whether this process is the config process of a multi-process server, which commits the changes
    of configuration and processes no messages.
    """
    out = _worker_slot == ModuleCtx.Config_Slot
    return out

# ################################################################################################################################

def is_singleton_owner() -> 'bool':
    """ Says whether this process runs the message processing of which a server runs one instance, which a process
    that is not a worker always does and, of the workers of a multi-process server, the worker of the first slot does.
    """
    out = _worker_slot is None or _worker_slot == ModuleCtx.Singleton_Slot
    return out

# ################################################################################################################################

def is_config_owner() -> 'bool':
    """ Says whether this process runs the maintenance duties of which a server runs one instance, which a process
    that is not a worker always does and, of the processes of a multi-process server, the config process does.
    """
    out = _worker_slot is None or _worker_slot == ModuleCtx.Config_Slot
    return out

# ################################################################################################################################

def is_first_start() -> 'bool':
    """ Says whether this process runs the duties that a server runs once after it starts, which a process that is not
    a worker always does and, of the processes of a multi-process server, the first generation of the config process does,
    so that a respawned config process never runs them again.
    """
    if _worker_slot is None:
        out = True
    else:
        is_config_slot = _worker_slot == ModuleCtx.Config_Slot
        is_first_generation = _worker_generation == ModuleCtx.First_Generation
        out = is_config_slot and is_first_generation

    return out

# ################################################################################################################################
# ################################################################################################################################
