# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The failures of one item of a batch of the pub/sub writer on SQLite, each of which fails the caller of the item alone -
# a strict fenced acknowledgement whose receipt reuses the message ID of a different stored message, a message with
# the same ID that another process publishes while a fenced acknowledgement is checked, and a value that SQLite rejects.

# stdlib
import os
import sqlite3
import sys
from contextlib import contextmanager
from logging import getLogger, Handler, INFO
from subprocess import PIPE, Popen
from time import monotonic

# gevent
from gevent.monkey import get_original

# SQLAlchemy
from sqlalchemy import event as sa_event
from sqlalchemy.exc import DBAPIError

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, get_message_rows, write_in_one_commit
from concurrent_publisher import ModuleCtx as PublisherCtx
from transaction_statements import get_verb_table
from zato.common.db_env.database import get_database_engine
from zato.common.db_env.errors import is_value_error
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.pubsub.sql.pending import new_fenced_ack, new_pending_ack, new_pending_atomic, new_pending_attempts, \
    new_pending_lease
from zato.common.pubsub.sql.publication import build_publication
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from logging import LogRecord
    from sqlalchemy.engine import Engine
    from zato.common.pubsub.sql.pending import PendingAtomic, PendingAttempts, PendingLease
    from zato.common.typing_ import any_, anydict, anylist, floatnone, strdict, strlist, strnone

    any_ = any_
    anydict = anydict
    anylist = anylist
    Engine = Engine
    floatnone = floatnone
    LogRecord = LogRecord
    PendingAtomic = PendingAtomic
    PendingAttempts = PendingAttempts
    PendingLease = PendingLease
    strdict = strdict
    strlist = strlist
    strnone = strnone

    nonegen    = Iterator[None]
    handlergen = Iterator['SplitRecords']

# ################################################################################################################################
# ################################################################################################################################

# The topics and subscribers of the scenarios
_topic_orders   = 'pubsub.backend.test.false-conflicts.orders'
_topic_input    = 'pubsub.backend.test.false-conflicts.input'
_topic_receipts = 'pubsub.backend.test.false-conflicts.receipts'

_sub_key_orders   = 'zpsk.test.false-conflicts.orders'
_sub_key_input    = 'zpsk.test.false-conflicts.input'
_sub_key_receipts = 'zpsk.test.false-conflicts.receipts'

# The message ID of a receipt that a stored message has already, and that of a receipt that no stored message has
_taken_msg_id = 'zpsm.test.false-conflicts.taken'
_free_msg_id  = 'zpsm.test.false-conflicts.free'

# The payloads of the messages
_data_order         = 'Order ORD-{} for Maria Johnson'
_data_input         = 'Order ORD-{} for John Smith'
_data_receipt       = 'Receipt RCP-0100 for John Smith'
_data_receipt_other = 'Receipt RCP-0200 for Anna Miller'

# How many messages the orders subscriber has in its queue before a batch
_order_count = 2

# How many messages a lease takes at most, how long it lasts and the largest total size of the messages that it takes
_lease_max_messages = 10
_lease_ms = 30_000
_lease_max_len = 10_000_000

# The largest string or blob that SQLite accepts in the scenario of a rejected value, and a payload longer than that
_value_length_limit = 65_536
_data_too_long = 'Order ORD-0500 for Jane Doe. ' * 5000

# How long a fenced acknowledgement waits for the publication of the other process after it signaled the process
_concurrent_wait_seconds = 2.0

# The statement that reads the delivery rows of a fenced acknowledgement once its publications are checked
_select_fenced_delivery = ('SELECT', 'pubsub_delivery')

# The logger of the pub/sub writer and the beginning of its message about a batch that is written item by item
_writer_logger_name   = 'zato.common.pubsub.sql.writes'
_split_message_prefix = 'Pub/sub commit split'

# The script of the other process, and how much of its output is read at a time
_publisher_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concurrent_publisher.py')
_read_size = 4096

# The select of the standard library, which blocks the thread of the pool that runs a database call
_select = get_original('select', 'select')

# ################################################################################################################################
# ################################################################################################################################

class ConcurrentPublisher:
    """ A process of its own that publishes one message when a fenced acknowledgement of a batch reads its delivery rows,
    and the outcome of the publication.
    """
    def __init__(self, topic_name:'str', data:'str', msg_id:'str') -> 'None':
        command = [sys.executable, '-m', 'gevent.monkey', _publisher_path, topic_name, data, msg_id]

        self.process = Popen(command, stdin=PIPE, stdout=PIPE)
        self.stdin_fd = cast_('any_', self.process.stdin).fileno()
        self.stdout_fd = cast_('any_', self.process.stdout).fileno()

        self.buffer = b''
        self.is_signaled = False
        self.outcome_during_batch:'strnone' = None

        # The publisher is signaled only once its backend is ready
        ready = self._read_line(None)

        if ready != PublisherCtx.Ready:
            raise Exception(f'Concurrent publisher not ready -> `{ready}`')

    def _read_line(self, timeout:'floatnone') -> 'strnone':
        """ Returns the next line of the publisher, or None if none arrived before the timeout.
        """
        if timeout is None:
            deadline = None
        else:
            deadline = monotonic() + timeout

        while True:

            # A complete line is returned if the publisher wrote it, and other output is skipped ..
            if b'\n' in self.buffer:
                line, self.buffer = self.buffer.split(b'\n', 1)
                line = line.decode('utf8')

                if line.startswith(PublisherCtx.Line_Prefix):
                    out = line.removeprefix(PublisherCtx.Line_Prefix)
                    break

                continue

            # .. otherwise more output is waited for, until the deadline if there is one ..
            if deadline is None:
                remaining = None
            else:
                remaining = deadline - monotonic()

                if remaining <= 0:
                    out = None
                    break

            readable, _, _ = _select([self.stdout_fd], [], [], remaining)

            if not readable:
                out = None
                break

            # .. and the output of a process that exited ends the scenario.
            chunk = os.read(self.stdout_fd, _read_size)

            if not chunk:
                raise Exception('Concurrent publisher exited without its outcome')

            self.buffer += chunk

        return out

    def _on_trace(self, statement:'str') -> 'None':
        """ Signals the publication at the first read of the delivery rows of a fenced acknowledgement
        and waits for its outcome for a limited time.
        """
        if self.is_signaled:
            return

        verb_table = get_verb_table(statement)

        if verb_table != _select_fenced_delivery:
            return

        self.is_signaled = True
        _ = os.write(self.stdin_fd, b'\n')

        self.outcome_during_batch = self._read_line(_concurrent_wait_seconds)

    def _on_checkout(self, dbapi_connection:'any_', connection_record:'any_', connection_proxy:'any_') -> 'None':
        dbapi_connection.set_trace_callback(self._on_trace)

    def _on_checkin(self, dbapi_connection:'any_', connection_record:'any_') -> 'None':
        dbapi_connection.set_trace_callback(None)

    @contextmanager
    def signal_on_fenced_select(self, engine:'Engine') -> 'nonegen':
        """ Signals the publication from within the batch that the block writes.
        """
        sa_event.listen(engine, 'checkout', self._on_checkout)
        sa_event.listen(engine, 'checkin', self._on_checkin)

        try:
            yield
        finally:
            sa_event.remove(engine, 'checkout', self._on_checkout)
            sa_event.remove(engine, 'checkin', self._on_checkin)

    def get_outcome(self) -> 'str':
        """ Returns the outcome of the publication, waiting for it if it did not arrive within the batch.
        """
        if self.outcome_during_batch is None:
            out = self._read_line(None)
        else:
            out = self.outcome_during_batch

        out = cast_('str', out)
        return out

    def stop(self) -> 'None':
        """ Ends the process and closes its pipes.
        """
        if self.process.poll() is None:
            self.process.kill()

        _ = self.process.wait()

        cast_('any_', self.process.stdin).close()
        cast_('any_', self.process.stdout).close()

# ################################################################################################################################

class LengthLimit:
    """ The largest string or blob that SQLite accepts on each connection checked out for the duration of a block.
    """
    def __init__(self, limit:'int') -> 'None':
        self.limit = limit
        self.previous:'anydict' = {}

    def _on_checkout(self, dbapi_connection:'any_', connection_record:'any_', connection_proxy:'any_') -> 'None':
        previous = dbapi_connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, self.limit)
        self.previous[id(dbapi_connection)] = previous

    def _on_checkin(self, dbapi_connection:'any_', connection_record:'any_') -> 'None':
        if previous := self.previous.pop(id(dbapi_connection), None):
            _ = dbapi_connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, previous)

    @contextmanager
    def applied(self, engine:'Engine') -> 'nonegen':
        """ Applies the limit within the block.
        """
        sa_event.listen(engine, 'checkout', self._on_checkout)
        sa_event.listen(engine, 'checkin', self._on_checkin)

        try:
            yield
        finally:
            sa_event.remove(engine, 'checkout', self._on_checkout)
            sa_event.remove(engine, 'checkin', self._on_checkin)

# ################################################################################################################################

class SplitRecords(Handler):
    """ The messages of the pub/sub writer about batches that it wrote item by item.
    """
    def __init__(self) -> 'None':
        super().__init__()
        self.messages:'strlist' = []

    def emit(self, record:'LogRecord') -> 'None':
        message = record.getMessage()

        if message.startswith(_split_message_prefix):
            self.messages.append(message)

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _recording_splits() -> 'handlergen':
    """ Records the messages of the pub/sub writer about batches written item by item, for the duration of a block.
    """
    writer_logger = getLogger(_writer_logger_name)
    previous_level = writer_logger.level

    handler = SplitRecords()

    writer_logger.addHandler(handler)
    writer_logger.setLevel(INFO)

    try:
        yield handler
    finally:
        writer_logger.removeHandler(handler)
        writer_logger.setLevel(previous_level)

# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend with an audit log of its own, starting from empty tables, with one subscriber of each topic.
    """
    delete_all_rows()
    delete_audit_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())

    out.subscribe(_sub_key_orders, _topic_orders)
    out.subscribe(_sub_key_input, _topic_input)
    out.subscribe(_sub_key_receipts, _topic_receipts)

    return out

# ################################################################################################################################

def _publish_orders(backend:'SQLPubSubBackend') -> 'strlist':
    """ Publishes the messages of the queue of the orders subscriber and returns their message IDs.
    """
    out:'strlist' = []

    for index in range(_order_count):
        data = _data_order.format(f'{index:04d}')
        result = backend.publish(_topic_orders, data)
        out.append(result.msg_id)

    return out

# ################################################################################################################################

def _pull_inputs(backend:'SQLPubSubBackend', count:'int') -> 'anylist':
    """ Publishes the given number of input messages and returns them as the input subscriber pulled them.
    """
    for index in range(count):
        data = _data_input.format(f'{index:04d}')
        _ = backend.publish(_topic_input, data)

    out = backend.pull_messages(_sub_key_input)
    return out

# ################################################################################################################################

def _new_atomic(backend:'SQLPubSubBackend', message:'anydict', receipt_msg_id:'str', data:'str') -> 'PendingAtomic':
    """ Returns a strict fenced acknowledgement of a pulled input message with one receipt.
    """
    msg_id = message['msg_id']
    attempt = message['delivery_attempt']

    ack = new_fenced_ack(_sub_key_input, [msg_id], [attempt])
    built = build_publication(backend, _topic_receipts, data, msg_id=receipt_msg_id)

    out = new_pending_atomic([built.pending], ack, True)
    return out

# ################################################################################################################################

def _new_attempts() -> 'PendingAttempts':
    """ Returns the push attempts of every delivery of the orders subscriber.
    """
    delivery_ids:'anylist' = []

    for row in get_delivery_rows(_sub_key_orders):
        delivery_ids.append(row.id)

    out = new_pending_attempts(delivery_ids)
    return out

# ################################################################################################################################

def _new_lease(backend:'SQLPubSubBackend') -> 'PendingLease':
    """ Returns a lease of the queue of the orders subscriber.
    """
    now_ms = backend.clock.now_ms()
    leased_until_ms = now_ms + _lease_ms

    out = new_pending_lease(_sub_key_orders, _lease_max_messages, _lease_max_len, now_ms, leased_until_ms, backend._on_leased)
    return out

# ################################################################################################################################

def _get_payloads(topic_name:'str') -> 'strdict':
    """ Returns the payload of each stored message of a topic by its message ID.
    """
    out:'strdict' = {}

    for row in get_message_rows(topic_name):
        out[row.msg_id] = row.payload

    return out

# ################################################################################################################################

def _get_leased_msg_ids(lease:'PendingLease') -> 'strlist':
    """ Returns the message IDs of the messages that a lease handed out.
    """
    out:'strlist' = []

    for message in lease.messages:
        out.append(message['msg_id'])

    return out

# ################################################################################################################################

def _assert_orders_leased(lease:'PendingLease', order_msg_ids:'strlist') -> 'None':
    """ Confirms that a lease committed and handed out each message of the queue of the orders subscriber.
    """
    assert lease.exception is None, lease.exception

    leased_msg_ids = _get_leased_msg_ids(lease)

    for msg_id in order_msg_ids:
        assert msg_id in leased_msg_ids, leased_msg_ids

# ################################################################################################################################

def _wrap_sqlite_error(error:'Exception') -> 'DBAPIError':
    """ Returns an error of SQLite as the pub/sub writer raises it.
    """
    out = DBAPIError.instance(None, None, error, sqlite3.Error)
    out = cast_('DBAPIError', out)

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_duplicate_with_unrelated_items() -> 'None':
    """ A strict fenced acknowledgement whose receipt reuses the message ID of a stored message with different content
    fails its own caller alone, while a publication, push attempts and a lease of the same batch commit.
    """
    backend = _new_backend()

    _ = backend.publish(_topic_receipts, _data_receipt, msg_id=_taken_msg_id)
    order_msg_ids = _publish_orders(backend)
    messages = _pull_inputs(backend, 1)
    first_message = messages[0]

    input_rows = get_delivery_rows(_sub_key_input)

    data_order = _data_order.format('0300')

    built = build_publication(backend, _topic_orders, data_order)
    publication = built.pending
    publication_msg_id = publication.message_values['msg_id']

    atomic = _new_atomic(backend, first_message, _taken_msg_id, _data_receipt_other)
    attempts = _new_attempts()
    lease = _new_lease(backend)

    write_in_one_commit(backend, [publication, atomic, attempts, lease])

    # The fenced acknowledgement failed and wrote neither its acknowledgement nor its receipt ..
    assert isinstance(atomic.exception, PubSubDuplicateMsgID), atomic.exception
    assert get_delivery_rows(_sub_key_input) == input_rows
    assert _get_payloads(_topic_receipts) == {_taken_msg_id: _data_receipt}

    # .. while the other items of the batch committed.
    assert publication.exception is None, publication.exception
    assert attempts.exception is None, attempts.exception

    order_payloads = _get_payloads(_topic_orders)
    assert publication_msg_id in order_payloads, order_payloads

    _assert_orders_leased(lease, order_msg_ids)

# ################################################################################################################################

def run_duplicate_first_writer() -> 'None':
    """ A strict fenced acknowledgement that is the first writer of its batch and whose receipt reuses the message ID
    of a stored message with different content fails its own caller alone, while another fenced acknowledgement,
    push attempts and a lease of the same batch commit.
    """
    backend = _new_backend()

    _ = backend.publish(_topic_receipts, _data_receipt, msg_id=_taken_msg_id)
    order_msg_ids = _publish_orders(backend)
    messages = _pull_inputs(backend, 2)
    first_message = messages[0]
    second_message = messages[1]

    failing = _new_atomic(backend, first_message, _taken_msg_id, _data_receipt_other)
    passing = _new_atomic(backend, second_message, _free_msg_id, _data_receipt)
    attempts = _new_attempts()
    lease = _new_lease(backend)

    write_in_one_commit(backend, [failing, passing, attempts, lease])

    # The first fenced acknowledgement failed and wrote nothing ..
    assert isinstance(failing.exception, PubSubDuplicateMsgID), failing.exception

    # .. while the second one acknowledged its message and published its receipt ..
    assert passing.exception is None, passing.exception
    assert len(get_delivery_rows(_sub_key_input)) == 1

    receipt_payloads = _get_payloads(_topic_receipts)
    assert receipt_payloads == {_taken_msg_id: _data_receipt, _free_msg_id: _data_receipt}, receipt_payloads

    # .. and the other items committed.
    assert attempts.exception is None, attempts.exception
    _assert_orders_leased(lease, order_msg_ids)

# ################################################################################################################################

def run_concurrent_publication() -> 'None':
    """ A fenced acknowledgement that is the first writer of its batch checks its receipt under the write lock
    of the database, so another process that publishes a different message with the same ID while the item is checked
    publishes it only after the batch committed, and is refused, instead of failing every item of the batch.
    """
    backend = _new_backend()
    engine = get_database_engine()

    order_msg_ids = _publish_orders(backend)
    messages = _pull_inputs(backend, 1)
    first_message = messages[0]

    atomic = _new_atomic(backend, first_message, _free_msg_id, _data_receipt)
    attempts = _new_attempts()
    lease = _new_lease(backend)

    publisher = ConcurrentPublisher(_topic_receipts, _data_receipt_other, _free_msg_id)

    try:
        with publisher.signal_on_fenced_select(engine):
            write_in_one_commit(backend, [atomic, attempts, lease])

        # The other process was signaled while the fenced acknowledgement was checked,
        # and its publication did not complete before the batch committed ..
        assert publisher.is_signaled
        assert publisher.outcome_during_batch is None, publisher.outcome_during_batch

        outcome = publisher.get_outcome()

    finally:
        publisher.stop()

    # .. every item of the batch committed ..
    assert atomic.exception is None, atomic.exception
    assert attempts.exception is None, attempts.exception
    assert get_delivery_rows(_sub_key_input) == []
    assert _get_payloads(_topic_receipts) == {_free_msg_id: _data_receipt}

    _assert_orders_leased(lease, order_msg_ids)

    # .. and the publication of the other process, which followed the receipt, was refused.
    assert outcome == PubSubDuplicateMsgID.__name__, outcome

# ################################################################################################################################

def run_rejected_value() -> 'None':
    """ A publication whose payload SQLite rejects fails its own caller alone, and the other items of its batch commit
    once the batch is written item by item.
    """
    backend = _new_backend()
    engine = get_database_engine()

    order_msg_ids = _publish_orders(backend)
    first_order_msg_id = order_msg_ids[0]

    data_small = _data_order.format('0400')

    built_small = build_publication(backend, _topic_orders, data_small)
    built_large = build_publication(backend, _topic_orders, _data_too_long)

    small = built_small.pending
    large = built_large.pending
    ack = new_pending_ack(_sub_key_orders, [first_order_msg_id], None)

    small_msg_id = small.message_values['msg_id']
    large_msg_id = large.message_values['msg_id']

    length_limit = LengthLimit(_value_length_limit)

    with length_limit.applied(engine), _recording_splits() as split_records:
        write_in_one_commit(backend, [small, large, ack])

    # The large publication failed with the error of SQLite ..
    assert isinstance(large.exception, DBAPIError), large.exception
    assert isinstance(large.exception.orig, sqlite3.DataError), large.exception.orig

    # .. the other items committed ..
    assert small.exception is None, small.exception
    assert ack.exception is None, ack.exception
    assert ack.removed_count == 1

    order_payloads = _get_payloads(_topic_orders)
    assert small_msg_id in order_payloads, order_payloads
    assert large_msg_id not in order_payloads, order_payloads

    # .. because the batch was written item by item.
    split_count = len(split_records.messages)
    assert split_count == 1, split_records.messages

# ################################################################################################################################

def run_value_error_classes() -> 'None':
    """ The errors of SQLite about the values of one statement are value errors, and the error of a lock is not.
    """
    integrity_error = _wrap_sqlite_error(sqlite3.IntegrityError('NOT NULL constraint failed: pubsub_message.topic_name'))
    data_error      = _wrap_sqlite_error(sqlite3.DataError('string or blob too big'))
    lock_error      = _wrap_sqlite_error(sqlite3.OperationalError('database is locked'))

    assert is_value_error(integrity_error)
    assert is_value_error(data_error)
    assert not is_value_error(lock_error)

# ################################################################################################################################
# ################################################################################################################################
