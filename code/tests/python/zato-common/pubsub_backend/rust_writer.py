# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The Rust write path of pub/sub on SQLite - a connection without an open transaction, the ownership of the handle
# of the driver's connection, the threads of the pool writing while greenlets hold the GIL, and the release of the GIL
# for the whole transaction of a batch.

# stdlib
from time import perf_counter

# gevent
import gevent
from gevent.monkey import get_original

# pytest
import pytest

# Zato
from common import delete_all_rows, get_delivery_rows, get_message_rows, write_in_one_commit
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.publication import build_publication
from zato.common.pubsub.sql.sqlite_write import write_items_sqlite
from zato.common.pubsub.sql.writes import PubSubWriter
from zato.common.test.audit_log_ import new_test_audit_log

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import anylist, floatlist, strlist
    from zato_common_core.zato_common_core import SubscriptionList

    anylist = anylist
    AuditLog = AuditLog
    Engine = Engine
    floatlist = floatlist
    strlist = strlist
    SubscriptionList = SubscriptionList

# ################################################################################################################################
# ################################################################################################################################

# The thread functions of the interpreter itself, which gevent replaces with greenlets
_start_new_thread = get_original('_thread', 'start_new_thread')
_allocate_lock = get_original('_thread', 'allocate_lock')
_native_sleep = get_original('time', 'sleep')

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The topic of the scenario and its two subscribers
    Topic_Name = 'pubsub.backend.test.rust-writer'
    Sub_Key_1 = 'zpsk.test.rust-writer.1'
    Sub_Key_2 = 'zpsk.test.rust-writer.2'

    # The payload of a regular message
    Payload = 'Order ORD-0042 for Maria Johnson'

    # How many rounds of publications, pulls and acknowledgements the handle goes through, and how many messages each has
    Ownership_Rounds = 40
    Ownership_Round_Size = 20

    # How many messages are published before the concurrent writes, and how many during them
    Backlog_Count = 100
    Concurrent_Count = 200

    # How many greenlets hold the GIL during the concurrent writes, and how much work each does between its switches
    GIL_Holder_Count = 4
    GIL_Holder_Work = 20_000

    # The line that a large payload repeats, how many times, and how many large messages one batch has
    Large_Line = 'Invoice line for Maria Johnson 42.50 USD\n'
    Large_Repeat = 100_000
    Large_Count = 24

    # How long the counting thread sleeps between its samples, in seconds
    Counter_Interval = 0.0005

    # The share of the transaction that the longest pause of the counting thread may take at most
    Max_Gap_Share = 0.25

    # The result of an integrity check of a database without defects
    Integrity_OK = 'ok'

# ################################################################################################################################
# ################################################################################################################################

class _TimedWriter(PubSubWriter):
    """ A writer that records when each of its transactions started and ended.
    """
    def __init__(self, audit_log:'AuditLog', subscription_list:'SubscriptionList') -> 'None':
        super().__init__(audit_log, subscription_list)
        self.windows:'anylist' = []

    def _write_transaction(self, engine:'Engine', batch:'anylist') -> 'anylist':
        start = perf_counter()
        out = super()._write_transaction(engine, batch)
        self.windows.append((start, perf_counter()))
        return out

# ################################################################################################################################
# ################################################################################################################################

class _Counter:
    """ A thread of the interpreter that records the time of each of its samples while it runs.
    """
    def __init__(self) -> 'None':
        self.samples:'floatlist' = []
        self.is_running = True
        self.done = _allocate_lock()

    def run(self) -> 'None':
        while self.is_running:
            self.samples.append(perf_counter())
            _native_sleep(ModuleCtx.Counter_Interval)
        self.done.release()

    def start(self) -> 'None':
        _ = self.done.acquire()
        _ = _start_new_thread(self.run, ())

    def stop(self) -> 'None':
        self.is_running = False
        _ = self.done.acquire()

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'tuple[SQLPubSubBackend, _TimedWriter]':
    """ Returns a backend whose transactions are timed, with both subscribers subscribed to the topic of the scenario.
    """
    delete_all_rows()

    audit_log = new_test_audit_log()
    backend = SQLPubSubBackend(audit_log=audit_log)

    writer = _TimedWriter(audit_log, backend.subscription_list)
    backend._writer = writer

    backend.subscribe(ModuleCtx.Sub_Key_1, ModuleCtx.Topic_Name)
    backend.subscribe(ModuleCtx.Sub_Key_2, ModuleCtx.Topic_Name)

    out = backend, writer
    return out

# ################################################################################################################################

def _publish_many(backend:'SQLPubSubBackend', count:'int') -> 'strlist':
    """ Publishes messages from concurrent greenlets and returns their identifiers.
    """
    greenlets:'anylist' = []

    for _ in range(count):
        greenlet = gevent.spawn(backend.publish, ModuleCtx.Topic_Name, ModuleCtx.Payload)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    out:'strlist' = []

    for greenlet in greenlets:
        out.append(greenlet.value.msg_id)

    return out

# ################################################################################################################################

def _get_integrity() -> 'str':
    """ Returns the result of the integrity check of the database.
    """
    engine = get_database_engine()

    with engine.connect() as connection:
        out = connection.exec_driver_sql('PRAGMA integrity_check').scalar_one()

    return out

# ################################################################################################################################

def _hold_gil(rounds:'int') -> 'None':
    """ Runs Python code that holds the GIL, switching to the other greenlets between its rounds.
    """
    total = 0

    for _ in range(rounds):
        for value in range(ModuleCtx.GIL_Holder_Work):
            total += value
        gevent.sleep(0)

# ################################################################################################################################
# ################################################################################################################################

def _run_no_transaction_flow() -> 'None':
    """ A connection without an open transaction is refused, and nothing of the batch is written.
    """
    backend, _ = _new_backend()

    built = build_publication(backend, ModuleCtx.Topic_Name, ModuleCtx.Payload)
    engine = get_database_engine()

    with engine.connect() as connection:
        with pytest.raises(Exception, match='The connection has no open transaction'):
            _ = write_items_sqlite(connection, [built.pending], [], [], [], [], backend.subscription_list)

    assert get_message_rows(ModuleCtx.Topic_Name) == []

# ################################################################################################################################

def _run_ownership_flow() -> 'None':
    """ After many batches through the handle of the pooled connections, the pool closes each connection normally
    and the database has no defects.
    """
    backend, writer = _new_backend()

    for _ in range(ModuleCtx.Ownership_Rounds):

        msg_ids = _publish_many(backend, ModuleCtx.Ownership_Round_Size)

        for sub_key in (ModuleCtx.Sub_Key_1, ModuleCtx.Sub_Key_2):
            messages = backend.pull_messages(sub_key, max_messages=ModuleCtx.Ownership_Round_Size)
            assert len(messages) == ModuleCtx.Ownership_Round_Size
            _ = backend.ack_messages(sub_key, msg_ids)

    # Each round committed its publications, its pulls and its acknowledgements ..
    assert len(writer.windows) >= ModuleCtx.Ownership_Rounds * 3

    # .. every message is fully delivered ..
    assert get_delivery_rows(ModuleCtx.Sub_Key_1) == []
    assert get_delivery_rows(ModuleCtx.Sub_Key_2) == []

    message_rows = get_message_rows(ModuleCtx.Topic_Name)
    assert len(message_rows) == ModuleCtx.Ownership_Rounds * ModuleCtx.Ownership_Round_Size

    for row in message_rows:
        assert row.payload is None

    # .. the pool closes every connection, whose handle the writer never closed ..
    get_database_engine().dispose()

    # .. and the database is intact.
    assert _get_integrity() == ModuleCtx.Integrity_OK

# ################################################################################################################################

def _run_concurrent_flow() -> 'None':
    """ The publications and the acknowledgements commit in their own lanes, each in a thread of the pool on its own
    connection, while greenlets hold the GIL, and every row of every batch is in the database afterwards.
    """
    backend, _ = _new_backend()

    backlog = _publish_many(backend, ModuleCtx.Backlog_Count)

    greenlets:'anylist' = []

    for _ in range(ModuleCtx.GIL_Holder_Count):
        greenlets.append(gevent.spawn(_hold_gil, ModuleCtx.Concurrent_Count))

    publisher = gevent.spawn(_publish_many, backend, ModuleCtx.Concurrent_Count)
    acker = gevent.spawn(backend.ack_messages, ModuleCtx.Sub_Key_1, backlog)
    greenlets.append(publisher)
    greenlets.append(acker)

    _ = gevent.joinall(greenlets, raise_error=True)

    total = ModuleCtx.Backlog_Count + ModuleCtx.Concurrent_Count

    # The backlog was acknowledged by the first subscriber alone, which keeps the payloads ..
    assert acker.value == 0

    # .. so every message remains, the first subscriber has the new ones and the second one has all of them ..
    message_rows = get_message_rows(ModuleCtx.Topic_Name)
    assert len(message_rows) == total

    for row in message_rows:
        assert row.payload == ModuleCtx.Payload

    assert len(get_delivery_rows(ModuleCtx.Sub_Key_1)) == ModuleCtx.Concurrent_Count
    assert len(get_delivery_rows(ModuleCtx.Sub_Key_2)) == total

    # .. and the database is intact.
    assert _get_integrity() == ModuleCtx.Integrity_OK

# ################################################################################################################################

def _run_gil_release_flow() -> 'None':
    """ A thread that counts while a batch with large payloads is written advances throughout the transaction,
    so no statement of the transaction holds the GIL.
    """
    backend, writer = _new_backend()

    payload = ModuleCtx.Large_Line * ModuleCtx.Large_Repeat
    items:'anylist' = []

    for _ in range(ModuleCtx.Large_Count):
        built = build_publication(backend, ModuleCtx.Topic_Name, payload)
        items.append(built.pending)

    counter = _Counter()
    counter.start()

    try:
        write_in_one_commit(backend, items)
    finally:
        counter.stop()

    start, end = writer.windows[-1]
    window = end - start

    # The points in time at which the counting thread ran within the transaction ..
    points:'floatlist' = [start]

    for sample in counter.samples:
        if start < sample < end:
            points.append(sample)

    points.append(end)

    # .. are never further apart than a small share of it.
    max_gap = 0.0

    for previous, current in zip(points, points[1:]):
        max_gap = max(max_gap, current - previous)

    assert max_gap <= window * ModuleCtx.Max_Gap_Share, f'{max_gap:.4f}s of {window:.4f}s'

    # The batch itself was written in full.
    message_rows = get_message_rows(ModuleCtx.Topic_Name)
    assert len(message_rows) == ModuleCtx.Large_Count

    for row in message_rows:
        assert row.payload == payload

# ################################################################################################################################
# ################################################################################################################################

def run_rust_writer_scenario() -> 'None':
    """ Runs the flows of the Rust write path of pub/sub on SQLite.
    """
    _run_no_transaction_flow()
    _run_ownership_flow()
    _run_concurrent_flow()
    _run_gil_release_flow()

# ################################################################################################################################
# ################################################################################################################################
