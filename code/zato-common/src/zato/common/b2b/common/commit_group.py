# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger
from threading import Condition, Event, Lock, Thread
from time import monotonic
from uuid import uuid4

# Zato
from zato.common.audit_log.api import get_audit_engine
from zato.common.audit_log.export.api import get_audit_export
from zato.common.b2b.common.commit_retention import delete_expired_messages, delete_old_events, RetentionResult
from zato.common.b2b.common.commit_sql import write_claims, write_events, write_statuses, WriteKind
from zato.common.b2b.common.schema import create_tables
from zato.common.db_env.engine import call_database
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_, anylist, callable_, floatnone
    any_ = any_
    anylist = anylist
    callable_ = callable_
    Connection = Connection
    datetime = datetime
    Engine = Engine
    floatnone = floatnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

ticket_list = list['CommitTicket']

# The environment variables that configure the group commit.
Env_Commit_Interval_Ms = 'Zato_B2B_Commit_Interval_Ms'
Env_Commit_Max_Rows    = 'Zato_B2B_Commit_Max_Rows'

# How long the pending writes wait for a commit, and how many rows they may reach before they are committed at once.
Default_Commit_Interval_Ms = 100
Default_Commit_Max_Rows    = 1000

# How often retention runs between two commits.
Retention_Interval_Seconds = 60

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

def write_transaction(connection:'Connection', tickets:'ticket_list', commit_id:'str') -> 'None':
    """ Writes the pending writes of one transaction, one statement for each table, in the order that the references
    between the tables require, and assigns its result to each ticket.
    """
    claims:'ticket_list' = []
    statuses:'ticket_list' = []
    events:'ticket_list' = []

    for ticket in tickets:
        kind = ticket.write.kind

        if kind == WriteKind.Claim:
            claims.append(ticket)
        elif kind == WriteKind.Status:
            statuses.append(ticket)
        else:
            events.append(ticket)

    if claims:
        results = write_claims(connection, _writes_of(claims), commit_id)
        _assign_results(claims, results)

    if statuses:
        results = write_statuses(connection, _writes_of(statuses))
        _assign_results(statuses, results)

    if events:
        results = write_events(connection, _writes_of(events), commit_id)
        _assign_results(events, results)

# ################################################################################################################################

def _writes_of(tickets:'ticket_list') -> 'anylist':
    out:'anylist' = []

    for ticket in tickets:
        out.append(ticket.write)

    return out

# ################################################################################################################################

def _assign_results(tickets:'ticket_list', results:'anylist') -> 'None':
    for ticket, result in zip(tickets, results):

        # A write that the transaction refused on its own carries its exception as the result.
        if isinstance(result, Exception):
            ticket.error = result
        else:
            ticket.result = result

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

        # The tables are created in the database of the writer, idempotently.
        create_tables(engine)

        if interval_ms is None:
            interval_ms = get_commit_interval_ms()

        if max_rows is None:
            max_rows = get_commit_max_rows()

        self.interval_ms = interval_ms
        self.max_rows = max_rows

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

        self.is_started = is_started

        if is_started:
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

    def _execute(self, tickets:'ticket_list', commit_id:'str') -> 'None':
        """ Writes and commits one transaction.
        """
        with self.engine.begin() as connection:
            write_transaction(connection, tickets, commit_id)

# ################################################################################################################################

    def _export(self, tickets:'ticket_list') -> 'None':
        """ Hands the committed audit events to the OTLP export of the process, if it has one.
        """
        if not (export := get_audit_export()):
            return

        batch:'anylist' = []

        for ticket in tickets:
            if ticket.write.kind == WriteKind.Event:
                batch.append(ticket.write.pending)

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
                _ = self._call_database(self._execute, tickets, commit_id)
            except Exception as e:
                logger.warning('B2B commit of %d writes failed: %s', len(tickets), e)
                for ticket in tickets:
                    ticket.error = e
            else:
                self._export(tickets)

        # The callers are released from the thread of the writer, never from the thread pool.
        for ticket in tickets:
            ticket.release()

# ################################################################################################################################

    def call(self, func:'callable_', *args:'any_') -> 'any_':
        """ Runs a database call outside the group commit, such as a read, serialized with the commits of this writer
        and in the thread pool of the gevent hub if the engine needs it.
        """
        with self._db_lock:
            out = self._call_database(func, *args)

        return out

# ################################################################################################################################

    def _call_database(self, func:'callable_', *args:'any_') -> 'any_':
        """ Runs one database call of this writer, in the thread pool of the gevent hub if the engine needs it.
        """
        out = call_database(self.engine, func, *args)
        return out

# ################################################################################################################################

    def _run_retention_transaction(self, now:'datetime', sources:'list[str]') -> 'RetentionResult':
        """ Deletes in one transaction what retention deletes, each kind of row up to the row limit.
        """
        out = RetentionResult()
        out.events = 0

        with self.engine.begin() as connection:

            out.messages = delete_expired_messages(connection, now, self.max_rows)

            for source in sources:
                out.events += delete_old_events(connection, source, now, self.max_rows)

        return out

# ################################################################################################################################

    def run_retention(self, now:'datetime') -> 'RetentionResult':
        """ Runs one retention, in a transaction of its own.
        """
        with self._condition:
            sources = sorted(self._event_sources)

        with self._db_lock:
            out = self._call_database(self._run_retention_transaction, now, sources)

        self._last_retention_at = self.clock()

        if out.messages or out.events:
            logger.info('B2B retention deleted %d message records and %d events', out.messages, out.events)

        return out

# ################################################################################################################################

    def _run_retention_if_due(self) -> 'None':
        """ Runs retention between two commits once its interval elapsed.
        """
        since_last = self.clock() - self._last_retention_at

        if since_last >= Retention_Interval_Seconds:
            now = utcnow()
            try:
                _ = self.run_retention(now)
            except Exception:
                logger.exception('B2B retention failed')

# ################################################################################################################################

    def _run(self) -> 'None':
        """ Commits the pending writes whenever they are due, until the writer is stopped.
        """
        while True:

            with self._condition:

                while not self._is_stopped and not self._is_due():
                    timeout = self._time_to_due()
                    _ = self._condition.wait(timeout)

                # A stopped writer commits what it still holds and ends.
                is_stopped = self._is_stopped
                tickets = self._take()

            if tickets:
                self._commit(tickets)

            if is_stopped:
                break

            self._run_retention_if_due()

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
