# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from heapq import heappop, heappush
from itertools import count
from logging import getLogger

# gevent
from gevent import sleep, spawn
from gevent.event import Event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from gevent import Greenlet
    from zato.common.b2b.common.clock import Clock
    from zato.common.b2b.common.recovery import RecoveredPage
    from zato.common.typing_ import any_, anylist, callable_
    any_ = any_
    anylist = anylist
    callable_ = callable_
    Clock = Clock
    datetime = datetime
    Greenlet = Greenlet
    RecoveredPage = RecoveredPage

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How many due entries run before the scheduler yields to the other greenlets.
Due_Batch_Size = 100

# How long after a failed run an entry runs again.
Failed_Entry_Delay = timedelta(seconds=5)

# ################################################################################################################################
# ################################################################################################################################

class EntryKind:
    """ What a scheduled entry stands for - the next delivery of a sent message, the deadline of a business transaction,
    the deadline of a sequence gap, or the next probe of a suspended address.
    """
    Delivery          = 'delivery'
    Business_Deadline = 'business-deadline'
    Gap_Deadline      = 'gap-deadline'
    Probe             = 'probe'

# ################################################################################################################################
# ################################################################################################################################

class DeliveryScheduler:
    """ Runs everything that is due at a moment - deliveries, deadlines and probes - in one greenlet over one heap
    ordered by the due time. The caller registers a handler for each kind of entry, which receives the key
    of the entry and the current time, does what is due, and returns when the entry is due next, or None
    when it is not due again. An entry scheduled again replaces the one scheduled before it.
    """

    def __init__(self, clock:'Clock', batch_size:'int'=Due_Batch_Size) -> 'None':

        self.clock = clock
        self.batch_size = batch_size

        # Each entry as a due time, an order among entries due at the same time, the kind and the key.
        self._heap:'anylist' = []
        self._order = count()

        # The current due time of each entry, by its kind and key - a heap item with another due time is stale.
        self._due:'dict[tuple[str, str], datetime]' = {}

        self._handlers:'dict[str, callable_]' = {}

        # Set when an entry earlier than the head of the heap arrives, or when the scheduler is to stop.
        self._wake = Event()
        self._is_stopped = False
        self._greenlet:'Greenlet | None' = None

# ################################################################################################################################

    def set_handler(self, kind:'str', handler:'callable_') -> 'None':
        """ Registers what runs the entries of one kind.
        """
        self._handlers[kind] = handler

# ################################################################################################################################

    def schedule(self, kind:'str', key:'str', due_at:'datetime') -> 'None':
        """ Schedules an entry, replacing the earlier one of the same kind and key, and wakes the scheduler
        if the entry is due before everything else.
        """
        is_earliest = (not self._heap) or due_at < self._heap[0][0]

        self._due[kind, key] = due_at
        heappush(self._heap, (due_at, next(self._order), kind, key))

        if is_earliest:
            self._wake.set()

# ################################################################################################################################

    def cancel(self, kind:'str', key:'str') -> 'None':
        """ Removes an entry, if it is scheduled.
        """
        _ = self._due.pop((kind, key), None)

# ################################################################################################################################

    def due_at(self, kind:'str', key:'str') -> 'datetime | None':
        """ Returns when an entry is due, or None when it is not scheduled.
        """
        out = self._due.get((kind, key))
        return out

# ################################################################################################################################

    def __len__(self) -> 'int':
        out = len(self._due)
        return out

# ################################################################################################################################

    def _next_due(self, now:'datetime') -> 'tuple[str, str] | None':
        """ Removes and returns the kind and the key of the earliest entry due at the given time, skipping stale items,
        or returns None when nothing is due.
        """
        while self._heap:
            due_at, _, kind, key = self._heap[0]

            # A replaced or cancelled entry is dropped ..
            if self._due.get((kind, key)) != due_at:
                _ = heappop(self._heap)
                continue

            # .. while a current one that is not due yet ends the search.
            if due_at > now:
                return None

            _ = heappop(self._heap)
            del self._due[kind, key]

            return kind, key

        return None

# ################################################################################################################################

    def _run_entry(self, kind:'str', key:'str', now:'datetime') -> 'None':
        """ Runs one entry and schedules it again for when its handler says it is due next.
        """
        handler = self._handlers[kind]

        # A failure of one entry does not stop the others, and the entry runs again after a delay.
        try:
            next_due = handler(key, now)
        except Exception:
            logger.exception('Scheduled entry `%s` of kind `%s` failed', key, kind)
            next_due = now + Failed_Entry_Delay

        # An entry the handler scheduled itself in the meantime keeps that time.
        if next_due is not None:
            if (kind, key) not in self._due:
                self.schedule(kind, key, next_due)

# ################################################################################################################################

    def run_due(self, now:'datetime') -> 'int':
        """ Runs up to one batch of the entries due at the given time, the earliest first, and returns how many ran.
        """
        out = 0

        while out < self.batch_size:

            if (entry := self._next_due(now)) is None:
                break

            kind, key = entry
            self._run_entry(kind, key, now)

            out += 1

        return out

# ################################################################################################################################

    def _wait_seconds(self) -> 'float | None':
        """ Returns how long the scheduler sleeps until the earliest entry is due, or None when nothing is scheduled.
        """
        if self._heap:
            due_in = self._heap[0][0] - self.clock.now()
            out = max(due_in.total_seconds(), 0.0)
        else:
            out = None

        return out

# ################################################################################################################################

    def _loop(self) -> 'None':

        while not self._is_stopped:

            timeout = self._wait_seconds()

            _ = self._wake.wait(timeout)
            self._wake.clear()

            # The entries due run in batches, and the other greenlets run between two batches.
            while not self._is_stopped:
                ran = self.run_due(self.clock.now())

                if ran < self.batch_size:
                    break

                sleep(0)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the greenlet that runs the entries as they become due.
        """
        self._is_stopped = False
        self._greenlet = spawn(self._loop)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the greenlet after the entry it runs, if any.
        """
        self._is_stopped = True
        self._wake.set()

        if self._greenlet:
            _ = self._greenlet.join()
            self._greenlet = None

# ################################################################################################################################
# ################################################################################################################################

def recover_pages(read_page:'callable_', on_item:'callable_', page_size:'int', after:'any_') -> 'int':
    """ Reads what a recovery returns page by page, from the page after the given cursor, passes each item
    to the given function, and yields to the other greenlets between two pages. Returns how many items there were.
    """
    out = 0

    while True:
        page:'RecoveredPage' = read_page(page_size, after)

        for item in page.items:
            on_item(item)

        out += len(page.items)
        after = page.last_id

        if page.is_last:
            break

        sleep(0)

    return out

# ################################################################################################################################
# ################################################################################################################################
