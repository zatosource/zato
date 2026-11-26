# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from threading import enumerate as enumerate_threads

# gevent
from gevent import joinall, sleep, spawn, Timeout
from gevent.event import Event

# SQLAlchemy
from sqlalchemy import text

# Zato
from support import Object_Name, read_rows, record_statements, Server_Name
from zato.common.audit_log.api import event_table, AuditEvent, AuditLog, AuditOutcome, AuditSource, ModuleCtx
from zato.common.audit_log.retention_runner import stop_retention_runner
from zato.common.db_env.database import get_database_engine
from zato.common.audit_log.pending import PendingEvent
from zato.common.audit_log.search_index import PostgreSQL_Pending_List_Limit_KB
from zato.common.audit_log.search_index_merge import get_search_index_merger
from zato.common.db_env.commit_queue import CommitQueue
from zato.common.db_env.commit_ticket import CommitTicket

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch
    from sqlalchemy.engine import Engine
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.typing_ import anylist, intlist, intnone, strlist

    anylist = anylist
    Engine = Engine
    intlist = intlist
    intnone = intnone
    MonkeyPatch = MonkeyPatch
    pending_event_list = pending_event_list
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# How many concurrent callers the concurrency tests run
_caller_count = 64

# How many events each commit of the queue tests writes at most
_max_events = 5

# How many events each caller of the event list tests writes together
_event_list_size = 3

# How much of a commit's capacity an event of the queue tests takes, unless a test says otherwise
_event_weight = 1

# How much of a commit's capacity a heavy event of the queue tests takes
_heavy_event_weight = 3

# How long a commit of the queue tests takes, in seconds
_commit_time = 0.01

# How long a test waits for a background step at most, in seconds
_wait_timeout = 10

# The interval between retention runs with which the first commit requests a run, in seconds
_retention_interval_seconds = '0'

# How many events the retention test inserts
_retention_event_count = 10

# The name of the thread that the retention runs in
_retention_thread_name = 'audit-log-retention'

# The message of the exception a failing commit raises
_error_message = 'Test error message'

# The word and trigram indexes of PostgreSQL the merger covers
_index_names = ('idx_event_search', 'idx_event_payload_search', 'idx_event_attr_search_value')

# The storage options of the indexes given
_reloptions_query = text('select relname, reloptions from pg_class where relname = any(:index_names)')

# The statements that write one event with a payload and one attribute, the same on each database, as their verbs and tables
_single_statements = [('SELECT', 'event_payload'), ('INSERT', 'event_payload'), ('INSERT', 'event'), ('INSERT', 'event_attr')]

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

def _insert_failing(audit_log:'AuditLog', index:'int') -> 'Exception':
    """ Writes one event whose commit is to fail and returns the exception raised, which a greenlet would print
    if it ended with it.
    """
    try:
        _ = _insert(audit_log, index)
    except Exception as e:
        return e

    raise Exception(f'Event {index} was written although its commit was to fail')

# ################################################################################################################################

def _write_event_list(audit_log:'AuditLog', index:'int') -> 'pending_event_list':
    """ Writes several events of one operation together, each with a cid of its own.
    """
    out:'pending_event_list' = []

    for position in range(_event_list_size):
        pending = audit_log.new_pending_event(AuditSource.REST_Channel, AuditEvent.Message_Received, Object_Name,
            cid=f'cid-{index}-{position}', msg_id=f'msg-{index}-{position}', outcome=AuditOutcome.OK,
            data=f'Order {index} from John Smith')
        out.append(pending)

    audit_log.write_pending(out)

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
    engine = get_database_engine()

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

def test_concurrent_event_lists_share_commits(audit_backend:'str') -> 'None':
    """ Concurrent callers that write several events each share commits with one another, and each event receives
    the id of its own row.
    """
    audit_log = AuditLog(Server_Name)
    engine = get_database_engine()

    # Warm up the engine so that its pool and the schema exist before the callers start
    _ = _insert(audit_log, -1)

    with record_statements(engine) as recorder:

        greenlets:'anylist' = []

        for index in range(_caller_count):
            greenlet = spawn(_write_event_list, audit_log, index)
            greenlets.append(greenlet)

        _ = joinall(greenlets, raise_error=True)

    # Each event received the id of the row with its own cid ..
    cid_by_id:'anylist' = []

    for row in read_rows(event_table):
        cid_by_id.append((row['id'], row['cid']))

    cid_by_event_id = dict(cid_by_id)

    for greenlet in greenlets:
        for pending in greenlet.value:
            assert cid_by_event_id[pending.event_id] == pending.values['cid']

    # .. and the callers shared far fewer commits than there were of them.
    assert recorder.commit_count < _caller_count // 4

# ################################################################################################################################

def test_isolated_insert_is_one_transaction(audit_backend:'str') -> 'None':
    """ A caller with no concurrent callers commits its event at once, in a transaction of its own.
    """
    audit_log = AuditLog(Server_Name)
    engine = get_database_engine()

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
        greenlet = spawn(_insert_failing, audit_log, index)
        greenlets.append(greenlet)

    _ = joinall(greenlets, raise_error=True)

    # Each caller receives an exception object of its own, caused by the exception of the commit.
    exceptions:'anylist' = []

    for greenlet in greenlets:
        exception = greenlet.value
        assert str(exception) == _error_message
        assert str(exception.__cause__) == _error_message

        for other in exceptions:
            assert exception is not other

        exceptions.append(exception)

    # The queue is not left waiting for a commit that failed.
    audit_log.is_failing = False
    event_id = _insert(audit_log, _caller_count)

    rows = read_rows(event_table)

    assert len(rows) == 1
    assert rows[0]['id'] == event_id

# ################################################################################################################################

def test_search_indexes_are_merged(audit_backend:'str') -> 'None':
    """ A process that writes events to PostgreSQL merges the event and attribute indexes, along with the indexes
    of other tables registered with the merger, and the pending lists of the audit log indexes have the same limit.
    """
    audit_log = AuditLog(Server_Name)
    _ = _insert(audit_log, 0)

    engine = get_database_engine()
    merger = get_search_index_merger(engine)

    # The indexes of the audit log come first, followed by the indexes of other tables registered with the merger.
    audit_index_count = len(_index_names)
    assert merger.index_names[:audit_index_count] == _index_names

    assert merger._thread.is_alive()

    # The pending lists can be merged ..
    merger.merge()

    # .. and all the indexes have the same limit on them.
    index_names = list(_index_names)

    with engine.connect() as connection:
        result = connection.execute(_reloptions_query, {'index_names': index_names})
        rows = result.all()

    options = dict(rows)

    expected = [f'gin_pending_list_limit={PostgreSQL_Pending_List_Limit_KB}']

    for index_name in _index_names:
        assert options[index_name] == expected, index_name

# ################################################################################################################################

def test_retention_runs_outside_the_write(audit_backend:'str', monkeypatch:'MonkeyPatch') -> 'None':
    """ The commit after the retention interval hands the retention to the thread of the runner
    and returns without running it in the write.
    """

    # No run of an earlier test is still in progress
    stop_retention_runner()

    monkeypatch.setenv(ModuleCtx.Env_Retention_Interval_Seconds, _retention_interval_seconds)
    audit_log = AuditLog(Server_Name)

    for index in range(_retention_event_count):
        _ = _insert(audit_log, index)

    # The commit after the interval started the thread of the runner ..
    thread_names:'strlist' = []

    for thread in enumerate_threads():
        thread_names.append(thread.name)

    assert _retention_thread_name in thread_names

    # .. the retention removed none of the events, none of which has expired ..
    assert len(read_rows(event_table)) == _retention_event_count

    # .. and the runner completes the run in progress before it stops.
    stop_retention_runner()

# ################################################################################################################################
# ################################################################################################################################

class TestCommitQueue:
    """ The queue on its own, with a writer that keeps the events in memory.
    """

    def test_batches_are_capped(self) -> 'None':
        writer = _QueueWriter()
        queue = CommitQueue(write_batch=writer.write_batch, max_weight=_max_events)

        greenlets:'anylist' = []
        pending_events:'anylist' = []

        for index in range(16):
            pending = _new_pending(index)
            pending_events.append(pending)

            greenlet = spawn(queue.write, pending, weight=_event_weight, is_urgent=False)
            greenlets.append(greenlet)

        _ = joinall(greenlets, raise_error=True)

        # The first caller commits alone and the others share commits of at most the maximum each ..
        assert writer.batch_sizes == [1, 5, 5, 5]

        # .. in the order they arrived, each one receiving the id of its own event.
        expected_cids:'anylist' = []

        for index in range(16):
            expected_cids.append(f'cid-{index}')

        assert writer.written_cids == expected_cids

        for index, pending in enumerate(pending_events):
            assert pending.event_id == index + 1

    def test_urgent_events_go_first_and_share_the_commit(self) -> 'None':
        writer = _QueueWriter()
        writer.release_event = Event()

        queue = CommitQueue(write_batch=writer.write_batch, max_weight=_max_events)

        # The first caller holds the commit ..
        greenlets:'anylist' = [spawn(queue.write, _new_pending(0), weight=_event_weight, is_urgent=False)]
        sleep(0)

        # .. three heavy events wait, and two urgent ones arrive after them ..
        for index in range(1, 4):
            greenlet = spawn(queue.write, _new_pending(index), weight=_heavy_event_weight, is_urgent=False)
            greenlets.append(greenlet)

        for index in range(4, 6):
            greenlet = spawn(queue.write, _new_pending(index), weight=_event_weight, is_urgent=True)
            greenlets.append(greenlet)

        sleep(0)

        # .. and once the first commit completes, the urgent events go first, in a commit that the first heavy event
        # .. shares with them up to the maximum weight, and each of the other heavy ones goes in a commit of its own,
        # .. because two of them exceed the maximum weight.
        writer.release_event.set()
        _ = joinall(greenlets, raise_error=True)

        assert writer.written_cids == ['cid-0', 'cid-4', 'cid-5', 'cid-1', 'cid-2', 'cid-3']
        assert writer.batch_sizes == [1, 3, 1, 1]

    def test_urgent_lane_does_not_wait_for_other_commits(self) -> 'None':
        writer = _QueueWriter()
        release_event = Event()
        writer.release_event = release_event

        queue = CommitQueue(write_batch=writer.write_batch, max_weight=_max_events, max_urgent_in_flight=1)

        # The first caller holds the only regular commit ..
        first = spawn(queue.write, _new_pending(0), weight=_event_weight, is_urgent=False)
        sleep(0)

        # .. another event that is not urgent waits for it ..
        waiting = spawn(queue.write, _new_pending(1), weight=_event_weight, is_urgent=False)
        sleep(0)

        # .. while an urgent event is committed at once in the reserved lane ..
        writer.release_event = None
        queue.write(_new_pending(2), weight=_event_weight, is_urgent=True)

        assert writer.written_cids == ['cid-2']

        # .. and once the first commit completes, the waiting event follows it in the regular lane.
        release_event.set()
        _ = joinall([first, waiting], raise_error=True)

        assert writer.written_cids == ['cid-2', 'cid-0', 'cid-1']
        assert writer.batch_sizes == [1, 1, 1]
        assert queue._in_flight == 0
        assert queue._urgent_in_flight == 0

    def test_lanes_take_their_own_events_first(self) -> 'None':
        writer = _QueueWriter()

        # With a reserved lane, the regular lane takes the event that is not urgent ..
        queue = CommitQueue(write_batch=writer.write_batch, max_weight=_max_events, max_urgent_in_flight=1)

        urgent = CommitTicket(_new_pending(0), _event_weight, True)
        other = CommitTicket(_new_pending(1), _event_weight, False)
        queue._waiting.extend([urgent, other])

        assert queue._take_batch(False) == [other]

        # .. and the reserved lane takes the urgent one ..
        queue._waiting.append(other)

        assert queue._take_batch(True) == [urgent]

        # .. while without a reserved lane, the regular lane takes the urgent event first and the other one
        # .. in the same commit.
        queue = CommitQueue(write_batch=writer.write_batch, max_weight=_max_events)

        queue._waiting.extend([other, urgent])

        assert queue._take_batch(False) == [urgent, other]
        assert queue._waiting == []

    def test_heavy_event_is_not_held_back_by_urgent_ones(self) -> 'None':
        writer = _QueueWriter()
        queue = CommitQueue(write_batch=writer.write_batch, max_weight=_max_events)

        # A heavy event that is not urgent waits first, and urgent ones wait behind it ..
        heavy = CommitTicket(_new_pending(0), _max_events, False)
        first_urgent = CommitTicket(_new_pending(1), _event_weight, True)
        second_urgent = CommitTicket(_new_pending(2), _event_weight, True)
        queue._waiting.extend([heavy, first_urgent, second_urgent])

        # .. the next commit takes the heavy one alone, because no urgent event fits next to it ..
        assert queue._take_batch(False) == [heavy]

        # .. and a heavy event that waits behind urgent ones is committed once it is the oldest one waiting.
        another_heavy = CommitTicket(_new_pending(3), _max_events, False)
        third_urgent = CommitTicket(_new_pending(4), _event_weight, True)
        queue._waiting.extend([another_heavy, third_urgent])

        assert queue._take_batch(False) == [first_urgent, second_urgent, third_urgent]
        assert queue._take_batch(False) == [another_heavy]
        assert queue._waiting == []

    def test_abandoned_waiter_is_not_written(self) -> 'None':
        writer = _QueueWriter()
        writer.release_event = Event()

        queue = CommitQueue(write_batch=writer.write_batch, max_weight=_max_events)

        # The first caller holds the commit ..
        first = spawn(queue.write, _new_pending(0), weight=_event_weight, is_urgent=False)
        sleep(0)

        # .. a second one stops waiting before its event is taken ..
        def write_with_timeout() -> 'Timeout':
            pending = _new_pending(1)

            # The timeout is returned rather than raised, which a greenlet would print if it ended with it
            try:
                with Timeout(_commit_time):
                    queue.write(pending, weight=_event_weight, is_urgent=False)
            except Timeout as e:
                return e

            raise Exception('Event 1 was written although its caller stopped waiting')

        abandoned = spawn(write_with_timeout)
        _ = abandoned.join()

        assert isinstance(abandoned.value, Timeout)

        # .. a third one waits ..
        third = spawn(queue.write, _new_pending(2), weight=_event_weight, is_urgent=False)
        sleep(0)

        # .. and once the first commit completes, only the third event is written after it.
        writer.release_event.set()
        _ = joinall([first, third], raise_error=True)

        assert writer.written_cids == ['cid-0', 'cid-2']
        assert writer.batch_sizes == [1, 1]

        # The queue is idle again, so a new caller commits at once.
        writer.release_event = None

        pending = _new_pending(3)
        queue.write(pending, weight=_event_weight, is_urgent=False)

        assert pending.event_id == 3
        assert writer.batch_sizes == [1, 1, 1]

    def test_abandoned_runner_passes_its_batch_on(self) -> 'None':
        writer = _QueueWriter()
        queue = CommitQueue(write_batch=writer.write_batch, max_weight=_max_events)

        first = CommitTicket(_new_pending(0), _event_weight, False)
        second = CommitTicket(_new_pending(1), _event_weight, False)

        # Two callers wait while a commit is in progress ..
        queue._in_flight = 1
        queue._waiting.extend([first, second])

        # .. the commit completes and the first of them is to run the next one ..
        queue._hand_off(False)

        assert first.batch == [first, second]
        assert first.ready.is_set()

        # .. but it stops waiting before it begins, so the second one is to commit its own event.
        queue._abandon(first)

        assert first.batch is None
        assert second.batch == [second]
        assert second.ready.is_set()
        assert queue._waiting == []
        assert queue._in_flight == 1

# ################################################################################################################################
# ################################################################################################################################
