# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The rows that acknowledgements leave behind and what each acknowledgement removed, by public message identifiers
# and by primary keys, alone and in commits shared with other acknowledgements, with the payloads of the messages
# that no subscriber needs anymore dropped.

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, get_message_rows, get_trace_rows, \
    write_in_one_commit
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.pending import new_pending_ack
from zato.common.test.audit_log_ import new_test_audit_log

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.pending import PendingAck
    from zato.common.typing_ import anydict, intlist, strlist

    anydict = anydict
    intlist = intlist
    PendingAck = PendingAck
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The topics and subscribers of the scenario
_topic_shared = 'pubsub.backend.test.ack-values.shared'
_topic_single = 'pubsub.backend.test.ack-values.single'

_sub_key_first  = 'zpsk.test.ack-values.first'
_sub_key_second = 'zpsk.test.ack-values.second'

# A message identifier that no message stands for
_unknown_msg_id = 'zpsm.test.ack-values.unknown'

# The payload of each message published
_data = 'Invoice INV-7781 for John Smith'

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend with an audit log of its own, starting from empty tables,
    with two subscribers of the shared topic and the first one alone subscribed to the single topic.
    """
    delete_all_rows()
    delete_audit_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())
    _subscribe(out)

    return out

# ################################################################################################################################

def _subscribe(backend:'SQLPubSubBackend') -> 'None':
    """ Subscribes both subscribers to the shared topic and the first one to the single topic.
    """
    backend.subscribe(_sub_key_first, _topic_shared)
    backend.subscribe(_sub_key_second, _topic_shared)
    backend.subscribe(_sub_key_first, _topic_single)

# ################################################################################################################################

def _publish(backend:'SQLPubSubBackend', topic_name:'str', count:'int') -> 'strlist':
    """ Publishes the given number of messages to one topic and returns their identifiers.
    """
    out:'strlist' = []

    for _ in range(count):
        result = backend.publish(topic_name, _data)
        out.append(result.msg_id)

    return out

# ################################################################################################################################

def _ack(backend:'SQLPubSubBackend', sub_key:'str', msg_ids:'strlist', sequence_ids:'intlist | None'=None) -> 'PendingAck':
    """ Writes one acknowledgement in a commit of its own and returns it with what it removed.
    """
    out = new_pending_ack(sub_key, msg_ids, sequence_ids)
    backend._writer.ack(out)

    return out

# ################################################################################################################################

def _assert_ack(pending:'PendingAck', removed_count:'int', fully_delivered_count:'int') -> 'None':
    """ An acknowledgement removed the given number of rows, of which the given number of messages became fully delivered.
    """
    assert pending.exception is None, pending.exception
    assert pending.removed_count == removed_count, (pending.removed_count, removed_count)
    assert pending.fully_delivered_count == fully_delivered_count, (pending.fully_delivered_count, fully_delivered_count)

# ################################################################################################################################

def _get_queue(sub_key:'str') -> 'strlist':
    """ Returns the identifiers of the messages that a subscriber's delivery rows refer to, in the order of the rows.
    """
    msg_ids_by_id:'anydict' = {}

    for topic_name in (_topic_shared, _topic_single):
        for row in get_message_rows(topic_name):
            msg_ids_by_id[row.id] = row.msg_id

    out:'strlist' = []

    for row in get_delivery_rows(sub_key):
        msg_id = msg_ids_by_id[row.message_id]
        out.append(msg_id)

    return out

# ################################################################################################################################

def _get_payloads(topic_name:'str') -> 'anydict':
    """ Returns the stored payload of each message of a topic and whether it is encrypted, by message identifier.
    """
    out:'anydict' = {}

    for row in get_message_rows(topic_name):
        out[row.msg_id] = (row.payload, row.payload_encrypted)

    return out

# ################################################################################################################################

def _get_sequence_id(msg_id:'str') -> 'int':
    """ Returns the primary key of the message row of a message identifier.
    """
    for row in get_message_rows(_topic_shared):
        if row.msg_id == msg_id:
            out = row.id
            break
    else:
        raise Exception(f'No message row for {msg_id}')

    return out

# ################################################################################################################################

def _run_by_msg_id(backend:'SQLPubSubBackend') -> 'None':
    """ An acknowledgement by public identifiers removes the rows of its own subscriber alone, and the last subscriber
    to acknowledge a message makes it fully delivered and drops its payload.
    """
    first, second, third = _publish(backend, _topic_shared, 3)

    # The first subscriber acknowledges two of the messages, which the other one still needs ..
    pending = _ack(backend, _sub_key_first, [first, second])
    _assert_ack(pending, 2, 0)

    assert _get_queue(_sub_key_first) == [third]
    assert _get_queue(_sub_key_second) == [first, second, third]

    payloads = _get_payloads(_topic_shared)
    assert payloads == {first: (_data, False), second: (_data, False), third: (_data, False)}, payloads

    # .. the second subscriber acknowledges the first message, which is now fully delivered ..
    pending = _ack(backend, _sub_key_second, [first])
    _assert_ack(pending, 1, 1)

    assert _get_queue(_sub_key_second) == [second, third]

    payloads = _get_payloads(_topic_shared)
    assert payloads == {first: (None, False), second: (_data, False), third: (_data, False)}, payloads

    # .. which makes it a trace ..
    traces = get_trace_rows(_topic_shared)
    first_id = _get_sequence_id(first)

    assert len(traces) == 1, traces
    assert traces[0].message_id == first_id

    # .. a repeated acknowledgement and an unknown identifier remove nothing ..
    pending = _ack(backend, _sub_key_second, [first, _unknown_msg_id])
    _assert_ack(pending, 0, 0)

    # .. and neither does an acknowledgement of a message that only the other subscriber's queue still holds.
    pending = _ack(backend, _sub_key_first, [second])
    _assert_ack(pending, 0, 0)

    assert _get_queue(_sub_key_first) == [third]
    assert _get_queue(_sub_key_second) == [second, third]

# ################################################################################################################################

def _run_by_sequence_id(backend:'SQLPubSubBackend') -> 'None':
    """ An acknowledgement by primary keys removes the rows of those messages, its identifiers notwithstanding.
    """
    first, second = _publish(backend, _topic_shared, 2)

    first_id = _get_sequence_id(first)
    second_id = _get_sequence_id(second)

    # The primary key of the first message is given with the identifier of the second one ..
    pending = _ack(backend, _sub_key_first, [second], [first_id])
    _assert_ack(pending, 1, 0)

    assert _get_queue(_sub_key_first) == [second]

    # .. and the public API acknowledges by primary keys in the same way.
    fully_delivered_count = backend.ack_messages(_sub_key_second, [first], [first_id])
    assert fully_delivered_count == 1

    _ = backend.ack_messages(_sub_key_first, [second], [second_id])
    fully_delivered_count = backend.ack_messages(_sub_key_second, [second], [second_id])

    assert fully_delivered_count == 1
    assert _get_queue(_sub_key_first) == []
    assert _get_queue(_sub_key_second) == []

    payloads = _get_payloads(_topic_shared)
    assert payloads == {first: (None, False), second: (None, False)}, payloads

# ################################################################################################################################

def _run_same_row_in_one_commit(backend:'SQLPubSubBackend') -> 'None':
    """ Two acknowledgements of one commit about the same row remove it once, which counts towards the first of them.
    """
    msg_id, = _publish(backend, _topic_single, 1)

    first = new_pending_ack(_sub_key_first, [msg_id], None)
    second = new_pending_ack(_sub_key_first, [msg_id], None)

    write_in_one_commit(backend, [first, second])

    _assert_ack(first, 1, 1)
    _assert_ack(second, 0, 0)

    assert _get_queue(_sub_key_first) == []

    payloads = _get_payloads(_topic_single)
    assert payloads == {msg_id: (None, False)}, payloads

# ################################################################################################################################

def _run_subscribers_in_one_commit(backend:'SQLPubSubBackend') -> 'None':
    """ Acknowledgements of two subscribers in one commit remove the rows of their own messages alone, and a message
    that both of them acknowledge counts as fully delivered towards the last one.
    """
    first, second, shared = _publish(backend, _topic_shared, 3)

    # Each subscriber acknowledges another message and both acknowledge the shared one ..
    by_first = new_pending_ack(_sub_key_first, [first, shared], None)
    by_second = new_pending_ack(_sub_key_second, [second, shared], None)

    write_in_one_commit(backend, [by_first, by_second])

    _assert_ack(by_first, 2, 0)
    _assert_ack(by_second, 2, 1)

    # .. so the row of the other subscriber of each message stays in place ..
    assert _get_queue(_sub_key_first) == [second]
    assert _get_queue(_sub_key_second) == [first]

    # .. and the shared message alone lost its payload.
    payloads = _get_payloads(_topic_shared)
    assert payloads == {first: (_data, False), second: (_data, False), shared: (None, False)}, payloads

# ################################################################################################################################

def _run_encrypted_payload() -> 'None':
    """ A payload encrypted at rest is dropped with its flag cleared once the last subscriber acknowledges its message.
    """
    delete_all_rows()
    delete_audit_rows()

    secret_key = CryptoManager.generate_key()
    crypto_manager = CryptoManager(secret_key=secret_key)

    backend = SQLPubSubBackend(audit_log=new_test_audit_log(), crypto_manager=crypto_manager, encrypt_at_rest=True)
    _subscribe(backend)

    msg_id, = _publish(backend, _topic_single, 1)

    payload, is_encrypted = _get_payloads(_topic_single)[msg_id]

    assert is_encrypted
    assert crypto_manager.decrypt(payload) == _data

    pending = _ack(backend, _sub_key_first, [msg_id])
    _assert_ack(pending, 1, 1)

    payloads = _get_payloads(_topic_single)
    assert payloads == {msg_id: (None, False)}, payloads

# ################################################################################################################################

def run_ack_values_scenario() -> 'None':
    """ The rows that acknowledgements leave behind, each part starting from empty tables.
    """
    _run_by_msg_id(_new_backend())
    _run_by_sequence_id(_new_backend())
    _run_same_row_in_one_commit(_new_backend())
    _run_subscribers_in_one_commit(_new_backend())
    _run_encrypted_payload()

# ################################################################################################################################
# ################################################################################################################################
