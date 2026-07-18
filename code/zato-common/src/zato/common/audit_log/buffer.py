# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from logging import getLogger
from threading import Lock, Thread
from time import monotonic, sleep

# gevent
from gevent.monkey import is_module_patched

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, callable_, stranydict

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    callable_ = callable_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The environment variables configuring the buffered writer
Env_Flush_Max_Size    = 'Zato_Audit_Log_Flush_Max_Size'
Env_Flush_Max_Wait_Ms = 'Zato_Audit_Log_Flush_Max_Wait_Ms'

# One event per flush means the writer is synchronous - the default, high-volume producers opt into batching
_default_flush_max_size = 1

# How long a buffered event may wait before it is flushed regardless of the batch size
_default_flush_max_wait_ms = 500

# The background flusher never sleeps less than this between checks
_min_check_interval_seconds = 0.05

# .. and never more than this, so a shrinking max-wait is honored promptly.
_max_check_interval_seconds = 1.0

# Per-flush trace diagnostics - opt-in through the environment
_is_trace_enabled = bool(os.environ.get('Zato_HL7_Trace'))

def _trace(message:'str', *args:'object') -> 'None':
    if _is_trace_enabled:
        logger.info('TRACE ' + message, *args)

# ################################################################################################################################

def get_flush_max_size() -> 'int':
    """ Returns how many events are buffered before a flush. One means every event is written synchronously.
    """
    if value := os.environ.get(Env_Flush_Max_Size, ''):
        out = int(value)
    else:
        out = _default_flush_max_size

    return out

# ################################################################################################################################

def get_flush_max_wait_ms() -> 'int':
    """ Returns how long a buffered event may wait, in milliseconds, before it is flushed.
    """
    if value := os.environ.get(Env_Flush_Max_Wait_Ms, ''):
        out = int(value)
    else:
        out = _default_flush_max_wait_ms

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingEvent:
    """ One audit event waiting in the buffer, with everything that is written alongside it.
    """

    # The values of the event row itself
    values: 'stranydict'

    # Searchable attributes, name to value
    attrs: 'stranydict'

    # Message bodies, kind to content
    bodies: 'stranydict'

    # Lineage - the ids of parent events and how this event relates to them
    parents: 'anylist'
    parent_link_type: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

# The list type the buffer holds
pending_event_list = list[PendingEvent]

# ################################################################################################################################
# ################################################################################################################################

class EventBuffer:
    """ Buffers audit events and writes them out in batches - a flush runs when the buffer
    reaches its maximum size or when its oldest event has waited long enough.
    With a maximum size of one, every event is written synchronously and no flusher thread ever starts.
    """

    def __init__(self, *, max_size:'int', max_wait_ms:'int', write_batch:'callable_') -> 'None':

        self.max_size = max_size
        self.max_wait_ms = max_wait_ms
        self.write_batch = write_batch

        # Guards the pending list and the first-added timestamp
        self._lock = Lock()

        # What is waiting to be written
        self._pending:'pending_event_list' = []

        # When the oldest pending event was added, per the monotonic clock
        self._first_added_at = 0.0

        # The background flusher starts lazily, with the first buffered event
        self._flusher_started = False

# ################################################################################################################################

    def add(self, event:'PendingEvent') -> 'None':
        """ Adds one event, flushing inline if the buffer is full.
        """

        # Take the batch out under the lock if this event fills the buffer up ..
        with self._lock:

            self._pending.append(event)

            if len(self._pending) == 1:
                self._first_added_at = monotonic()

            if len(self._pending) >= self.max_size:
                batch = self._pending
                self._pending = []
            else:
                batch = None

            # .. make sure the time-based flusher is running ..
            if not self._flusher_started:
                self._flusher_started = True
                self._start_flusher()

        # .. and write outside the lock so producers are never blocked by the database.
        if batch:

            # Trace point 7: a full buffer flushes inline in the producer
            _trace('inline flush of %d events begins', len(batch))
            flush_start = monotonic()

            self._write_batch_off_loop(batch)

            _trace('inline flush of %d events done %.1fms', len(batch), (monotonic() - flush_start) * 1000)

# ################################################################################################################################

    def _write_batch_off_loop(self, batch:'pending_event_list') -> 'None':
        """ Runs the blocking database write on a real OS thread when gevent has the process
        monkey-patched - the database driver's C calls never yield to the event loop, so a slow
        write executed inline would freeze every socket in the process for its whole duration.
        """
        if is_module_patched('threading'):
            from gevent import get_hub
            get_hub().threadpool.apply(self.write_batch, (batch,))
        else:
            self.write_batch(batch)

# ################################################################################################################################

    def flush(self) -> 'None':
        """ Writes out everything currently buffered.
        """
        with self._lock:
            batch = self._pending
            self._pending = []

        if batch:
            self.write_batch(batch)

# ################################################################################################################################

    def _start_flusher(self) -> 'None':
        """ Starts the background thread enforcing the maximum wait time.
        """
        thread = Thread(target=self._run_flusher, name='audit-log-flusher', daemon=True)
        thread.start()

# ################################################################################################################################

    def _run_flusher(self) -> 'None':
        """ Periodically flushes events that have waited longer than the maximum wait time.
        """

        # Check twice per maximum wait, within sane bounds
        interval = self.max_wait_ms / 1000.0 / 2
        interval = max(interval, _min_check_interval_seconds)
        interval = min(interval, _max_check_interval_seconds)

        max_wait_seconds = self.max_wait_ms / 1000.0

        while True:

            sleep(interval)

            # Take the batch out under the lock if the oldest event has waited long enough ..
            with self._lock:

                if self._pending:
                    waited = monotonic() - self._first_added_at
                    if waited >= max_wait_seconds:
                        batch = self._pending
                        self._pending = []
                    else:
                        batch = None
                else:
                    batch = None

            # .. and write outside the lock.
            if batch:

                # Trace point 8: the timed flusher writes a batch in the background
                _trace('timed flush of %d events begins', len(batch))
                flush_start = monotonic()

                try:
                    self._write_batch_off_loop(batch)
                except Exception:
                    logger.warning('Audit log flush failed', exc_info=True)

                _trace('timed flush of %d events done %.1fms', len(batch), (monotonic() - flush_start) * 1000)

# ################################################################################################################################
# ################################################################################################################################
