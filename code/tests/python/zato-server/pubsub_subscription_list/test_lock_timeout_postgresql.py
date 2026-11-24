# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic

# gevent
from gevent import spawn

# SQLAlchemy
from sqlalchemy import text

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.subscription_list import Lock_Timeout_Ms

from .conftest import Security_Pull, Topic_Pull, Topic_Push_Rest, Topic_Second
from .helpers import sub_key_for_topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class _RowLock:
    """ Holds a FOR UPDATE lock on one row of a pub/sub table from a connection of its own.
    """

    def __init__(self, engine:'any_', statement:'str', params:'any_') -> 'None':
        self.engine = engine
        self.statement = statement
        self.params = params
        self.connection = None

# ################################################################################################################################

    def acquire(self) -> 'None':
        """ Opens a connection, begins a transaction and locks the row.
        """
        self.connection = self.engine.connect()
        _ = self.connection.execute(text('begin'))
        _ = self.connection.execute(text(self.statement), self.params)

# ################################################################################################################################

    def release(self) -> 'None':
        """ Rolls back the transaction and closes the connection.
        """
        if self.connection is None:
            return

        _ = self.connection.execute(text('rollback'))
        self.connection.close()
        self.connection = None

# ################################################################################################################################
# ################################################################################################################################

def test_lock_on_topic_sub_fails_only_needing_publications(in_process_server:'any_') -> 'None':
    """ A lock on a pubsub_topic_sub row fails only the publications that need that row after the lock timeout.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    backend = parallel.pubsub_backend
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)

    lock = _RowLock(
        backend.engine,
        'select 1 from pubsub_topic_sub where sub_key = :sub_key and topic_name = :topic_name for update',
        {'sub_key': sub_key, 'topic_name': Topic_Pull.lower()},
    )
    lock.acquire()

    try:
        other_data = 'other.topic.' + CryptoManager.generate_hex_string(8)
        other_result = backend.publish(Topic_Push_Rest, other_data)
        assert other_result.msg_id

        started = monotonic()
        raised = False

        try:
            _ = backend.publish(Topic_Pull, 'locked.topic.' + CryptoManager.generate_hex_string(8))
        except Exception:
            raised = True

        elapsed_ms = (monotonic() - started) * 1000

        assert raised
        assert elapsed_ms >= Lock_Timeout_Ms * 0.5
        assert elapsed_ms < Lock_Timeout_Ms * 3

    finally:
        lock.release()

# ################################################################################################################################

def test_enmasse_applies_while_row_lock_held(in_process_server:'any_') -> 'None':
    """ An enmasse file placed while a row lock is held is applied, and the wait ends after the lock is released.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    backend = parallel.pubsub_backend
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)

    lock = _RowLock(
        backend.engine,
        'select 1 from pubsub_topic_sub where sub_key = :sub_key and topic_name = :topic_name for update',
        {'sub_key': sub_key, 'topic_name': Topic_Pull.lower()},
    )
    lock.acquire()

    enmasse_yaml = f"""
pubsub_subscription:
  - security: {Security_Pull}
    delivery_type: pull
    topic_list:
      - {Topic_Pull}
      - {Topic_Second}
"""

    try:
        import_greenlet = spawn(server.apply_enmasse, 'while-locked', enmasse_yaml)

        other_data = 'while.locked.' + CryptoManager.generate_hex_string(8)
        other_result = backend.publish(Topic_Push_Rest, other_data)
        assert other_result.msg_id

        lock.release()
        exit_code = import_greenlet.get()

        assert exit_code == 0

        data = 'after.lock.release.' + CryptoManager.generate_hex_string(8)
        result = backend.publish(Topic_Second, data)
        assert result.msg_id

    finally:
        if lock.connection is not None:
            lock.release()

# ################################################################################################################################

def test_lock_on_queue_count_and_delivery(in_process_server:'any_') -> 'None':
    """ Locks on pubsub_queue_count and pubsub_delivery fail only the callers that need those rows.
    """
    server, _push_endpoint = in_process_server
    parallel = server.server
    backend = parallel.pubsub_backend
    subscription_list = parallel.pubsub_subscription_list

    sub_key = sub_key_for_topic(subscription_list, Topic_Pull)

    seed_result = backend.publish(Topic_Pull, 'seed.' + CryptoManager.generate_hex_string(8))

    queue_lock = _RowLock(
        backend.engine,
        'select 1 from pubsub_queue_count where sub_key = :sub_key and topic_name = :topic_name for update',
        {'sub_key': sub_key, 'topic_name': Topic_Pull.lower()},
    )
    queue_lock.acquire()

    # The triggers of PostgreSQL append change rows to pubsub_queue_count, so no publication needs a row that is locked
    try:
        other_result = backend.publish(Topic_Push_Rest, 'queue.other.' + CryptoManager.generate_hex_string(8))
        assert other_result.msg_id

        started = monotonic()
        locked_result = backend.publish(Topic_Pull, 'queue.locked.' + CryptoManager.generate_hex_string(8))
        elapsed_ms = (monotonic() - started) * 1000

        assert locked_result.msg_id
        assert elapsed_ms < Lock_Timeout_Ms * 0.5

    finally:
        queue_lock.release()

    delivery_lock = _RowLock(
        backend.engine,
        'select 1 from pubsub_delivery where sub_key = :sub_key and message_id = ' +
        '(select id from pubsub_message where msg_id = :msg_id) for update',
        {'sub_key': sub_key, 'msg_id': seed_result.msg_id},
    )
    delivery_lock.acquire()

    # An acknowledgement needs the delivery row that is locked, while publications insert rows of their own
    try:
        other_result = backend.publish(Topic_Push_Rest, 'delivery.other.' + CryptoManager.generate_hex_string(8))
        assert other_result.msg_id

        same_topic_result = backend.publish(Topic_Pull, 'delivery.same.' + CryptoManager.generate_hex_string(8))
        assert same_topic_result.msg_id

        raised = False
        started = monotonic()

        try:
            _ = backend.ack_messages(sub_key, [seed_result.msg_id])
        except Exception:
            raised = True

        elapsed_ms = (monotonic() - started) * 1000

        assert raised
        assert elapsed_ms >= Lock_Timeout_Ms * 0.5
        assert elapsed_ms < Lock_Timeout_Ms * 3

    finally:
        delivery_lock.release()

    # The acknowledgement that the lock failed commits once the lock is released
    removed_count = backend.ack_pulled(sub_key, [seed_result.msg_id])
    assert removed_count == 1

# ################################################################################################################################
# ################################################################################################################################
