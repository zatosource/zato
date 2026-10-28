# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from dataclasses import dataclass
from logging import getLogger
from threading import Condition, Event, Lock, Thread
from time import monotonic
from uuid import uuid4

# Zato
from zato.common.audit_log.api import get_audit_engine, metadata as audit_metadata
from zato.common.audit_log.export.api import get_audit_export
from zato.common.b2b.common.commit_retention import delete_expired_messages, delete_old_events, delete_old_held, \
    RetentionResult
from zato.common.b2b.common.commit_sql import write_claims, write_events, write_statuses, WriteKind
from zato.common.b2b.common.schema import create_tables
from zato.common.db_env.engine import call_database
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_, anylist, anytuple, callable_, floatnone
    any_ = any_
    anylist = anylist
    anytuple = anytuple
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

def write_transaction(connection:'Connection', tickets:'ticket_list', commit_id:'str') -> 'anylist':
    """ Writes the pending writes of one transaction, one statement for each table, in the order that the references
    between the tables require, assigns its result to each ticket, and returns the event writes it inserted.
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

    # The events that claims and status updates carry are inserted after the events of their own tickets ..
    carried:'anylist' = []

    if claims:
        results = write_claims(connection, _writes_of(claims), commit_id)
        _assign_results(claims, results)

        # .. a claim carries its event only into the transaction in which it recorded the message ..
        for ticket in claims:
            if ticket.write.event and ticket.result:
                carried.append(ticket.write.event)

    if statuses:
        results = write_statuses(connection, _writes_of(statuses))
        _assign_results(statuses, results)

        # .. and a status update only if the message has a record.
        for ticket in statuses:
            if ticket.write.event and not ticket.error:
                carried.append(ticket.write.event)

    out = _writes_of(events)
    out.extend(carried)

    if out:
        results = write_events(connection, out, commit_id)
        _assign_results(events, results)

    return out

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

        # The audit log tables and the B2B tables are created in the database of the writer, idempotently.
        audit_metadata.create_all(engine)
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

    def call(self, func:'callable_', *args:'any_') -> 'any_':
        """ Runs a database call outside the group commit, such as a read, serialized with the commits of this writer
        and in the thread pool of the gevent hub if the engine needs it.
        """
        with self._db_lock:
            out = self._call_database(func, *args)

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

        with self._db_lock:
            result = self._call_database(self._execute_function, func, commit_id, args)
            self._export(result.event_writes)

        out = result.value
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
        out.held = 0
        out.events = 0

        with self.engine.begin() as connection:

            out.messages = delete_expired_messages(connection, now, self.max_rows)

            # A held message goes before the events of its receipt, which are kept while it is held.
            for source in sources:
                out.held += delete_old_held(connection, source, now, self.max_rows)
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

        if out.messages or out.held or out.events:
            logger.info('B2B retention deleted %d message records, %d held messages and %d events', out.messages, out.held,
                out.events)

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
