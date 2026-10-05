# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from collections import deque
from logging import getLogger
from threading import Event, Lock, Thread
from time import monotonic, sleep

# OpenTelemetry
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.proto.logs.v1.logs_pb2 import ResourceLogs, ScopeLogs

# Zato
from zato.common.audit_log.export.mapping import build_log_record

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from opentelemetry.proto.common.v1.common_pb2 import InstrumentationScope
    from opentelemetry.proto.resource.v1.resource_pb2 import Resource
    from zato.common.audit_log.export.config import ExportConfig
    from zato.common.audit_log.export.mapping import QueuedEvent
    from zato.common.audit_log.export.sender import Sender
    from zato.common.typing_ import anylist, stranydict

    queued_event_list = list[QueuedEvent]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long the worker waits before retrying a batch the collector did not accept, doubling up to the maximum
    Backoff_Min_Seconds = 1.0
    Backoff_Max_Seconds = 60.0

    # How many records are built before the rest of the process gets its turn, and how long that turn is.
    # The pause is a real timer and never a zero sleep, which under gevent would only queue a callback and
    # hold the loop for the whole batch.
    Records_Per_Slice = 8
    Slice_Pause_Seconds = 0.0001

    # The name of the worker
    Worker_Name = 'audit-log-export'

# ################################################################################################################################
# ################################################################################################################################

def _plural(count:'int', singular:'str', plural:'str') -> 'str':
    """ Returns a count followed by the right form of the noun.
    """
    noun = singular if count == 1 else plural
    out = f'{count:,} {noun}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class ExportQueue:
    """ A bounded queue of audit events and the worker that sends them to the collector in batches.
    Adding an event never waits - a full queue drops its oldest event instead. A batch the collector
    did not accept stays where it is and is retried until it is accepted.
    """

    def __init__(
        self,
        *,
        config:'ExportConfig',
        sender:'Sender',
        resource:'Resource',
        scope:'InstrumentationScope',
        address:'str',
        ) -> 'None':

        self.config = config
        self.sender = sender
        self.resource = resource
        self.scope = scope

        # The collector's address as log lines name it
        self.address = address

        self._queue:'deque[QueuedEvent]' = deque()
        self._lock = Lock()

        # Wakes the worker up when a full batch is waiting or when it is time to stop
        self._wake = Event()
        self._stop = Event()

        # The batch being sent and its body, both kept until the collector accepts it
        self._in_flight:'queued_event_list' = []
        self._in_flight_body = b''

        # Why the collector did not accept the last batch
        self._last_reason = ''

        # The state of the current outage
        self._is_paused = False
        self._has_logged_full = False
        self._dropped_count = 0
        self._dropped_min_id = 0
        self._dropped_max_id = 0

        # Counters for the whole life of the queue
        self.emitted_count = 0
        self.exported_count = 0
        self.dropped_total = 0
        self.batches_ok = 0
        self.batches_failed = 0

        self._batch_size = config.batch_size
        self._max_batch_size = config.max_batch_size
        self._flush_interval = config.flush_interval_ms / 1000

        self._worker:'Thread | None' = None

# ################################################################################################################################

    def __len__(self) -> 'int':
        return len(self._queue)

# ################################################################################################################################

    def add(self, event:'QueuedEvent') -> 'None':
        """ Adds one event, dropping the oldest one when the queue is full.
        """
        with self._lock:

            # A full queue makes room by dropping its oldest event ..
            queue_length = len(self._queue)
            is_full = queue_length >= self.config.queue_size

            if is_full:
                dropped = self._queue.popleft()
                self._on_dropped(dropped.event_id)

            # .. the new event goes to the end ..
            self._queue.append(event)
            self.emitted_count += 1

            queue_length = len(self._queue)

        # .. the worker starts with the first event ..
        if self._worker is None:
            self._start_worker()

        # .. and is woken up as soon as a full batch is waiting.
        has_full_batch = queue_length >= self._batch_size

        if has_full_batch:
            self._wake.set()

# ################################################################################################################################

    def _on_dropped(self, event_id:'int') -> 'None':
        """ Counts a dropped event and logs the first drop of an outage.
        """
        if self._dropped_count == 0:
            self._dropped_min_id = event_id

        self._dropped_count += 1
        self._dropped_max_id = event_id
        self.dropped_total += 1

        if not self._has_logged_full:
            self._has_logged_full = True
            queue_size = _plural(self.config.queue_size, 'event', 'events')
            logger.warning('Audit export queue full at %s, dropping the oldest', queue_size)

# ################################################################################################################################

    def _start_worker(self) -> 'None':
        """ Starts the worker that sends the batches.
        """
        self._worker = Thread(target=self._run, name=ModuleCtx.Worker_Name, daemon=True)
        self._worker.start()

# ################################################################################################################################

    def _take_batch(self) -> 'None':
        """ Moves what is queued, up to the maximum batch, out of the queue and builds the body that is sent.
        """
        with self._lock:
            queue_length = len(self._queue)
            count = min(self._max_batch_size, queue_length)

            batch:'queued_event_list' = []
            for _ in range(count):
                batch.append(self._queue.popleft())

        if not batch:
            return

        # A batch whose records cannot be built is dropped, so one event never holds up the queue
        try:
            body = self._build_body(batch)
        except Exception:
            event_ids:'anylist' = []
            for event in batch:
                event_ids.append(event.event_id)
            logger.exception('Audit export dropped a batch it could not build, event ids %s', event_ids)
            return

        self._in_flight = batch
        self._in_flight_body = body

# ################################################################################################################################

    def _build_body(self, batch:'queued_event_list') -> 'bytes':
        """ Builds the records of a batch a slice at a time, letting the rest of the process run in between,
        and returns the request ready to be sent.
        """
        max_payload_size = self.config.max_payload_size
        records:'anylist' = []

        for index, event in enumerate(batch, 1):
            records.append(build_log_record(event, max_payload_size))
            is_slice_over = index % ModuleCtx.Records_Per_Slice == 0
            if is_slice_over:
                sleep(ModuleCtx.Slice_Pause_Seconds)

        scope_logs = ScopeLogs(scope=self.scope, log_records=records)
        resource_logs = ResourceLogs(resource=self.resource, scope_logs=[scope_logs])
        request = ExportLogsServiceRequest(resource_logs=[resource_logs])

        serialized = request.SerializeToString()

        out = self.sender.prepare(serialized)
        return out

# ################################################################################################################################

    def _send_in_flight(self) -> 'bool':
        """ Sends the batch in flight and returns whether the collector accepted it.
        """
        self._last_reason = self.sender.send(self._in_flight_body)

        out = not self._last_reason
        return out

# ################################################################################################################################

    def _on_accepted(self) -> 'None':
        """ Forgets the batch the collector accepted and ends an outage if there was one.
        """
        self.exported_count += len(self._in_flight)
        self.batches_ok += 1

        self._in_flight = []
        self._in_flight_body = b''

        # Nothing was paused or dropped, so there is nothing to report ..
        if not self._is_paused:
            if not self._dropped_count:
                return

        # .. otherwise, say how the outage ended ..
        if self._dropped_count:
            dropped = _plural(self._dropped_count, 'event', 'events')
            logger.warning('Audit export to %s resumed, %s dropped, ids %s to %s',
                self.address, dropped, f'{self._dropped_min_id:,}', f'{self._dropped_max_id:,}')
        else:
            logger.warning('Audit export to %s resumed', self.address)

        # .. and start counting afresh.
        self._is_paused = False
        self._has_logged_full = False
        self._dropped_count = 0
        self._dropped_min_id = 0
        self._dropped_max_id = 0

# ################################################################################################################################

    def _on_refused(self) -> 'None':
        """ Keeps the batch for a retry and logs the first refusal of an outage.
        """
        self.batches_failed += 1

        if not self._is_paused:
            self._is_paused = True
            logger.warning('Audit export to %s paused - %s', self.address, self._last_reason)

# ################################################################################################################################

    def _run(self) -> 'None':
        """ Sends batches until told to stop, retrying a refused batch with a growing backoff.
        """
        backoff = ModuleCtx.Backoff_Min_Seconds

        while not self._stop.is_set():

            # Take a new batch unless one is still waiting to be accepted ..
            if not self._in_flight:

                # .. wait for a full batch or the flush interval, unless a full batch is already there ..
                queue_length = len(self._queue)
                has_full_batch = queue_length >= self._batch_size

                if not has_full_batch:
                    _ = self._wake.wait(self._flush_interval)
                    self._wake.clear()

                self._take_batch()

            # .. there may have been nothing to take ..
            if not self._in_flight:
                continue

            # .. send it and either move on to the next one ..
            if self._send_in_flight():
                self._on_accepted()
                backoff = ModuleCtx.Backoff_Min_Seconds

            # .. or wait before trying it again.
            else:
                self._on_refused()
                _ = self._stop.wait(backoff)
                backoff = min(backoff * 2, ModuleCtx.Backoff_Max_Seconds)

# ################################################################################################################################

    def flush_and_stop(self, timeout_seconds:'float') -> 'None':
        """ Sends what is queued for at most the given time, then stops the worker and the sender.
        """
        deadline = monotonic() + timeout_seconds

        # The worker finishes what it is sending first ..
        self._stop.set()
        self._wake.set()

        if self._worker:
            self._worker.join(timeout_seconds)

        # .. then what is left is sent while there is time and the collector takes it ..
        while monotonic() < deadline:

            if not self._in_flight:
                self._take_batch()

            if not self._in_flight:
                break

            if self._send_in_flight():
                self._on_accepted()
            else:
                break

        # .. and the sender is closed.
        self.sender.close()

# ################################################################################################################################

    def get_stats(self) -> 'stranydict':
        """ Returns the queue's counters and its current state.
        """
        out:'stranydict' = {
            'queue_length': len(self._queue),
            'in_flight': len(self._in_flight),
            'is_paused': self._is_paused,
            'emitted': self.emitted_count,
            'exported': self.exported_count,
            'dropped': self.dropped_total,
            'batches_ok': self.batches_ok,
            'batches_failed': self.batches_failed,
        }

        return out

# ################################################################################################################################
# ################################################################################################################################
