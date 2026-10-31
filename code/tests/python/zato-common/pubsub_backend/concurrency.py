# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
import gevent

# SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Zato
from common import delete_all_rows, get_delivery_rows, get_message_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.writes import PubSubWriter
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.pubsub.sql.backend import PublishResult
    from zato.common.typing_ import anylist, intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The topic and subscribers all the concurrency assertions share.
_topic = 'pubsub.backend.test.concurrency'
_sub_key_1 = 'zpsk.test.concurrency.1'
_sub_key_2 = 'zpsk.test.concurrency.2'

# How many callers publish or acknowledge at the same time.
_caller_count = 200

# How many callers try to claim the same message.
_claimer_count = 20

# ################################################################################################################################
# ################################################################################################################################

class _RecordingWriter(PubSubWriter):
    """ A writer that records how many items each of its transactions held.
    """

    def __init__(self) -> 'None':
        super().__init__()
        self.transaction_sizes:'intlist' = []

    def _write_transaction(self, engine:'Engine', batch:'anylist') -> 'None':
        self.transaction_sizes.append(len(batch))
        super()._write_transaction(engine, batch)

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'tuple[SQLPubSubBackend, _RecordingWriter]':
    """ Returns a backend whose writes are recorded, subscribed to the shared topic by both subscribers.
    """
    delete_all_rows()

    writer = _RecordingWriter()

    backend = SQLPubSubBackend()
    backend._writer = writer

    backend.subscribe(_sub_key_1, _topic)
    backend.subscribe(_sub_key_2, _topic)

    out = backend, writer
    return out

# ################################################################################################################################

def _publish_concurrently(backend:'SQLPubSubBackend', count:'int') -> 'strlist':
    """ Publishes the given number of messages from as many concurrent callers and returns their identifiers.
    """
    greenlets:'anylist' = []

    for index in range(count):
        greenlet = gevent.spawn(backend.publish, _topic, f'concurrent-message-{index}')
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    out:'strlist' = []

    for greenlet in greenlets:
        result:'PublishResult' = greenlet.value
        out.append(result.msg_id)

    return out

# ################################################################################################################################

def _run_concurrent_publish_flow() -> 'None':
    """ Concurrent publishers share commits and each of them gets its own message with one delivery row per subscriber.
    """
    backend, writer = _new_backend()

    msg_ids = _publish_concurrently(backend, _caller_count)

    # Each publisher has a message of its own ..
    assert len(set(msg_ids)) == _caller_count

    message_rows = get_message_rows(_topic)
    assert len(message_rows) == _caller_count

    # .. with its payload kept for the subscribers ..
    for row in message_rows:
        assert row.payload is not None

    # .. each subscriber has one delivery row per message ..
    for sub_key in (_sub_key_1, _sub_key_2):

        delivered_message_ids:'intlist' = []

        for row in get_delivery_rows(sub_key):
            delivered_message_ids.append(row.message_id)

        assert len(delivered_message_ids) == _caller_count
        assert len(set(delivered_message_ids)) == _caller_count

    # .. and the publishers shared their commits.
    assert sum(writer.transaction_sizes) == _caller_count
    assert max(writer.transaction_sizes) > 1, writer.transaction_sizes
    assert len(writer.transaction_sizes) < _caller_count, writer.transaction_sizes

# ################################################################################################################################

def _publish_duplicate(backend:'SQLPubSubBackend', msg_id:'str') -> 'str':
    """ Publishes a message under a given identifier and tells whether it was stored or rejected.
    """
    try:
        _ = backend.publish(_topic, 'duplicate-message', msg_id=msg_id)
    except IntegrityError:
        out = 'rejected'
    else:
        out = 'stored'

    return out

# ################################################################################################################################

def _run_duplicate_flow() -> 'None':
    """ A message whose identifier exists already fails its own publisher alone, the others in its commit succeed.
    """
    backend, _ignored = _new_backend()

    existing_msg_id = 'zpsm.test.concurrency.duplicate'
    _ = backend.publish(_topic, 'original-message', msg_id=existing_msg_id)

    greenlets:'anylist' = []

    for index in range(_caller_count):

        # Every tenth caller reuses the identifier that exists already.
        if index % 10 == 0:
            msg_id = existing_msg_id
        else:
            msg_id = f'zpsm.test.concurrency.unique.{index}'

        greenlet = gevent.spawn(_publish_duplicate, backend, msg_id)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    rejected_count = 0
    stored_count = 0

    for index, greenlet in enumerate(greenlets):

        outcome = greenlet.value

        if index % 10 == 0:
            assert outcome == 'rejected', index
            rejected_count += 1
        else:
            assert outcome == 'stored', index
            stored_count += 1

    # The original and every unique message are stored, with their delivery rows.
    message_rows = get_message_rows(_topic)
    assert len(message_rows) == stored_count + 1

    delivery_rows = get_delivery_rows(_sub_key_1)
    assert len(delivery_rows) == stored_count + 1

# ################################################################################################################################

def _ack_all(backend:'SQLPubSubBackend', sub_key:'str', msg_ids:'strlist') -> 'anylist':
    """ Acknowledges each message from a concurrent caller of its own and returns what each acknowledgement returned.
    """
    greenlets:'anylist' = []

    for msg_id in msg_ids:
        greenlet = gevent.spawn(backend.ack_message, sub_key, msg_id)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    out:'anylist' = []

    for greenlet in greenlets:
        out.append(greenlet.value)

    return out

# ################################################################################################################################

def _run_concurrent_ack_flow() -> 'None':
    """ Concurrent per-message acknowledgements of two subscribers remove every delivery row and every message
    becomes fully delivered exactly once.
    """
    backend, writer = _new_backend()

    msg_ids = _publish_concurrently(backend, _caller_count)
    writer.transaction_sizes.clear()

    # Both subscribers acknowledge every message at the same time ..
    first_greenlet = gevent.spawn(_ack_all, backend, _sub_key_1, msg_ids)
    second_greenlet = gevent.spawn(_ack_all, backend, _sub_key_2, msg_ids)

    _ = gevent.joinall([first_greenlet, second_greenlet], raise_error=True)

    first_results = cast_('anylist', first_greenlet.value)
    second_results = cast_('anylist', second_greenlet.value)

    fully_delivered:'anylist' = []
    fully_delivered.extend(first_results)
    fully_delivered.extend(second_results)

    # .. each message became fully delivered exactly once ..
    assert fully_delivered.count(True) == _caller_count

    # .. no delivery row is left ..
    assert get_delivery_rows(_sub_key_1) == []
    assert get_delivery_rows(_sub_key_2) == []

    # .. every message is a delivered-message trace ..
    for row in get_message_rows(_topic):
        assert row.payload is None

    # .. and the acknowledgements shared their commits.
    assert sum(writer.transaction_sizes) == 2 * _caller_count
    assert max(writer.transaction_sizes) > 1, writer.transaction_sizes

# ################################################################################################################################

def _run_concurrent_claim_flow() -> 'None':
    """ Of many concurrent callers claiming one message for one subscriber, exactly one succeeds.
    """
    backend, _ignored = _new_backend()

    result = backend.publish(_topic, 'claimed-message')

    greenlets:'anylist' = []

    for _index in range(_claimer_count):
        greenlet = gevent.spawn(backend.claim_message, _sub_key_1, result.msg_id)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    claims:'anylist' = []

    for greenlet in greenlets:
        claims.append(greenlet.value)

    assert claims.count(True) == 1, claims

    # The other subscriber still has the message, so it keeps its payload.
    assert len(get_delivery_rows(_sub_key_1)) == 0
    assert len(get_delivery_rows(_sub_key_2)) == 1

    message_rows = get_message_rows(_topic)
    assert message_rows[0].payload is not None

# ################################################################################################################################

def run_concurrency_scenario() -> 'None':
    """ Concurrent publications and acknowledgements, written in shared commits.
    """
    _run_concurrent_publish_flow()
    _run_duplicate_flow()
    _run_concurrent_ack_flow()
    _run_concurrent_claim_flow()

# ################################################################################################################################
# ################################################################################################################################
