# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The first in first out queue of the worker processes of one server for the writes to one SQLite file.
# A write takes a place in the queue of the shared region, waits for its turn on the wake-up descriptor
# of its slot in that queue, and releases the turn when it completes.

# stdlib
from select import POLLIN
from time import monotonic

# gevent
from gevent.monkey import get_original

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anytuple, callable_
    from zato_ipc_core.zato_ipc_core import SharedRegion

    any_ = any_
    anytuple = anytuple
    callable_ = callable_
    SharedRegion = SharedRegion

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many busy timeouts of SQLite a write waits for its turn, for each worker of the server
    Busy_Timeouts_Per_Worker = 2

    Milliseconds_Per_Second = 1000

# The poll of the operating system, which blocks the thread of the pool that waits for its turn and never the hub
_poll = get_original('select', 'poll')

# ################################################################################################################################
# ################################################################################################################################

class ProcessQueueTimeout(Exception):
    """ A write waited for its turn in the queue of a SQLite file past its deadline and withdrew its place.
    """

# ################################################################################################################################
# ################################################################################################################################

def get_deadline_seconds(busy_timeout_ms:'int', worker_count:'int') -> 'float':
    """ Returns how long a write waits for its turn, a number of busy timeouts of SQLite for each worker.
    """
    deadline_ms = busy_timeout_ms * ModuleCtx.Busy_Timeouts_Per_Worker * worker_count
    out = deadline_ms / ModuleCtx.Milliseconds_Per_Second
    return out

# ################################################################################################################################
# ################################################################################################################################

class ProcessQueue:
    """ The place of one worker process in the queue of the shared region for the writes to one SQLite file.
    The caller holds the thread lock of the file in its process, so one thread of a worker is in the queue at a time.
    """

    def __init__(self, region:'SharedRegion', queue:'int', slot:'int', deadline_seconds:'float') -> 'None':
        self.region           = region
        self.queue            = queue
        self.slot             = slot
        self.deadline_seconds = deadline_seconds
        self.wake_fd          = region.queue_wake_fd(queue, slot)

# ################################################################################################################################

    def _wait_for_turn(self) -> 'bool':
        """ Returns whether the turn came before the deadline. The wake-ups of the slot are drained before each poll,
        so one that arrives during a poll makes the next wait return at once.
        """
        now = monotonic()
        deadline = now + self.deadline_seconds

        poller = _poll()
        poller.register(self.wake_fd, POLLIN)

        # The first poll follows the entry, which may have found the queue empty ..
        has_turn = self.region.queue_poll(self.queue, self.slot)

        # .. and each later one follows a wake-up, until the turn comes or the deadline passes.
        while not has_turn:

            now = monotonic()
            remaining = deadline - now

            if remaining <= 0:
                break

            remaining_ms = remaining * ModuleCtx.Milliseconds_Per_Second
            _ = poller.poll(remaining_ms)
            _ = self.region.queue_drain(self.queue, self.slot)

            has_turn = self.region.queue_poll(self.queue, self.slot)

        return has_turn

# ################################################################################################################################

    def run(self, func:'callable_', args:'anytuple') -> 'any_':
        """ Runs one write when the turn of this worker comes, and releases the turn when the write completes.
        """
        # Take a place in the queue ..
        _ = self.region.queue_enter(self.queue, self.slot)

        # .. wait for the turn, and withdraw the place when the deadline passes ..
        has_turn = self._wait_for_turn()

        if not has_turn:
            self.region.queue_abandon(self.queue, self.slot)
            message = f'No turn in writer queue {self.queue} for slot {self.slot} within {self.deadline_seconds}s'
            raise ProcessQueueTimeout(message)

        # .. and run the write, after which the next worker in the queue is woken.
        try:
            out = func(*args)
        finally:
            self.region.queue_release(self.queue, self.slot)

        return out

# ################################################################################################################################

    def run_under_lock(self, lock:'any_', func:'callable_', args:'anytuple') -> 'any_':
        """ Runs one write under the thread lock of the file in this process, then in the queue of all the workers.
        """
        with lock:
            out = self.run(func, args)

        return out

# ################################################################################################################################
# ################################################################################################################################
