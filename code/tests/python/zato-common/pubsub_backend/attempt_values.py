# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The push attempts that are recorded in the delivery rows before their requests are sent, the attempt numbers that
# their callers receive, and the deliveries that the same commit acknowledged, which receive no attempt.

# Zato
from common import delete_all_rows, delete_audit_rows, get_delivery_rows, write_in_one_commit
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.pending import new_pending_ack, new_pending_attempts
from zato.common.test.audit_log_ import new_test_audit_log

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, intdict, intlist

    anydict = anydict
    anylist = anylist
    intdict = intdict
    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

# The topic and the subscriber of the scenario
_topic = 'pubsub.backend.test.attempt-values'
_sub_key = 'zpsk.test.attempt-values'

# The payload of each message published
_data = 'Invoice INV-7781 for John Smith'

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'SQLPubSubBackend':
    """ Returns a backend with an audit log of its own, starting from empty tables, with one subscriber of the topic.
    """
    delete_all_rows()
    delete_audit_rows()

    out = SQLPubSubBackend(audit_log=new_test_audit_log())
    out.subscribe(_sub_key, _topic)

    return out

# ################################################################################################################################

def _get_attempts() -> 'intdict':
    """ Returns the attempt column of each delivery row of the subscriber, by delivery ID.
    """
    out:'intdict' = {}

    for row in get_delivery_rows(_sub_key):
        out[row.id] = row.attempt

    return out

# ################################################################################################################################

def _fetch(backend:'SQLPubSubBackend', count:'int') -> 'anylist':
    """ Publishes the given number of messages and fetches them for push delivery.
    """
    for _ in range(count):
        _ = backend.publish(_topic, _data)

    out = backend.fetch_messages(_sub_key)
    assert len(out) == count, out

    return out

# ################################################################################################################################

def _get_delivery_ids(messages:'anylist') -> 'intlist':
    """ Returns the delivery ID of each fetched message, in the order of the messages.
    """
    out:'intlist' = []

    for message in messages:
        out.append(message['delivery_id'])

    return out

# ################################################################################################################################

def _run_record_attempts(backend:'SQLPubSubBackend') -> 'None':
    """ Each attempt is the next number of its delivery, stored in its message and recorded in its delivery row.
    """
    messages = _fetch(backend, 2)
    delivery_ids = _get_delivery_ids(messages)

    # A fetched message has no attempt yet ..
    for message in messages:
        assert message['delivery_attempt'] == 0, message

    assert _get_attempts() == {delivery_ids[0]: 0, delivery_ids[1]: 0}

    # .. each recording adds one attempt to each message ..
    for expected_attempt in (1, 2):

        recorded = backend.record_attempts(messages)
        assert recorded == set(delivery_ids), recorded

        for message in messages:
            assert message['delivery_attempt'] == expected_attempt, message

        # .. which the delivery rows hold as well.
        assert _get_attempts() == {delivery_ids[0]: expected_attempt, delivery_ids[1]: expected_attempt}

    # A single message is recorded in the same way.
    is_recorded = backend.record_attempt(messages[0])

    assert is_recorded
    assert messages[0]['delivery_attempt'] == 3

# ################################################################################################################################

def _run_acknowledged_before(backend:'SQLPubSubBackend') -> 'None':
    """ A delivery acknowledged before its attempt is recorded receives no attempt, and its caller learns
    that it left the queue.
    """
    messages = _fetch(backend, 2)
    delivery_ids = _get_delivery_ids(messages)

    _ = backend.ack_messages(_sub_key, [messages[0]['msg_id']])

    recorded = backend.record_attempts(messages)

    assert recorded == {delivery_ids[1]}, recorded
    assert messages[0]['delivery_attempt'] == 0
    assert messages[1]['delivery_attempt'] == 1
    assert _get_attempts() == {delivery_ids[1]: 1}

# ################################################################################################################################

def _run_acknowledged_in_one_commit(backend:'SQLPubSubBackend') -> 'None':
    """ A delivery that the commit of its attempts also acknowledges receives no attempt, and the other ones do.
    """
    messages = _fetch(backend, 2)
    delivery_ids = _get_delivery_ids(messages)

    ack = new_pending_ack(_sub_key, [messages[0]['msg_id']], None)
    attempts = new_pending_attempts(delivery_ids)

    write_in_one_commit(backend, [attempts, ack])

    assert ack.exception is None
    assert ack.removed_count == 1

    assert attempts.exception is None
    assert attempts.attempts == {delivery_ids[1]: 1}, attempts.attempts

    assert _get_attempts() == {delivery_ids[1]: 1}

# ################################################################################################################################

def run_attempt_values_scenario() -> 'None':
    """ The push attempts recorded before their requests are sent, each part starting from empty tables.
    """
    _run_record_attempts(_new_backend())
    _run_acknowledged_before(_new_backend())
    _run_acknowledged_in_one_commit(_new_backend())

# ################################################################################################################################
# ################################################################################################################################
