# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The transaction of one batch of the pub/sub writer - the statements of each composition of a batch and their order,
# one transaction per batch, the rows of a batch with every kind of item, a failing item in a batch with others,
# the audit events that commit with their items and the batches that the weight of the items determines.

# stdlib
import os
from contextlib import contextmanager

# gevent
import gevent

# SQLAlchemy
from sqlalchemy import event as sa_event, select

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, get_dialect_name, get_event_rows, \
    get_message_rows, write_in_one_commit
from zato.common.audit_log.api import event_table, AuditEvent
from zato.common.audit_log.export.api import set_audit_export
from zato.common.config_db import Env_Audit_Log_Enabled
from zato.common.db_env.database import get_database_engine
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.pending import new_fenced_ack, new_pending_ack, new_pending_atomic, new_pending_attempts, \
    new_pending_lease
from zato.common.pubsub.sql.publication import add_published_event, build_publication
from zato.common.test.audit_log_ import new_test_audit_log, RecordingAuditExport

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from sqlalchemy.engine import Engine
    from zato.common.audit_log.pending import pending_event_list
    from zato.common.pubsub.sql.pending import PendingAtomic
    from zato.common.typing_ import any_, anydict, anylist, anytuple, intlist, strlist

    any_ = any_
    anydict = anydict
    anylist = anylist
    anytuple = anytuple
    Engine = Engine
    intlist = intlist
    pending_event_list = pending_event_list
    PendingAtomic = PendingAtomic
    strlist = strlist

    recordergen = Iterator['TransactionRecorder']

# ################################################################################################################################
# ################################################################################################################################

# The topics and subscribers of the scenario
_topic_main = 'pubsub.backend.test.write-transaction.main'
_topic_in   = 'pubsub.backend.test.write-transaction.input'
_topic_out  = 'pubsub.backend.test.write-transaction.output'
_topic_pub  = 'pubsub.backend.test.write-transaction.publish'

_sub_key_main = 'zpsk.test.write-transaction.main'
_sub_key_in   = 'zpsk.test.write-transaction.input'
_sub_key_out  = 'zpsk.test.write-transaction.output'
_sub_key_pub  = 'zpsk.test.write-transaction.publish'

# The identifiers of the publication and of the receipt of a batch
_pub_msg_id     = 'zpsm.test.write-transaction.publication'
_receipt_msg_id = 'zpsm.test.write-transaction.receipt'

# The payloads of the messages
_data_main    = 'Order ORD-{} for Maria Johnson'
_data_input   = 'Order ORD-0100 for John Smith'
_data_pub     = 'Invoice INV-0042 for Anna Miller'
_data_receipt = 'Receipt RCP-0100 for John Smith'

# How many messages the main subscriber has in its queue, and how many of them a lease takes at most
_main_count = 3
_lease_max_messages = 3

# How long the leases of the scenario last, and the largest total size of the messages that they take
_lease_ms = 30_000
_lease_max_len = 10_000_000

# The audit events of a batch with every kind of item - its publication, its receipt and the two messages of its lease
_every_kind_event_count = 4

# The attempt of a fenced acknowledgement that no pull handed out
_stale_attempt = 5

# The value of the switch that turns the audit log off
_audit_log_disabled = 'false'

# The largest total weight of a batch in the scenario of the weights, the number of acknowledgements written
# concurrently in it and the number of messages that each of them acknowledges
_weight_max_messages = '4'
_weight_commits_in_flight = '1'
_weight_ack_count = 5
_weight_ack_size = 2

# The statements that open and close a transaction and a savepoint
_begin     = ('BEGIN', '')
_commit    = ('COMMIT', '')
_savepoint = ('SAVEPOINT', '')
_release   = ('RELEASE', '')

# The verbs that are recorded, with the position of the table among the words of a statement or None for no table
_verb_table_position:'anydict' = {
    'INSERT': 2,
    'UPDATE': 1,
    'DELETE': 2,
    'COPY': 1,
    'BEGIN': None,
    'COMMIT': None,
    'ROLLBACK': None,
    'SAVEPOINT': None,
    'RELEASE': None,
}

# ################################################################################################################################
# ################################################################################################################################

# The statements of each part of a transaction, by verb and table, on each database
_statements_publication = [
    ('SELECT', 'pubsub_topic_sub'), ('INSERT', 'pubsub_message'), ('INSERT', 'pubsub_delivery'),
]

_statements_ack = [
    ('SELECT', 'pubsub_message'), ('SELECT', 'pubsub_delivery'), ('DELETE', 'pubsub_delivery'),
]

_statements_atomic_checks = [
    ('SELECT', 'pubsub_message'), ('SELECT', 'pubsub_delivery'),
]

_statements_atomic_writes = [
    ('SELECT', 'pubsub_topic_sub'), ('INSERT', 'pubsub_message'), ('INSERT', 'pubsub_delivery'),
    ('DELETE', 'pubsub_delivery'),
]

_statements_attempts = [
    ('UPDATE', 'pubsub_delivery'),
]

_statements_lease = [
    ('SELECT', 'pubsub_delivery'), ('UPDATE', 'pubsub_delivery'), ('SELECT', 'pubsub_message'),
]

_statements_drop = {
    'sqlite': [
        ('UPDATE', 'pubsub_message'),
    ],
    'postgresql': [
        ('SELECT', 'pubsub_message'), ('SELECT', 'pubsub_message'), ('UPDATE', 'pubsub_message'),
    ],
}

_statement_payload_select   = ('SELECT', 'event_payload')
_statement_payload_insert   = ('INSERT', 'event_payload')
_statement_event_ids_select = ('SELECT', 'generate_series')
_statement_event_insert     = ('INSERT', 'event')

# ################################################################################################################################
# ################################################################################################################################

class TransactionRecorder:
    """ The statements of an engine by verb and table, with the transactions they ran in. On SQLite, these are
    the statements that the database runs, including the ones that run in Rust, with the consecutive runs
    of one statement recorded once, and on PostgreSQL, the statements that SQLAlchemy sends, each with whether
    a transaction was open when it was sent.
    """

    def __init__(self, is_sqlite:'bool') -> 'None':
        self.is_sqlite = is_sqlite
        self.statements:'anylist' = []
        self.in_transaction:'anylist' = []
        self.begin_count = 0
        self.commit_count = 0

    def on_trace(self, statement:'str') -> 'None':
        if verb_table := get_verb_table(statement):
            if not self.statements or self.statements[-1] != verb_table:
                self.statements.append(verb_table)

    def on_checkout(self, dbapi_connection:'any_', connection_record:'any_', connection_proxy:'any_') -> 'None':
        dbapi_connection.set_trace_callback(self.on_trace)

    def on_checkin(self, dbapi_connection:'any_', connection_record:'any_') -> 'None':
        dbapi_connection.set_trace_callback(None)

    def on_execute(
        self,
        conn:'any_',
        cursor:'any_',
        statement:'str',
        parameters:'any_',
        context:'any_',
        executemany:'bool',
        ) -> 'None':
        if verb_table := get_verb_table(statement):
            self.statements.append(verb_table)
            self.in_transaction.append(conn.in_transaction())

    def on_begin(self, conn:'any_') -> 'None':
        self.begin_count += 1

    def on_commit(self, conn:'any_') -> 'None':
        self.commit_count += 1

        # SQLite runs a statement of its own for the commit, which the trace records
        if self.is_sqlite:
            return

        # .. whereas PostgreSQL commits through the driver.
        self.statements.append(_commit)
        self.in_transaction.append(True)

# ################################################################################################################################

def get_verb_table(statement:'str') -> 'anytuple | None':
    """ Returns the verb and the table of a statement, the verb alone for a statement of a transaction
    or a savepoint, and None for any other statement.
    """
    words = statement.split()
    verb = words[0]

    if verb == 'SELECT':
        if 'FROM' in words:
            from_index = words.index('FROM')
            table_name = words[from_index + 1]
        else:
            table_name = words[1]
        table_name = table_name.split('(')[0]

    elif verb in _verb_table_position:
        position = _verb_table_position[verb]
        if position is None:
            table_name = ''
        else:
            table_name = words[position]

    else:
        return None

    out = (verb, table_name)
    return out

# ################################################################################################################################

@contextmanager
def record_transactions(engine:'Engine') -> 'recordergen':
    """ Records the statements, the transactions and the commits of an engine for the duration of a block.
    """
    is_sqlite = engine.dialect.name == 'sqlite'
    recorder = TransactionRecorder(is_sqlite)

    if is_sqlite:
        sa_event.listen(engine, 'checkout', recorder.on_checkout)
        sa_event.listen(engine, 'checkin', recorder.on_checkin)
    else:
        sa_event.listen(engine, 'before_cursor_execute', recorder.on_execute)

    sa_event.listen(engine, 'begin', recorder.on_begin)
    sa_event.listen(engine, 'commit', recorder.on_commit)

    try:
        yield recorder
    finally:
        if is_sqlite:
            sa_event.remove(engine, 'checkout', recorder.on_checkout)
            sa_event.remove(engine, 'checkin', recorder.on_checkin)
        else:
            sa_event.remove(engine, 'before_cursor_execute', recorder.on_execute)

        sa_event.remove(engine, 'begin', recorder.on_begin)
        sa_event.remove(engine, 'commit', recorder.on_commit)

# ################################################################################################################################
# ################################################################################################################################

class Prepared:
    """ The state that the items of a batch refer to - the messages and delivery rows of the main subscriber
    and the message that the input subscriber pulled.
    """
    main_msg_ids: 'strlist'
    main_delivery_ids: 'intlist'
    input_msg_id: 'str'
    input_attempt: 'int'

# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend with an audit log of its own, starting from empty tables, with one subscriber of each topic.
    """
    delete_all_rows()
    delete_audit_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())

    out.subscribe(_sub_key_main, _topic_main)
    out.subscribe(_sub_key_in, _topic_in)
    out.subscribe(_sub_key_out, _topic_out)
    out.subscribe(_sub_key_pub, _topic_pub)

    return out

# ################################################################################################################################

def _prepare(backend:'SQLPubSubBackend') -> 'Prepared':
    """ Publishes the messages that the items of a batch refer to and pulls the input message.
    """
    out = Prepared()
    out.main_msg_ids = []
    out.main_delivery_ids = []

    for index in range(_main_count):
        result = backend.publish(_topic_main, _data_main.format(f'{index:04d}'))
        out.main_msg_ids.append(result.msg_id)

    for row in get_delivery_rows(_sub_key_main):
        out.main_delivery_ids.append(row.id)

    _ = backend.publish(_topic_in, _data_input)
    messages = backend.pull_messages(_sub_key_in)

    out.input_msg_id = messages[0]['msg_id']
    out.input_attempt = messages[0]['delivery_attempt']

    return out

# ################################################################################################################################

def _new_publication(backend:'SQLPubSubBackend') -> 'any_':
    """ Returns a publication of its own with the audit event that records it.
    """
    built = build_publication(backend, _topic_pub, _data_pub, msg_id=_pub_msg_id)
    add_published_event(backend, built)

    out = built.pending
    return out

# ################################################################################################################################

def _new_atomic(backend:'SQLPubSubBackend', prepared:'Prepared', attempt:'int') -> 'PendingAtomic':
    """ Returns a fenced acknowledgement of the input message with the given attempt and one receipt.
    """
    ack = new_fenced_ack(_sub_key_in, [prepared.input_msg_id], [attempt])

    built = build_publication(backend, _topic_out, _data_receipt, msg_id=_receipt_msg_id)
    add_published_event(backend, built)

    out = new_pending_atomic([built.pending], ack, True)
    return out

# ################################################################################################################################

def _new_lease(backend:'SQLPubSubBackend') -> 'any_':
    """ Returns a lease of the queue of the main subscriber.
    """
    now_ms = backend.clock.now_ms()
    leased_until_ms = now_ms + _lease_ms

    out = new_pending_lease(_sub_key_main, _lease_max_messages, _lease_max_len, now_ms, leased_until_ms, backend._on_leased)
    return out

# ################################################################################################################################

def _write(backend:'SQLPubSubBackend', items:'anylist') -> 'TransactionRecorder':
    """ Writes the items in one commit and returns what it recorded.
    """
    engine = get_database_engine()

    with record_transactions(engine) as out:
        write_in_one_commit(backend, items)

    return out

# ################################################################################################################################

def _get_expected(dialect_name:'str', parts:'anylist') -> 'anylist':
    """ Returns the statements of a transaction of the given parts, opened and committed. On SQLite, the driver opens
    the transaction before the first statement that writes, so the selects that precede it run before it.
    """
    out:'anylist' = []
    needs_begin = dialect_name == 'sqlite'

    for part in parts:
        for verb_table in part:

            # The first statement that writes opens the transaction on SQLite ..
            if needs_begin and verb_table[0] != 'SELECT':
                out.append(_begin)
                needs_begin = False

            out.append(verb_table)

    # .. and every transaction is committed.
    out.append(_commit)
    return out

# ################################################################################################################################

def _get_atomic_statements(dialect_name:'str') -> 'anylist':
    """ Returns the statements of a fenced acknowledgement with one receipt, which PostgreSQL writes in a savepoint.
    """
    out:'anylist' = []

    if dialect_name == 'postgresql':
        out.append(_savepoint)

    out.extend(_statements_atomic_checks)
    out.extend(_statements_atomic_writes)

    if dialect_name == 'postgresql':
        out.append(_release)

    return out

# ################################################################################################################################

def _get_event_statements(dialect_name:'str', event_count:'int', has_new_payloads:'bool') -> 'anylist':
    """ Returns the statements of the audit events of a batch. PostgreSQL reserves the ids of more than one event
    from its sequence, and a payload stored already by an earlier event is not inserted again.
    """
    out:'anylist' = [_statement_payload_select]

    if dialect_name == 'postgresql' and event_count > 1:
        out.append(_statement_event_ids_select)

    if has_new_payloads:
        out.append(_statement_payload_insert)

    out.append(_statement_event_insert)
    return out

# ################################################################################################################################

def _assert_one_transaction(recorder:'TransactionRecorder', expected:'anylist') -> 'None':
    """ The batch ran the expected statements in one transaction, which it opened and committed once.
    """
    assert recorder.statements == expected, recorder.statements
    assert recorder.begin_count == 1, recorder.begin_count
    assert recorder.commit_count == 1, recorder.commit_count

    for is_open in recorder.in_transaction:
        assert is_open

# ################################################################################################################################
# ################################################################################################################################

def _run_compositions() -> 'None':
    """ Each kind of item alone in a batch runs its own statements, in one transaction.
    """
    dialect_name = get_dialect_name()
    publication = _statements_publication
    drop = _statements_drop[dialect_name]
    one_event = _get_event_statements(dialect_name, 1, True)

    # A publication with its audit event ..
    backend = _new_backend()
    recorder = _write(backend, [_new_publication(backend)])

    _assert_one_transaction(recorder, _get_expected(dialect_name, [publication, one_event]))

    # .. an acknowledgement, which drops the payload of the message that it fully delivered ..
    backend = _new_backend()
    prepared = _prepare(backend)

    ack = new_pending_ack(_sub_key_main, [prepared.main_msg_ids[0]], None)
    recorder = _write(backend, [ack])

    _assert_one_transaction(recorder, _get_expected(dialect_name, [_statements_ack, drop]))

    # .. a fenced acknowledgement with its receipt ..
    backend = _new_backend()
    prepared = _prepare(backend)

    atomic = _new_atomic(backend, prepared, prepared.input_attempt)
    recorder = _write(backend, [atomic])

    parts = [_get_atomic_statements(dialect_name), drop, one_event]
    _assert_one_transaction(recorder, _get_expected(dialect_name, parts))

    # .. the push attempts of two deliveries ..
    backend = _new_backend()
    prepared = _prepare(backend)

    attempts = new_pending_attempts(prepared.main_delivery_ids[:2])
    recorder = _write(backend, [attempts])

    _assert_one_transaction(recorder, _get_expected(dialect_name, [_statements_attempts]))

    # .. and a lease with the audit events of the messages that it hands out, whose payloads their publications stored.
    backend = _new_backend()
    _ = _prepare(backend)

    recorder = _write(backend, [_new_lease(backend)])

    parts = [_statements_lease, _get_event_statements(dialect_name, _main_count, False)]
    _assert_one_transaction(recorder, _get_expected(dialect_name, parts))

# ################################################################################################################################

def _get_payload(topic_name:'str', msg_id:'str') -> 'any_':
    """ Returns the payload column of the message row of one message identifier.
    """
    for row in get_message_rows(topic_name):
        if row.msg_id == msg_id:
            out = row.payload
            break
    else:
        raise Exception(f'No message row for {msg_id}')

    return out

# ################################################################################################################################

def _get_msg_ids(messages:'anylist') -> 'strlist':
    """ Returns the message identifiers of the messages that a lease handed out.
    """
    out:'strlist' = []

    for message in messages:
        out.append(message['msg_id'])

    return out

# ################################################################################################################################

def _run_every_kind() -> 'None':
    """ A batch with an item of every kind writes them in the order of the kinds, whatever the order of the items,
    and each item sees what the items written before it did.
    """
    dialect_name = get_dialect_name()

    backend = _new_backend()
    prepared = _prepare(backend)

    main_msg_ids = prepared.main_msg_ids
    main_delivery_ids = prepared.main_delivery_ids

    publication = _new_publication(backend)
    ack = new_pending_ack(_sub_key_main, [main_msg_ids[0]], None)
    atomic = _new_atomic(backend, prepared, prepared.input_attempt)
    attempts = new_pending_attempts(main_delivery_ids[:2])
    lease = _new_lease(backend)

    # The items are given in the reverse order of the kinds ..
    recorder = _write(backend, [lease, attempts, atomic, ack, publication])

    # .. and their statements run in the order of the kinds, with the payloads dropped after every write of delivery rows ..
    parts = [
        _statements_publication,
        _statements_ack,
        _get_atomic_statements(dialect_name),
        _statements_attempts,
        _statements_lease,
        _statements_drop[dialect_name],
        _get_event_statements(dialect_name, _every_kind_event_count, True),
    ]

    _assert_one_transaction(recorder, _get_expected(dialect_name, parts))

    # .. the publication stored its message with one delivery row ..
    assert publication.exception is None
    assert not publication.is_repeat
    assert publication.subscriber_keys == [_sub_key_pub], publication.subscriber_keys
    assert len(get_delivery_rows(_sub_key_pub)) == 1

    # .. the acknowledgement removed its row and the payload of its message, which no other subscriber needs ..
    assert ack.removed_count == 1
    assert ack.fully_delivered_count == 1
    assert _get_payload(_topic_main, main_msg_ids[0]) is None

    # .. the fenced acknowledgement removed the input row and the payload, and published its receipt ..
    assert atomic.exception is None
    assert get_delivery_rows(_sub_key_in) == []
    assert _get_payload(_topic_in, prepared.input_msg_id) is None
    assert _get_payload(_topic_out, _receipt_msg_id) == _data_receipt
    assert len(get_delivery_rows(_sub_key_out)) == 1

    # .. the attempts were recorded for the delivery that the batch did not acknowledge alone ..
    assert attempts.attempts == {main_delivery_ids[1]: 1}, attempts.attempts

    # .. and the lease took the messages that the batch did not acknowledge, the first one after its attempt.
    assert _get_msg_ids(lease.messages) == main_msg_ids[1:], lease.messages

    lease_columns:'anylist' = []

    for row in get_delivery_rows(_sub_key_main):
        lease_columns.append((row.id, row.attempt, row.leased_until_ms))

    expected_columns = [
        (main_delivery_ids[1], 2, lease.leased_until_ms),
        (main_delivery_ids[2], 1, lease.leased_until_ms),
    ]

    assert lease_columns == expected_columns, lease_columns

# ################################################################################################################################

def _run_failing_item() -> 'None':
    """ A fenced acknowledgement that fails its checks writes nothing and fails its own caller alone,
    while the other items of its batch commit with their audit events.
    """
    backend = _new_backend()
    prepared = _prepare(backend)

    input_rows = get_delivery_rows(_sub_key_in)

    publication = _new_publication(backend)
    ack = new_pending_ack(_sub_key_main, [prepared.main_msg_ids[0]], None)
    atomic = _new_atomic(backend, prepared, _stale_attempt)
    lease = _new_lease(backend)

    _ = _write(backend, [publication, ack, atomic, lease])

    # The fenced acknowledgement failed and wrote neither its acknowledgement nor its receipt ..
    assert isinstance(atomic.exception, PubSubAckConflict), atomic.exception
    assert get_delivery_rows(_sub_key_in) == input_rows
    assert get_message_rows(_topic_out) == []
    assert get_event_rows(_topic_out, AuditEvent.Published) == []

    # .. while the other items committed with their events.
    assert publication.exception is None
    assert ack.exception is None
    assert lease.exception is None

    assert ack.removed_count == 1
    assert _get_msg_ids(lease.messages) == prepared.main_msg_ids[1:], lease.messages

    assert len(get_event_rows(_topic_pub, AuditEvent.Published)) == 1
    assert len(get_event_rows(_topic_main, AuditEvent.Received)) == 2

# ################################################################################################################################
# ################################################################################################################################

class VisibilityExport(RecordingAuditExport):
    """ An export that records, for each batch handed to it, whether every event of the batch is visible
    to another connection at that moment.
    """
    def __init__(self) -> 'None':
        super().__init__()
        self.visible:'anylist' = []

    def emit_batch(self, batch:'pending_event_list') -> 'None':
        event_ids:'intlist' = []

        for pending in batch:
            event_ids.append(pending.event_id)

        engine = get_database_engine()
        query = select(event_table.c.id).where(event_table.c.id.in_(event_ids))

        with engine.connect() as connection:
            visible_ids = connection.execute(query).scalars().all()

        self.visible.append(sorted(visible_ids) == sorted(event_ids))
        super().emit_batch(batch)

# ################################################################################################################################

def _run_events_commit_with_items() -> 'None':
    """ The audit events of a batch are handed to the export with their ids once they are committed,
    and a batch committed while the audit log is off writes its items without their events.
    """
    backend = _new_backend()
    _ = _prepare(backend)

    publication = _new_publication(backend)
    lease = _new_lease(backend)

    export = VisibilityExport()
    set_audit_export(export)

    try:
        _ = _write(backend, [publication, lease])
    finally:
        set_audit_export(None)

    # The export received one batch, after its commit, with the id of each event of the batch ..
    assert export.visible == [True], export.visible

    exported_ids:'intlist' = []

    for exported in export.events:
        exported_ids.append(exported.event_id)

    committed_ids:'intlist' = []

    for event in get_event_rows(_topic_pub, AuditEvent.Published) + get_event_rows(_topic_main, AuditEvent.Received):
        committed_ids.append(event['id'])

    assert sorted(exported_ids) == sorted(committed_ids), (exported_ids, committed_ids)
    assert len(committed_ids) == 1 + _main_count

    # .. whereas the audit log turned off before a commit leaves the items of the batch without their events.
    backend = _new_backend()
    _ = _prepare(backend)

    publication = _new_publication(backend)
    lease = _new_lease(backend)

    os.environ[Env_Audit_Log_Enabled] = _audit_log_disabled

    try:
        _ = _write(backend, [publication, lease])
    finally:
        del os.environ[Env_Audit_Log_Enabled]

    assert len(get_message_rows(_topic_pub)) == 1
    assert len(lease.messages) == _main_count

    assert get_event_rows(_topic_pub, AuditEvent.Published) == []
    assert get_event_rows(_topic_main, AuditEvent.Received) == []

# ################################################################################################################################

def _run_weights() -> 'None':
    """ Items written concurrently whose weights exceed the largest weight of a batch are committed in several batches,
    each a transaction of its own.
    """
    os.environ[ModuleCtx.Env_Commit_Max_Messages] = _weight_max_messages
    os.environ[ModuleCtx.Env_Commits_In_Flight] = _weight_commits_in_flight

    try:
        backend = _new_backend()
    finally:
        del os.environ[ModuleCtx.Env_Commit_Max_Messages]
        del os.environ[ModuleCtx.Env_Commits_In_Flight]

    msg_ids:'strlist' = []

    for index in range(_weight_ack_count * _weight_ack_size):
        result = backend.publish(_topic_main, _data_main.format(f'{index:04d}'))
        msg_ids.append(result.msg_id)

    acks:'anylist' = []

    for index in range(_weight_ack_count):
        start = index * _weight_ack_size
        ack = new_pending_ack(_sub_key_main, msg_ids[start:start + _weight_ack_size], None)
        acks.append(ack)

    # The first acknowledgement commits alone, and the others wait for it and are taken two by two ..
    engine = get_database_engine()

    with record_transactions(engine) as recorder:
        greenlets:'anylist' = []

        for ack in acks:
            greenlet = gevent.spawn(backend._writer.ack, ack)
            greenlets.append(greenlet)

        _ = gevent.joinall(greenlets, raise_error=True)

    assert recorder.commit_count == 3, recorder.commit_count
    assert recorder.begin_count == 3, recorder.begin_count

    # .. and each acknowledgement removed its own rows and the payloads of its messages.
    for ack in acks:
        assert ack.removed_count == _weight_ack_size
        assert ack.fully_delivered_count == _weight_ack_size

    assert get_delivery_rows(_sub_key_main) == []

    for msg_id in msg_ids:
        assert _get_payload(_topic_main, msg_id) is None

# ################################################################################################################################

def run_write_transaction_scenario() -> 'None':
    """ The transaction of one batch of the pub/sub writer, each part starting from empty tables.
    """
    _run_compositions()
    _run_every_kind()
    _run_failing_item()
    _run_events_commit_with_items()
    _run_weights()

# ################################################################################################################################
# ################################################################################################################################
