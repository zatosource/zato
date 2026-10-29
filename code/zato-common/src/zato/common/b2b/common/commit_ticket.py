# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from threading import Event

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

        self._done = Event()

    @property
    def is_done(self) -> 'bool':
        out = self._done.is_set()
        return out

    def release(self) -> 'None':
        self._done.set()

    def wait(self) -> 'any_':
        """ Waits until the transaction that holds the write is committed and returns the result of the write.
        """
        _ = self._done.wait()

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

# ################################################################################################################################
# ################################################################################################################################
