# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

def silence_logging_teardown() -> 'None':
    """ Runs at exit, before the interpreter's final garbage collection. That collection
    destroys the log handlers, whose weakref cleanup callback takes the logging module
    lock - and under gevent that lock needs the hub, which is already gone by then,
    so every run ends with a spurious 'greenlet is being finalized' traceback.
    Flushing the handlers now and removing the lock makes the late cleanup a no-op.
    """
    logging.shutdown()
    logging._lock = None # type: ignore[assignment]

# ################################################################################################################################
# ################################################################################################################################
