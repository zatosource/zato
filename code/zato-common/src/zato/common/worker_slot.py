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

# ################################################################################################################################
# ################################################################################################################################

# The slot of the worker that this process runs, or None in a process that is not a worker of a multi-process server
_worker_slot:'intnone' = None

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

def is_singleton_owner() -> 'bool':
    """ Says whether this process runs the duties of which a server runs one instance, which a process that is not
    a worker always does and, of the workers of a multi-process server, the worker of the first slot does.
    """
    out = _worker_slot is None or _worker_slot == ModuleCtx.Singleton_Slot
    return out

# ################################################################################################################################
# ################################################################################################################################
