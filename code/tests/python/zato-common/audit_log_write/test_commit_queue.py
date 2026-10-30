# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import joinall, sleep, spawn, Timeout
from gevent.event import Event

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import text

# Zato
from support import Backend_PostgreSQL, Object_Name, read_rows, record_statements, Server_Name
from zato.common.audit_log import retention_runner
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.buffer import PendingEvent
from zato.common.audit_log.commit_queue import CommitQueue
from zato.common.audit_log.commit_ticket import CommitTicket
from zato.common.audit_log.search_index import PostgreSQL_Pending_List_Limit_KB
from zato.common.audit_log.search_index_merge import get_search_index_merger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Engine
    from zato.common.audit_log.buffer import pending_event_list
    from zato.common.typing_ import any_, anylist, callable_, intlist, intnone

    any_ = any_
    anylist = anylist
    callable_ = callable_
    datetime = datetime
    Engine = Engine
    intlist = intlist
    intnone = intnone
    pending_event_list = pending_event_list

# ################################################################################################################################
# ################################################################################################################################

# How many concurrent callers the concurrency tests run
_caller_count = 64

# How many events each commit of the queue tests writes at most
_max_events = 5

# How long a commit of the queue tests takes, in seconds
_commit_time = 0.01

# How long a test waits for a background step at most, in seconds
_wait_timeout = 10

# How many inserts make the writer request a retention run
_retention_check_interval = 1000

# The message of the exception a failing commit raises
_error_message = 'Test error message'

# The trigram indexes of PostgreSQL the merger covers
_index_names = ('idx_event_search', 'idx_event_attr_search_value')

# The storage options of the indexes given
_reloptions_query = text('select relname, reloptions from pg_class where relname = any(:index_names)')

# The statements that write one event with one attribute, the same on each database, as their verbs and tables
_single_statements = [('INSERT', 'event'), ('INSERT', 'event_attr')]

# ################################################################################################################################
# ################################################################################################################################

def _insert(audit_log:'AuditLog', index:'int') -> 'intnone':
    """ Writes one event with a cid and an attribute of its own.
    """
    out = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Message_Received, Object_Name,
        cid=f'cid-{index}', msg_id=f'msg-{index}', outcome=AuditOutcome.OK, data=f'Order {index} from John Smith',
        attrs={'order_id': f'ORD-{index:04d}'})

    return out

# ################################################################################################################################

def _new_pending(index:'int') -> 'PendingEvent':
    """ An event of the queue tests, which only carries its position.
    """
    out = PendingEvent()
    out.values = {'cid': f'cid-{index}'}

    return out

# ################################################################################################################################
# ################################################################################################################################

class _FailingAuditLog(AuditLog):
    """ A writer whose commits fail until it is told otherwise, each failing commit taking a while.
    """

    def __init__(self) -> 'None':
        super().__init__(Server_Name)
        self.is_failing = True

    def _write_batch(self, batch:'pending_event_list') -> 'intnone':
        if self.is_failing:
            sleep(_commit_time)
            raise Exception(_error_message)

        out = super()._write_batch(batch)
        return out

# ################################################################################################################################

class _QueueWriter:
    """ A writer of the queue tests that records the batches it was given and gives each event an id.
    """

    def __init__(self) -> 'None':
        self.batch_sizes:'intlist' = []
        self.written_cids:'anylist' = []
        self.next_id = 1
        self.release_event:'Event | None' = None

    def write_batch(self, batch:'pending_event_list') -> 'int':

        batch_size = len(batch)
        self.batch_sizes.append(batch_size)

        if self.release_event:
            _ = self.release_event.wait()
        else:
            sleep(_commit_time)

        for pending in batch:
            pending.event_id = self.next_id
            self.next_id += 1
            self.written_cids.append(pending.values['cid'])

        out = self.next_id - 1
        return out

# ################################################################################################################################
# ################################################################################################################################

def test_concurrent_callers_receive_their_own_ids(audit_backend:'str') -> 'None':
    """ Concurrent callers share commits, and each of them receives the id of the row of its own event.
    """
    audit_log = AuditLog(Server_Name)
    engine = get_audit_engine()

    # Warm up the engine so that its pool and the schema exist before the callers start
    _ = _insert(audit_log, -1)

    with record_statements(engine) as recorder:

        greenlets:'anylist' = []

        for index in range(_caller_count):
            greenlet = spawn(_insert, audit_log, index)
            greenlets.append(greenlet)

        _ = joinall(greenlets, raise_error=True)

    # Each caller received the id of the row with its own cid ..
    cid_by_id:'anylist' = []

    for row in read_rows(event_table):
        cid_by_id.append((row['id'], row['cid']))

    cid_by_event_id = dict(cid_by_id)

    for index, greenlet in enumerate(greenlets):
        event_id = greenlet.value
        assert cid_by_event_id[event_id] == f'cid-{index}'

    # .. and the callers shared far fewer commits than there were of them.
    assert recorder.commit_count < _caller_count // 4

# ################################################################################################################################

def test_isolated_insert_is_one_transaction(audit_backend:'str') -> 'None':
    """ A caller with no concurrent callers commits its event at once, in a transaction of its own.
    """
    audit_log = AuditLog(Server_Name)
    engine = get_audit_engine()

    _ = _insert(audit_log, -1)

    with record_statements(engine) as recorder:
        event_id = _insert(audit_log, 0)

    assert recorder.commit_count == 1
    assert recorder.statements == _single_statements

    rows = read_rows(event_table)
    last_row = rows[-1]

    assert last_row['id'] == event_id

# ################################################################################################################################

def test_failing_commit_raises_in_each_caller(audit_backend:'str') -> 'None':
    """ An exception from a shared commit reaches every caller whose event was part of it,
    and the queue writes the events of later callers once the commits succeed.
    """
    audit_log = _FailingAuditLog()

    greenlets:'anylist' = []

    for index in range(_caller_count):
        greenlet = spawn(_insert, audit_log, index)
        greenlets.append(greenlet)

    _ = joinall(greenlets)

    for greenlet in greenlets:
        assert str(greenlet.exception) == _error_message

    # The queue is not left waiting for a commit that failed.
    audit_log.is_failing = False
    event_id = _insert(audit_log, _caller_count)

    rows = read_rows(event_table)

    assert len(rows) == 1
    assert rows[0]['id'] == event_id

# ################################################################################################################################

def test_needs_id_under_buffered_mode(audit_backend:'str') -> 'None':
    """ A caller that needs the id of its event receives it from a buffered writer as well.
    """
    audit_log = AuditLog(Server_Name, flush_max_size=500, flush_max_wait_ms=60_000)

    event_id = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Message_Received, Object_Name,
        cid='cid-needs-id', msg_id='msg-needs-id', outcome=AuditOutcome.OK, needs_id=True)

    rows = read_rows(event_table)

    assert len(rows) == 1
    assert rows[0]['id'] == event_id
    assert rows[0]['cid'] == 'cid-needs-id'

# ################################################################################################################################

def test_search_indexes_are_merged(audit_backend:'str') -> 'None':
    """ A process that writes events to PostgreSQL merges the event and attribute indexes,
    whose pending lists have the same limit, and no merger runs on SQLite.
    """
    audit_log = AuditLog(Server_Name)
    _ = _insert(audit_log, 0)

    engine = get_audit_engine()
    merger = get_search_index_merger(engine)

    if audit_backend != Backend_PostgreSQL:
        assert merger is None
        return

    assert merger is not None
    assert merger.index_names == _index_names
    assert merger._thread.is_alive()

    # The pending lists can be merged ..
    merger.merge()

    # .. and both indexes have the same limit on them.
    index_names = list(_index_names)

    with engine.connect() as connection:
        result = connection.execute(_reloptions_query, {'index_names': index_names})
        rows = result.all()

    options = dict(rows)

    expected = [f'gin_pending_list_limit={PostgreSQL_Pending_List_Limit_KB}']

    for index_name in _index_names:
        assert options[index_name] == expected, index_name

# ################################################################################################################################

def test_retention_runs_outside_the_write(audit_backend:'str', monkeypatch:'pytest.MonkeyPatch') -> 'None':
    """ The insert that crosses the retention count returns while the retention it requested is still running.
    """
    started_event = Event()
    release_event = Event()
    finished_event = Event()

    def run_retention(engine:'Engine', now:'datetime') -> 'None':
        started_event.set()
        _ = release_event.wait(_wait_timeout)
        finished_event.set()

    # The retention runs in the greenlet of the runner rather than in the thread pool of SQLite,
    # so that it can wait for the events of this test.
    def call_database(engine:'Engine', func:'callable_', *args:'any_') -> 'any_':
        out = func(*args)
        return out

    monkeypatch.setattr(retention_runner, 'run_retention', run_retention)
    monkeypatch.setattr(retention_runner, 'call_database', call_database)

    audit_log = AuditLog(Server_Name, flush_max_size=_retention_check_interval, flush_max_wait_ms=60_000)

    for index in range(_retention_check_interval):
        _ = _insert(audit_log, index)

    # The insert that wrote the batch returned before the retention completed ..
    assert not finished_event.is_set()
    assert len(read_rows(event_table)) == _retention_check_interval

    # .. which runs in the background.
    assert started_event.wait(_wait_timeout)

    release_event.set()
    assert finished_event.wait(_wait_timeout)

# ################################################################################################################################
# ################################################################################################################################

class TestCommitQueue:
    """ The queue on its own, with a writer that keeps the events in memory.
    """

    def test_batches_are_capped(self) -> 'None':
        writer = _QueueWriter()
        queue = CommitQueue(write_batch=writer.write_batch, max_events=_max_events)

        greenlets:'anylist' = []

        for index in range(16):
            pending = _new_pending(index)
            greenlet = spawn(queue.write, pending)
            greenlets.append(greenlet)

        _ = joinall(greenlets, raise_error=True)

        # The first caller commits alone and the others share commits of at most the maximum each ..
        assert writer.batch_sizes == [1, 5, 5, 5]

        # .. in the order they arrived, each one receiving the id of its own event.
        expected_cids:'anylist' = []

        for index in range(16):
            expected_cids.append(f'cid-{index}')

        assert writer.written_cids == expected_cids

        for index, greenlet in enumerate(greenlets):
            assert greenlet.value == index + 1

    def test_abandoned_waiter_is_not_written(self) -> 'None':
        writer = _QueueWriter()
        writer.release_event = Event()

        queue = CommitQueue(write_batch=writer.write_batch, max_events=_max_events)

        # The first caller holds the commit ..
        first = spawn(queue.write, _new_pending(0))
        sleep(0)

        # .. a second one stops waiting before its event is taken ..
        def write_with_timeout() -> 'intnone':
            with Timeout(_commit_time):
                out = queue.write(_new_pending(1))
            return out

        abandoned = spawn(write_with_timeout)
        _ = abandoned.join()

        assert isinstance(abandoned.exception, Timeout)

        # .. a third one waits ..
        third = spawn(queue.write, _new_pending(2))
        sleep(0)

        # .. and once the first commit completes, only the third event is written after it.
        writer.release_event.set()
        _ = joinall([first, third], raise_error=True)

        assert writer.written_cids == ['cid-0', 'cid-2']
        assert writer.batch_sizes == [1, 1]

        # The queue is idle again, so a new caller commits at once.
        writer.release_event = None
        event_id = queue.write(_new_pending(3))

        assert event_id == 3
        assert writer.batch_sizes == [1, 1, 1]

    def test_abandoned_runner_passes_its_batch_on(self) -> 'None':
        queue = CommitQueue(write_batch=_QueueWriter().write_batch, max_events=_max_events)

        first = CommitTicket(_new_pending(0))
        second = CommitTicket(_new_pending(1))

        # Two callers wait while a commit is in progress ..
        queue._is_committing = True
        queue._waiting.extend([first, second])

        # .. the commit completes and the first of them is to run the next one ..
        queue._hand_off()

        assert first.batch == [first, second]
        assert first.ready.is_set()

        # .. but it stops waiting before it begins, so the second one is to commit its own event.
        queue._abandon(first)

        assert first.batch is None
        assert second.batch == [second]
        assert second.ready.is_set()
        assert queue._waiting == []
        assert queue._is_committing

# ################################################################################################################################
# ################################################################################################################################
