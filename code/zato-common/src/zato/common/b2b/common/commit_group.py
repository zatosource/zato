# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from queue import Queue
from threading import Condition, Lock, Thread
from time import monotonic, time
from typing import NamedTuple
from uuid import uuid4

# Zato
from zato.common.audit_log.api import get_audit_engine, metadata as audit_metadata
from zato.common.audit_log.export.api import get_audit_export
from zato.common.b2b.common.commit_retention import delete_candidates, delete_retained, read_candidate_rows, \
    RetentionResult, select_retained
from zato.common.b2b.common.commit_sql import write_transaction
from zato.common.b2b.common.commit_ticket import CommitTicket, GroupProgress, TransactionResult
from zato.common.b2b.common.commit_timing import timing_log
from zato.common.b2b.common.schema import create_tables
from zato.common.db_env.common import Type_SQLite
from zato.common.db_env.engine import call_database
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.b2b.common.commit_timing import TimingLog
    from zato.common.typing_ import any_, anylist, anytuple, callable_, floatnone, strlist
    any_ = any_
    anylist = anylist
    anytuple = anytuple
    callable_ = callable_
    datetime = datetime
    Engine = Engine
    floatnone = floatnone
    strlist = strlist
    TimingLog = TimingLog

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

ticket_list = list[CommitTicket]
queue_list  = list[Queue]
thread_list = list[Thread]
lane_groups = dict[int, GroupProgress]

# The environment variables that configure the group commit.
Env_Commit_Interval_Ms = 'Zato_B2B_Commit_Interval_Ms'
Env_Commit_Max_Rows    = 'Zato_B2B_Commit_Max_Rows'

# How long the pending writes wait for a commit, and how many rows they may reach before they are committed at once.
Default_Commit_Interval_Ms = 100
Default_Commit_Max_Rows    = 1000

# How often retention runs between two commits, how many rows of each kind one batch of it deletes,
# and how often the batches run while each one reaches that limit.
Retention_Interval_Seconds       = 60
Retention_Batch_Rows             = 500
Retention_Batch_Interval_Seconds = 0.5

# How many groups a pipelined writer holds at a time - one being committed and one executing its statements.
_lane_count = 2

# ################################################################################################################################
# ################################################################################################################################

class RetentionJob(NamedTuple):
    """ One batch of retention of a pipelined writer - the time it deletes as of, and the last group of each lane,
    whose commits precede its select.
    """
    now:    'datetime'
    groups: 'list[GroupProgress]'

# ################################################################################################################################
# ################################################################################################################################

def get_commit_interval_ms() -> 'int':
    """ Returns how long, in milliseconds, the pending writes wait before they are committed.
    """
    if value := os.environ.get(Env_Commit_Interval_Ms, ''):
        out = int(value)
    else:
        out = Default_Commit_Interval_Ms

    return out

# ################################################################################################################################

def get_commit_max_rows() -> 'int':
    """ Returns how many rows the pending writes reach before they are committed without waiting for the interval.
    """
    if value := os.environ.get(Env_Commit_Max_Rows, ''):
        out = int(value)
    else:
        out = Default_Commit_Max_Rows

    return out

# ################################################################################################################################
# ################################################################################################################################

class GroupCommitWriter:
    """ Commits the writes of the B2B protocols - duplicate claims, status updates and audit events - in one transaction
    per interval, or sooner once the pending rows reach a limit. Each caller waits until the transaction that holds
    its write is committed. Retention runs between two commits.
    """

    def __init__(
        self,
        engine:'Engine',
        *,
        interval_ms:'int | None' = None,
        max_rows:'int | None' = None,
        clock:'callable_' = monotonic,
        is_started:'bool' = True,
        ) -> 'None':

        self.engine = engine

        # The audit log tables and the B2B tables are created in the database of the writer, idempotently.
        audit_metadata.create_all(engine)
        create_tables(engine)

        if interval_ms is None:
            interval_ms = get_commit_interval_ms()

        if max_rows is None:
            max_rows = get_commit_max_rows()

        self.interval_ms = interval_ms
        self.max_rows = max_rows

        # One batch of retention deletes no more rows of each kind than one transaction of the writer holds.
        self.retention_batch_rows = min(max_rows, Retention_Batch_Rows)

        # A database with concurrent writers executes the statements of the next group while the previous one
        # is being committed. SQLite has one writer, so its groups are committed one after another.
        self.is_pipelined = engine.dialect.name != Type_SQLite

        # The monotonic clock the interval is measured with.
        self.clock = clock

        # Guards the pending writes, and wakes the commit thread when a write arrives.
        self._condition = Condition()
        self._pending:'ticket_list' = []
        self._pending_rows = 0
        self._first_added_at = 0.0

        # Serializes the database calls of this writer - its commits, its retention and the reads made through it.
        self._db_lock = Lock()

        # The sources whose B2B audit events retention deletes.
        self._event_sources:'set[str]' = set()

        self._last_retention_at = self.clock()
        self._is_stopped = False

        # Whether the last batch of retention reached the row limit, so that the next batch is due without the interval.
        self._has_retention_backlog = False

        # Whether a batch of retention of a pipelined writer is in its lane, so that the next one waits for its commit.
        self._is_retention_running = False

        # When the batch in the lane started, and whether the next one fell due before it was committed.
        self._retention_started_at = self._last_retention_at
        self._is_retention_requested = False

        self.is_started = is_started

        # The queues and the threads of the lanes of a pipelined writer, each committing its groups one after another.
        self._lanes:'queue_list' = []
        self._lane_threads:'thread_list' = []

        # The lane of retention of a pipelined writer, whose commits do not delay the groups.
        self._retention_lane = Queue()

        if is_started:

            if self.is_pipelined:
                for idx in range(_lane_count):
                    lane = Queue()
                    lane_thread = Thread(target=self._run_lane, args=(lane,), name=f'b2b-commit-lane-{idx}', daemon=True)
                    lane_thread.start()
                    self._lanes.append(lane)
                    self._lane_threads.append(lane_thread)

                lane_thread = Thread(target=self._run_retention_lane, name='b2b-retention-lane', daemon=True)
                lane_thread.start()
                self._lane_threads.append(lane_thread)

            thread = Thread(target=self._run, name='b2b-commit-group', daemon=True)
            thread.start()

# ################################################################################################################################

    def add_event_source(self, source:'str') -> 'None':
        """ Includes the B2B audit events of one source in retention.
        """
        with self._condition:
            self._event_sources.add(source)

# ################################################################################################################################

    def enqueue(self, write:'any_', row_count:'int') -> 'CommitTicket':
        """ Adds one write to the next transaction and returns its ticket, without waiting for the commit.
        """
        out = CommitTicket(write, row_count)

        with self._condition:

            if not self._pending:
                self._first_added_at = self.clock()

            self._pending.append(out)
            self._pending_rows += row_count

            self._condition.notify()

        return out

# ################################################################################################################################

    def submit(self, write:'any_', row_count:'int') -> 'CommitTicket':
        """ Adds one write to the next transaction and returns its ticket. A writer without a commit thread
        commits in the thread of the caller.
        """
        out = self.enqueue(write, row_count)

        if not self.is_started:
            _ = self.commit_due()

        return out

# ################################################################################################################################

    def write(self, write:'any_', row_count:'int') -> 'any_':
        """ Adds one write to the next transaction, waits until the transaction is committed and returns the result.
        """
        ticket = self.submit(write, row_count)

        out = ticket.wait()
        return out

# ################################################################################################################################

    def _is_due(self) -> 'bool':
        """ Says whether the pending writes are to be committed now. The condition is held by the caller.
        """
        if not self._pending:
            out = False

        elif self._pending_rows >= self.max_rows:
            out = True

        else:
            waited = self.clock() - self._first_added_at
            out = waited * 1000 >= self.interval_ms

        return out

# ################################################################################################################################

    def _time_to_due(self) -> 'floatnone':
        """ Returns how many seconds remain until the pending writes are due, or None when there are none.
        The condition is held by the caller.
        """
        if not self._pending:
            out = None
        else:
            waited = self.clock() - self._first_added_at
            remaining = self.interval_ms / 1000 - waited
            out = max(remaining, 0.0)

        return out

# ################################################################################################################################

    def _take(self) -> 'ticket_list':
        """ Takes out every pending write. The condition is held by the caller.
        """
        out = self._pending

        self._pending = []
        self._pending_rows = 0

        return out

# ################################################################################################################################

    def commit_due(self) -> 'bool':
        """ Commits the pending writes if their interval elapsed or their rows reached the limit,
        and says whether it did.
        """
        with self._condition:
            if self._is_due():
                tickets = self._take()
            else:
                tickets = []

        if tickets:
            self._commit(tickets)
            out = True
        else:
            out = False

        return out

# ################################################################################################################################

    def _execute(self, tickets:'ticket_list', commit_id:'str') -> 'anylist':
        """ Writes and commits one transaction, and returns the event writes it inserted.
        """
        with self.engine.begin() as connection:
            out = write_transaction(connection, tickets, commit_id)

        return out

# ################################################################################################################################

    def _export(self, event_writes:'anylist') -> 'None':
        """ Hands the committed audit events to the OTLP export of the process, if it has one.
        """
        if not (export := get_audit_export()):
            return

        batch:'anylist' = []

        for write in event_writes:
            batch.append(write.pending)

        if batch:
            try:
                export.emit_batch(batch)
            except Exception:
                logger.exception('Audit export could not take a batch of %d B2B events', len(batch))

# ################################################################################################################################

    def _commit(self, tickets:'ticket_list') -> 'None':
        """ Commits one transaction and releases the caller of each write in it, with the error of the commit if it failed.
        """
        commit_id = uuid4().hex

        with self._db_lock:
            try:
                event_writes = self._call_database(self._execute, tickets, commit_id)
            except Exception as e:
                logger.warning('B2B commit of %d writes failed: %s', len(tickets), e)
                for ticket in tickets:
                    ticket.error = e
            else:
                self._export(event_writes)

        # The callers are released from the thread of the writer, never from the thread pool.
        for ticket in tickets:
            ticket.release()

# ################################################################################################################################

    def _execute_pipelined(self, commit_id:'str', progress:'GroupProgress') -> 'anylist':
        """ Writes one transaction while holding the database lock of this writer, and commits it without the lock,
        so that the next group executes its statements during the commit. Returns the event writes it inserted.
        """
        progress.lane_started_at = time()

        with self.engine.connect() as connection:

            # A transaction whose statements fail is rolled back when its connection is closed ..
            with self._db_lock:
                progress.lock_acquired_at = time()
                transaction = connection.begin()
                out = write_transaction(connection, progress.tickets, commit_id)

            # .. and once they are executed, the next group may execute its own.
            progress.statements_done_at = time()
            progress.statements_done.set()
            transaction.commit()
            progress.committed_at = time()

        return out

# ################################################################################################################################

    def _commit_pipelined(self, progress:'GroupProgress') -> 'None':
        """ Commits one group of a pipelined writer and releases the caller of each write in it, with the error
        of the commit if it failed.
        """
        commit_id = uuid4().hex
        tickets = progress.tickets

        try:
            event_writes = self._execute_pipelined(commit_id, progress)
        except Exception as e:
            logger.warning('B2B commit of %d writes failed: %s', len(tickets), e)
            for ticket in tickets:
                ticket.error = e
        else:
            self._export(event_writes)

        # A group whose statements failed does not hold up the next one, nor the next batch of retention ..
        progress.statements_done.set()
        progress.is_committed.set()

        # .. and its callers are released.
        for ticket in tickets:
            ticket.release()

        if timing_log:
            self._write_group_timing(timing_log, progress)

# ################################################################################################################################

    def _write_group_timing(self, log:'TimingLog', progress:'GroupProgress') -> 'None':
        """ Prototype - writes how long each step of the commit of one group took.
        """
        tickets = progress.tickets
        first_enqueued_at = min(ticket.enqueued_at for ticket in tickets)
        rows = sum(ticket.row_count for ticket in tickets)
        released_at = time()

        log.write({
            'type': 'group',
            'tickets': len(tickets),
            'rows': rows,
            'pending_ms': round((progress.taken_at - first_enqueued_at) * 1000, 2),
            'lane_ms': round((progress.lane_started_at - progress.taken_at) * 1000, 2),
            'lock_ms': round((progress.lock_acquired_at - progress.lane_started_at) * 1000, 2),
            'exec_ms': round((progress.statements_done_at - progress.lock_acquired_at) * 1000, 2),
            'commit_ms': round((progress.committed_at - progress.statements_done_at) * 1000, 2),
            'release_ms': round((released_at - progress.committed_at) * 1000, 2),
        })

# ################################################################################################################################

    def _run_lane(self, lane:'Queue') -> 'None':
        """ Commits the groups of one lane in the order they were handed to it, until it receives None.
        """
        while progress := lane.get():
            self._commit_pipelined(progress)

# ################################################################################################################################

    def call(self, func:'callable_', *args:'any_') -> 'any_':
        """ Runs a database call outside the group commit, such as a read, serialized with the commits of this writer
        and in the thread pool of the gevent hub if the engine needs it.
        """
        started_at = time()

        with self._db_lock:
            lock_acquired_at = time()
            out = self._call_database(func, *args)

        if timing_log:
            timing_log.write({
                'type': 'call',
                'func': func.__name__,
                'lock_ms': round((lock_acquired_at - started_at) * 1000, 2),
                'exec_ms': round((time() - lock_acquired_at) * 1000, 2),
            })

        return out

# ################################################################################################################################

    def _execute_function(self, func:'callable_', commit_id:'str', args:'anytuple') -> 'TransactionResult':
        with self.engine.begin() as connection:
            out = func(connection, commit_id, *args)

        return out

# ################################################################################################################################

    def run_transaction(self, func:'callable_', *args:'any_') -> 'any_':
        """ Runs a function of several dependent statements in one transaction of its own, serialized with the commits
        of this writer. The function receives the connection and an identifier of the transaction, and returns
        a TransactionResult whose committed events are exported like those of a group commit.
        """
        commit_id = uuid4().hex
        started_at = time()

        with self._db_lock:
            lock_acquired_at = time()
            result = self._call_database(self._execute_function, func, commit_id, args)
            self._export(result.event_writes)

        if timing_log:
            timing_log.write({
                'type': 'transaction',
                'func': func.__name__,
                'lock_ms': round((lock_acquired_at - started_at) * 1000, 2),
                'exec_ms': round((time() - lock_acquired_at) * 1000, 2),
            })

        out = result.value
        return out

# ################################################################################################################################

    def _call_database(self, func:'callable_', *args:'any_') -> 'any_':
        """ Runs one database call of this writer, in the thread pool of the gevent hub if the engine needs it.
        """
        out = call_database(self.engine, func, *args)
        return out

# ################################################################################################################################

    def _execute_retention(self, now:'datetime', sources:'strlist') -> 'RetentionResult':
        with self.engine.begin() as connection:
            out = delete_retained(connection, now, sources, self.retention_batch_rows)

        return out

# ################################################################################################################################

    def _execute_retention_pipelined(self, now:'datetime', sources:'strlist') -> 'RetentionResult':
        """ Finds the rows of one batch of retention without the database lock of this writer, deletes them while
        holding the lock, and commits without it, so that the groups execute their statements during the select
        and during the commit.
        """
        started_at = time()

        with self.engine.connect() as connection:

            # The rows due for deletion are selected and read in a transaction of their own, without the lock ..
            with connection.begin():
                candidates = select_retained(connection, now, sources, self.retention_batch_rows)
                read_candidate_rows(connection, candidates)

            selected_at = time()

            # .. those still due are deleted while holding it ..
            with self._db_lock:
                lock_acquired_at = time()
                transaction = connection.begin()
                out = delete_candidates(connection, now, candidates)

            # .. and the deletion is committed without it.
            statements_done_at = time()
            transaction.commit()

        if timing_log:
            timing_log.write({
                'type': 'retention',
                'messages': out.messages,
                'held': out.held,
                'events': out.events,
                'select_ms': round((selected_at - started_at) * 1000, 2),
                'lock_ms': round((lock_acquired_at - selected_at) * 1000, 2),
                'exec_ms': round((statements_done_at - lock_acquired_at) * 1000, 2),
                'commit_ms': round((time() - statements_done_at) * 1000, 2),
            })

        return out

# ################################################################################################################################

    def run_retention(self, now:'datetime') -> 'RetentionResult':
        """ Runs one batch of retention, in a transaction of its own.
        """
        with self._condition:
            sources = sorted(self._event_sources)

        if self.is_pipelined:
            out = self._execute_retention_pipelined(now, sources)
        else:
            with self._db_lock:
                out = self._call_database(self._execute_retention, now, sources)

        if out.messages or out.held or out.events:
            logger.info('B2B retention deleted %d message records, %d held messages and %d events', out.messages, out.held,
                out.events)

        return out

# ################################################################################################################################

    def _retain(self, now:'datetime') -> 'None':
        """ Runs one batch of retention and records whether the next one is due without the usual interval.
        """
        try:
            result = self.run_retention(now)
        except Exception:
            has_backlog = False
            logger.exception('B2B retention failed')
        else:
            has_backlog = result.is_at_limit(self.retention_batch_rows)

        # A batch that fell due while this one ran follows it as a batch of a backlog.
        with self._condition:
            self._has_retention_backlog = has_backlog or self._is_retention_requested
            self._is_retention_requested = False
            self._last_retention_at = self.clock()
            self._is_retention_running = False
            self._condition.notify()

# ################################################################################################################################

    def _run_retention_lane(self) -> 'None':
        """ Runs the batches of retention of a pipelined writer, until it receives None.
        """
        while job := self._retention_lane.get():

            # The groups handed to the lanes before the batch are committed before it selects what is due ..
            for progress in job.groups:
                _ = progress.is_committed.wait()

            # .. so that it sees their rows.
            self._retain(job.now)

# ################################################################################################################################

    def _run_retention_if_due(self, groups:'lane_groups') -> 'None':
        """ Runs one batch of retention between two commits once its interval elapsed, and the next batch after
        the next commit for as long as each batch reaches the row limit. A pipelined writer hands the batch to its lane,
        with the last group of each lane.
        """
        with self._condition:

            now_clock = self.clock()

            # A backlog is deleted batch by batch at an interval of its own ..
            if self._has_retention_backlog:
                interval = Retention_Batch_Interval_Seconds

            # .. and otherwise retention runs at the usual one ..
            else:
                interval = Retention_Interval_Seconds

            # .. a batch still in its lane is committed before the next one starts, and a batch that falls due
            # in the meantime follows it ..
            if self._is_retention_running:
                if now_clock - self._retention_started_at >= interval:
                    self._is_retention_requested = True
                return

            since_last = now_clock - self._last_retention_at

            if since_last < interval:
                return

            # .. and otherwise the batch starts now.
            self._is_retention_running = self.is_pipelined
            self._retention_started_at = now_clock

        now = utcnow()

        if self.is_pipelined:
            job = RetentionJob(now, list(groups.values()))
            self._retention_lane.put(job)
        else:
            self._retain(now)

# ################################################################################################################################

    def _time_to_batch(self) -> 'floatnone':
        """ Returns how many seconds remain until the next batch of retention after one that reached the row limit,
        or None when there is no such batch or one is still in its lane.
        """
        if self._is_retention_running:
            out = None

        elif self._has_retention_backlog:
            waited = self.clock() - self._last_retention_at
            remaining = Retention_Batch_Interval_Seconds - waited
            out = max(remaining, 0.0)
        else:
            out = None

        return out

# ################################################################################################################################

    def _has_work(self) -> 'bool':
        """ Says whether the commit thread is to stop waiting - the writer is stopped, the pending writes are due,
        or there are none and the next batch of retention is due. The condition is held by the caller.
        """
        if self._is_stopped:
            out = True

        # Pending writes are committed first, and the next batch of retention follows their commit ..
        elif self._pending:
            out = self._is_due()

        # .. while without them, the batches follow one another at their interval.
        elif (remaining := self._time_to_batch()) is None:
            out = False
        else:
            out = remaining <= 0

        return out

# ################################################################################################################################

    def _time_to_wake(self) -> 'floatnone':
        """ Returns how many seconds the commit thread waits for at most - until the pending writes are due,
        or without them, until the next batch of retention. The condition is held by the caller.
        """
        if self._pending:
            out = self._time_to_due()
        else:
            out = self._time_to_batch()

        return out

# ################################################################################################################################

    def _run(self) -> 'None':
        """ Commits the pending writes whenever they are due, until the writer is stopped. A pipelined writer hands
        its groups to its lanes in turn, each group once the statements of the previous one are executed.
        """
        # The lane the next group goes to, and the last group each lane received.
        lane_idx = 0
        groups:'lane_groups' = {}

        while True:

            with self._condition:

                while not self._has_work():
                    timeout = self._time_to_wake()
                    _ = self._condition.wait(timeout)

                # A stopped writer commits what it still holds and ends.
                is_stopped = self._is_stopped
                tickets = self._take()

            if tickets:
                if self.is_pipelined:
                    progress = GroupProgress(tickets)
                    self._lanes[lane_idx].put(progress)
                    groups[lane_idx] = progress
                    lane_idx = (lane_idx + 1) % _lane_count

                    # The next group is taken once the statements of this one are executed.
                    _ = progress.statements_done.wait()
                else:
                    self._commit(tickets)

            if is_stopped:

                # A stopped writer ends once its lanes committed every group they hold.
                for lane in self._lanes:
                    lane.put(None)

                self._retention_lane.put(None)

                for lane_thread in self._lane_threads:
                    lane_thread.join()

                break

            self._run_retention_if_due(groups)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Commits the pending writes and ends the commit thread.
        """
        with self._condition:
            self._is_stopped = True
            self._condition.notify()

# ################################################################################################################################
# ################################################################################################################################

# The writer of each audit log database this process writes to.
_writers:'dict[Engine, GroupCommitWriter]' = {}
_writers_lock = Lock()

def get_writer() -> 'GroupCommitWriter':
    """ Returns the group commit writer of this process for the audit log database.
    """
    engine = get_audit_engine()

    with _writers_lock:
        if not (out := _writers.get(engine)):
            out = GroupCommitWriter(engine)
            _writers[engine] = out

    return out

# ################################################################################################################################
# ################################################################################################################################
