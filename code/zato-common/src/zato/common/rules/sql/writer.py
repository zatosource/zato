# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from datetime import datetime
from queue import Empty, Full, Queue
from threading import Event, Thread
from time import monotonic
from typing import NamedTuple

# SQLAlchemy
from sqlalchemy import insert, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# typing-extensions
from typing_extensions import TypeAlias

# Zato
from zato.common.defaults import default_cluster_id
from zato.common.typing_ import cast_

# Local
from .constants import Day_Bucket_Format, Default_Batch_Size, Default_Buffer_Capacity, \
    Default_Flush_Interval_Seconds, Event_Type_Rule_Fired_Daily, System_Actor
from .data import decision_write_list, DecisionWrite, rowdict, rowlist
from .database import SessionFactory
from .decisions import CapturePolicy, decision_to_row, find_existing_decision_ids, normalize_utc
from .errors import DecisionBufferFullError, DecisionWriterError, InvalidStoreInputError, RuleSQLStoreError
from .schema import rule_decision_table, rule_event_table
from .time_ import utc_now

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm import Session

    Session = Session

# ################################################################################################################################
# ################################################################################################################################

class _StopSignal:
    """ Private queue marker requesting a final flush and shutdown.
    """

# ################################################################################################################################

class _RollupKey(NamedTuple):
    """ One in-memory firing counter coordinate.
    """

    ruleset_id:    'int'
    rules_version: 'int'
    day_bucket:    'datetime'
    rule_id:       'str'

# ################################################################################################################################

queue_item:TypeAlias = DecisionWrite | _StopSignal
decision_queue:TypeAlias = Queue[queue_item]
rollup_count_dict:TypeAlias = dict[_RollupKey, int]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class DecisionWriterConfig:
    """ Batch size, flush cadence and bounded memory capacity.
    """

    batch_size:             'int'
    flush_interval_seconds: 'float'
    buffer_capacity:        'int'

    def __init__(
        self,
        *,
        batch_size:'int' = Default_Batch_Size,
        flush_interval_seconds:'float' = Default_Flush_Interval_Seconds,
        buffer_capacity:'int' = Default_Buffer_Capacity,
        ) -> 'None':

        # Require every bound to admit actual work ..
        if batch_size < 1:
            raise InvalidStoreInputError('Decision writer batch size must be at least 1')

        if flush_interval_seconds <= 0:
            raise InvalidStoreInputError('Decision writer flush interval must be greater than zero')

        if buffer_capacity < 1:
            raise InvalidStoreInputError('Decision writer buffer capacity must be at least 1')

        # .. then retain the validated writer configuration.
        self.batch_size             = batch_size
        self.flush_interval_seconds = flush_interval_seconds
        self.buffer_capacity        = buffer_capacity

# ################################################################################################################################
# ################################################################################################################################

class DecisionBatchWriter:
    """ Non-blocking decision submission with timed multi-row inserts and append-only firing rollups.
    """

    def __init__(
        self,
        session_factory:'SessionFactory',
        capture_policy:'CapturePolicy',
        config:'DecisionWriterConfig',
        ) -> 'None':

        # Retain the write policy and bounds shared with the background thread ..
        self._session_factory = session_factory
        self._capture_policy  = capture_policy
        self._config          = config

        # .. create the bounded handoff queue and lifecycle state ..
        self._queue:'decision_queue' = Queue(config.buffer_capacity)
        self._stop_signal = _StopSignal()
        self._stopped = Event()
        self._error:'Exception | None' = None
        self._started = False
        self._closing = False

        # .. and build the single writer thread without starting it yet.
        self._thread = Thread(
            target=self._run,
            name='zato-rule-decision-writer',
            daemon=True,
        )

# ################################################################################################################################

    def __enter__(self) -> 'DecisionBatchWriter':
        self.start()

        out = self
        return out

# ################################################################################################################################

    def __exit__(self, exception_type:'object', exception:'object', traceback:'object') -> 'None':
        _ = exception_type
        _ = exception
        _ = traceback

        self.close()

# ################################################################################################################################

    def _raise_if_failed(self) -> 'None':
        """ Raises the background failure on the caller's next interaction.
        """
        if self._error:
            message = f'Decision writer failed -> {self._error}'
            raise DecisionWriterError(message) from self._error

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the one background writer thread.
        """
        # Reject a second start because a Python thread cannot be restarted ..
        if self._started:
            raise DecisionWriterError('Decision writer is already started')

        # .. mark the lifecycle before the thread can observe it ..
        self._started = True

        # .. and start consuming queued decisions.
        self._thread.start()

# ################################################################################################################################

    def submit(self, decision:'DecisionWrite') -> 'None':
        """ Enqueues one decision without waiting for database work.
        """
        # Surface any prior background failure before accepting more work ..
        self._raise_if_failed()

        if not self._started:
            raise DecisionWriterError('Decision writer is not started')

        if self._closing:
            raise DecisionWriterError('Decision writer is closed')

        # .. place the decision in the bounded buffer without waiting ..
        try:
            self._queue.put_nowait(decision)

        # .. and reject saturation explicitly rather than silently dropping a mandatory header.
        except Full as e:
            raise DecisionBufferFullError('Decision writer buffer is full') from e

# ################################################################################################################################

    def close(self, timeout_seconds:'float | None' = None) -> 'None':
        """ Flushes all accepted decisions and waits for the writer to stop.
        """
        # A writer that never started has no accepted work to flush ..
        if not self._started:
            return

        # .. prevent submissions from landing behind the shutdown marker ..
        self._closing = True

        # .. surface a failure before a full queue could block shutdown ..
        self._raise_if_failed()

        # .. request shutdown after every previously queued decision, bounding the wait
        # .. so a full queue over a stuck thread can never block shutdown forever ..
        try:
            self._queue.put(self._stop_signal, timeout=timeout_seconds)
        except Full as e:
            raise DecisionWriterError('Decision writer buffer stayed full during shutdown') from e

        # .. wait for the final transaction to complete ..
        self._thread.join(timeout_seconds)

        # .. reject an incomplete shutdown ..
        thread_is_alive = self._thread.is_alive()
        if thread_is_alive:
            raise DecisionWriterError('Decision writer did not stop before the timeout')

        # .. and surface any final background failure.
        self._raise_if_failed()

# ################################################################################################################################

    def queued_count(self) -> 'int':
        """ Returns the number of entries currently waiting in memory.
        """
        out = self._queue.qsize()
        return out

# ################################################################################################################################

    def _day_bucket(self, occurred_at:'datetime') -> 'datetime':
        """ Returns the UTC start of the decision's daily firing-counter bucket.
        """
        # Normalize the decision timestamp ..
        occurred_at = normalize_utc(occurred_at)

        # .. format the portable day ..
        day_text = occurred_at.strftime(Day_Bucket_Format)

        # .. and parse its midnight boundary without database-specific date functions.
        out = datetime.strptime(day_text, Day_Bucket_Format)
        return out

# ################################################################################################################################

    def _rollup_counts(self, decisions:'decision_write_list') -> 'rollup_count_dict':
        """ Aggregates every fired rule in memory by ruleset, version and UTC day.
        """
        rollup_counts:'rollup_count_dict' = {}

        for decision in decisions:
            day_bucket = self._day_bucket(decision.occurred_at)

            for rule_id in decision.fired_rule_ids:
                key = _RollupKey(decision.ruleset_id, decision.rules_version, day_bucket, rule_id)

                if key in rollup_counts:
                    rollup_counts[key] += 1
                else:
                    rollup_counts[key] = 1

        return rollup_counts

# ################################################################################################################################

    def _upsert_rollups(self, session:'Session', rollup_counts:'rollup_count_dict') -> 'None':
        """ Adds each in-memory counter to its one daily row, so counter storage stays bounded
            by how many rules exist, never by traffic or by the flush cadence.
        """
        created_at = utc_now()

        for key, firing_count in rollup_counts.items():

            # Add the increment to the bucket's one existing row ..
            statement = update(rule_event_table)
            definition_condition = rule_event_table.c.definition_id == key.ruleset_id
            type_condition = rule_event_table.c.event_type == Event_Type_Rule_Fired_Daily
            bucket_condition = rule_event_table.c.bucket_start == key.day_bucket
            subject_condition = rule_event_table.c.subject_id == key.rule_id
            version_condition = rule_event_table.c.version == key.rules_version
            statement = statement.where(definition_condition)
            statement = statement.where(type_condition)
            statement = statement.where(bucket_condition)
            statement = statement.where(subject_condition)
            statement = statement.where(version_condition)
            incremented_count = rule_event_table.c.event_count + firing_count
            statement = statement.values(event_count=incremented_count)
            result = session.execute(statement)
            result = cast_(CursorResult, result)

            # .. and create that one row when this is the bucket's first increment.
            if result.rowcount == 0:
                event_row:'rowdict' = {
                    'cluster_id':    default_cluster_id,
                    'definition_id': key.ruleset_id,
                    'version':       key.rules_version,
                    'event_type':    Event_Type_Rule_Fired_Daily,
                    'actor':         System_Actor,
                    'subject_id':    key.rule_id,
                    'bucket_start':  key.day_bucket,
                    'event_count':   firing_count,
                    'created_at':    created_at,
                    'payload':       None,
                }
                statement = insert(rule_event_table)
                _ = session.execute(statement, event_row)

# ################################################################################################################################

    def _flush_batch(self, decisions:'decision_write_list') -> 'None':
        """ Writes one decision batch and its firing increments atomically.
        """
        # Convert every decision before opening the transaction ..
        decision_rows:'rowlist' = []

        for decision in decisions:
            row = decision_to_row(decision, self._capture_policy)
            decision_rows.append(row)

        rollup_counts = self._rollup_counts(decisions)
        session = self._session_factory()

        try:
            with session.begin():

                # .. persist one row per decision ..
                statement = insert(rule_decision_table)
                _ = session.execute(statement, decision_rows)

                # .. and fold the batch's firing counters into their daily rows in the same commit.
                self._upsert_rollups(session, rollup_counts)

        # Release the transactional session in every case.
        finally:
            session.close()

# ################################################################################################################################

    def _is_duplicate(self, decision_id:'str') -> 'bool':
        """ Returns whether one decision id already exists in the log.
        """
        session = self._session_factory()

        try:
            decision_ids = [decision_id]
            existing = find_existing_decision_ids(session, decision_ids)
        finally:
            session.close()

        out = decision_id in existing
        return out

# ################################################################################################################################

    def _flush_each(self, decisions:'decision_write_list') -> 'decision_write_list':
        """ Inserts decisions one at a time, skipping ids the log already contains.
        """
        landed:'decision_write_list' = []

        for decision in decisions:
            row = decision_to_row(decision, self._capture_policy)
            session = self._session_factory()

            # Insert this one decision in its own transaction ..
            try:
                with session.begin():
                    statement = insert(rule_decision_table)
                    _ = session.execute(statement, row)

            # .. skip a decision the log already holds, its header was never lost ..
            except IntegrityError:
                duplicate = self._is_duplicate(decision.decision_id)

                if duplicate:
                    continue

                # .. while a structural failure such as a missing ruleset must stop the writer loudly.
                raise

            finally:
                session.close()

            landed.append(decision)

        return landed

# ################################################################################################################################

    def _flush(self, decisions:'decision_write_list') -> 'None':
        """ Writes one batch, degrading to row-level inserts so one duplicate never stops the log.
        """
        # Try the whole batch and its rollups in one atomic transaction ..
        try:
            self._flush_batch(decisions)

        # .. and on an integrity failure retry row by row, counting rollups only for decisions
        # .. that actually landed, so a skipped duplicate is never counted twice.
        except IntegrityError:
            landed = self._flush_each(decisions)
            rollup_counts = self._rollup_counts(landed)

            if rollup_counts:
                session = self._session_factory()

                try:
                    with session.begin():
                        self._upsert_rollups(session, rollup_counts)
                finally:
                    session.close()

# ################################################################################################################################

    def _run(self) -> 'None':
        """ Consumes the buffer until a size, time or shutdown boundary requests a flush.
        """
        pending:'decision_write_list' = []
        current_time = monotonic()
        deadline = current_time + self._config.flush_interval_seconds

        try:
            while True:

                # Wait only until the next timed flush boundary ..
                current_time = monotonic()
                remaining_seconds = deadline - current_time
                if remaining_seconds < 0:
                    remaining_seconds = 0

                try:
                    item = self._queue.get(timeout=remaining_seconds)

                # .. flush an incomplete batch when its time boundary arrives ..
                except Empty:
                    if pending:
                        self._flush(pending)
                        pending.clear()

                    current_time = monotonic()
                    deadline = current_time + self._config.flush_interval_seconds
                    continue

                # .. flush all accepted work and stop when the shutdown marker arrives ..
                item_is_stop_signal = isinstance(item, _StopSignal)
                if item_is_stop_signal:
                    if pending:
                        self._flush(pending)

                    break

                # .. otherwise add the decision to the current in-memory batch ..
                pending.append(item)

                # .. and flush immediately when its size boundary is reached.
                pending_count = len(pending)
                if pending_count >= self._config.batch_size:
                    self._flush(pending)
                    pending.clear()
                    current_time = monotonic()
                    deadline = current_time + self._config.flush_interval_seconds

        # Preserve the complete background failure for the caller ..
        except (RuleSQLStoreError, SQLAlchemyError) as e:
            self._error = e

        # .. and mark the thread stopped after either success or failure.
        finally:
            self._stopped.set()

# ################################################################################################################################
# ################################################################################################################################
