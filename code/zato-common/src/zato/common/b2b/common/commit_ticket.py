# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from threading import Event
from time import time

# Zato
from zato.common.b2b.common.commit_timing import timing_log

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

ticket_list = list['CommitTicket']

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class TransactionResult:
    """ What a function run in a transaction of its own returns - its value for the caller,
    and the event writes it inserted.
    """
    value:        'any_'
    event_writes: 'anylist'

    def __init__(self) -> 'None':
        self.value = None
        self.event_writes = []

# ################################################################################################################################
# ################################################################################################################################

class CommitTicket:
    """ One write waiting for the commit of the transaction that holds it.
    """

    def __init__(self, write:'any_', row_count:'int') -> 'None':
        self.write = write
        self.row_count = row_count

        # What the write produced, or the exception that refused it.
        self.result:'any_' = None
        self.error:'Exception | None' = None

        # Prototype - when the write was enqueued and when its transaction released it.
        self.enqueued_at = time()
        self.released_at = 0.0

        self._done = Event()

    @property
    def is_done(self) -> 'bool':
        out = self._done.is_set()
        return out

    def release(self) -> 'None':
        self.released_at = time()
        self._done.set()

    def wait(self) -> 'any_':
        """ Waits until the transaction that holds the write is committed and returns the result of the write.
        """
        _ = self._done.wait()

        if timing_log:
            resumed_at = time()
            timing_log.write({
                'type': 'ticket',
                'rows': self.row_count,
                'wait_ms': round((resumed_at - self.enqueued_at) * 1000, 2),
                'lag_ms': round((resumed_at - self.released_at) * 1000, 2),
            })

        if self.error:
            raise self.error

        out = self.result
        return out

# ################################################################################################################################
# ################################################################################################################################

class GroupProgress:
    """ One group of writes of a pipelined writer, and whether its statements are executed.
    """

    def __init__(self, tickets:'ticket_list') -> 'None':
        self.tickets = tickets
        self.statements_done = Event()

        # Set once the transaction of the group is committed or rolled back.
        self.is_committed = Event()

        # Prototype - when the group was taken from the pending writes, and when each step of its commit ended.
        self.taken_at = time()
        self.lane_started_at = 0.0
        self.lock_acquired_at = 0.0
        self.statements_done_at = 0.0
        self.committed_at = 0.0

# ################################################################################################################################
# ################################################################################################################################
