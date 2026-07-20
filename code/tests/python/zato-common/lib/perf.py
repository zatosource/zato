# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from signal import SIGINT
from time import monotonic

# gevent
from gevent import getcurrent, kill, signal_handler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

    floatlist = list[float]

# ################################################################################################################################
# ################################################################################################################################

# Every user-visible operation must complete within this many seconds.
Max_Operation_Seconds = 0.050

# The performance floor the whole backend must sustain.
Min_Publish_Rate_Per_Second  = 100
Min_Delivery_Rate_Per_Second = 500

# The floors of runs whose connection to the backend uses SSL.
Min_Publish_Rate_Per_Second_SSL  = 90
Min_Delivery_Rate_Per_Second_SSL = 450

# The delivery floors of broadcast fan-out runs - above the standard ones
# because fan-out multiplies every publish tenfold.
Min_Fanout_Delivery_Rate_Per_Second     = 700
Min_Fanout_Delivery_Rate_Per_Second_SSL = 630

# How often the console progress line is printed, in seconds.
Progress_Interval_Seconds = 60

# ################################################################################################################################
# ################################################################################################################################

def install_interrupt_handler() -> 'None':
    """ Makes Ctrl-C work - under gevent the default handling raises KeyboardInterrupt
    in the greenlet that is currently running, which kills only that greenlet while
    the run continues. This handler directs the interrupt to the main greenlet instead,
    whose unwinding runs the finally blocks that remove the backends under test.
    A second Ctrl-C terminates the process immediately.
    """
    main_greenlet = getcurrent()
    state = {'count': 0}

    def _on_interrupt() -> 'None':
        state['count'] += 1

        # The second interrupt means the first one could not unwind - terminate immediately.
        if state['count'] > 1:
            os._exit(1)

        print('Interrupt received - stopping the run', flush=True)
        kill(main_greenlet, KeyboardInterrupt)

    _ = signal_handler(SIGINT, _on_interrupt)

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

def measure_median_seconds(operation:'callable_', iterations:'int') -> 'float':
    """ Runs an operation repeatedly and returns its median duration in seconds -
    the median keeps one-off cache misses and scheduler blips out of the verdict.
    """
    timings:'floatlist' = []

    for _ in range(iterations):
        start = monotonic()
        _ = operation()
        elapsed = monotonic() - start
        timings.append(elapsed)

    timings.sort()

    middle_index = len(timings) // 2
    out = timings[middle_index]

    return out

# ################################################################################################################################
# ################################################################################################################################
