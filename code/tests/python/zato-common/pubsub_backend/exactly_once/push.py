# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from exactly_once.common import build, count_deliveries, count_messages, get_msg_ids, In_Sub_Key, new_backend, Out_Sub_Key_A, \
    Out_Sub_Key_B, Out_Topic_A, Out_Topic_B, publish_input
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import anylist, intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

def _fetch_batch(backend:'SQLPubSubBackend', count:'int') -> 'tuple[strlist, intlist]':
    """ Publishes the given number of input messages and returns the message IDs and the sequence IDs of the batch
    that a push delivery of the input subscriber reads.
    """
    for index in range(count):
        _ = publish_input(backend, f'input-{index}')

    messages = backend.fetch_pending(In_Sub_Key)
    assert len(messages) == count

    msg_ids:'strlist' = []
    sequence_ids:'intlist' = []

    for message in messages:
        msg_ids.append(message['msg_id'])
        sequence_ids.append(message['sequence_id'])

    out = (msg_ids, sequence_ids)
    return out

# ################################################################################################################################
# ################################################################################################################################

def run_atomic_rollback_scenario() -> 'None':
    """ A push batch whose transaction fails on its second publication commits neither publication nor its acknowledgement,
    and the same batch committed again afterwards stores each publication once and acknowledges both messages.
    """
    backend = new_backend()
    msg_ids, sequence_ids = _fetch_batch(backend, 2)

    first = build(backend, Out_Topic_A, 'output-a')
    second = build(backend, Out_Topic_B, 'output-b')

    # A column that may not be NULL fails the insert of the second publication ..
    data_size = second.pending.message_values['data_size']
    second.pending.message_values['data_size'] = None

    publications:'anylist' = [first.pending, second.pending]

    with pytest.raises(DBAPIError):
        backend.ack_with_publications(In_Sub_Key, msg_ids, sequence_ids, publications)

    # .. so neither publication is stored ..
    assert count_messages(Out_Topic_A) == 0
    assert count_messages(Out_Topic_B) == 0

    # .. and both messages remain in the queue and are read again.
    assert count_deliveries(In_Sub_Key) == 2
    assert len(backend.fetch_pending(In_Sub_Key)) == 2

    # The same items committed again leave nothing of the failed transaction behind ..
    second.pending.message_values['data_size'] = data_size
    backend.ack_with_publications(In_Sub_Key, msg_ids, sequence_ids, publications)

    # .. each publication is stored once ..
    assert count_messages(Out_Topic_A) == 1
    assert count_messages(Out_Topic_B) == 1
    assert count_deliveries(Out_Sub_Key_A) == 1
    assert count_deliveries(Out_Sub_Key_B) == 1

    # .. and both messages are acknowledged.
    assert count_deliveries(In_Sub_Key) == 0

# ################################################################################################################################

def run_repeat_in_batch_scenario() -> 'None':
    """ A publication of a push batch that repeats an existing message with the same content creates no second message,
    while the acknowledgement and the other publication of the batch are committed.
    """
    backend = new_backend()
    msg_ids, sequence_ids = _fetch_batch(backend, 1)

    repeated_msg_id = 'exactly-once.backend.repeated'
    _ = backend.publish(Out_Topic_A, 'output-a', msg_id=repeated_msg_id)

    repeated = build(backend, Out_Topic_A, 'output-a', msg_id=repeated_msg_id)
    other = build(backend, Out_Topic_B, 'output-b')

    backend.ack_with_publications(In_Sub_Key, msg_ids, sequence_ids, [repeated.pending, other.pending])

    # The repetition is recognized ..
    assert repeated.pending.is_repeat
    assert get_msg_ids(Out_Topic_A) == [repeated_msg_id]
    assert count_deliveries(Out_Sub_Key_A) == 1

    # .. while the rest of the batch is committed.
    assert count_messages(Out_Topic_B) == 1
    assert count_deliveries(In_Sub_Key) == 0

# ################################################################################################################################

def run_batch_committed_twice_scenario() -> 'None':
    """ A push batch that is committed a second time with publications of its own, which is what a delivery that started
    before the first commit landed produces, is rejected, and one without publications commits nothing.
    """
    backend = new_backend()
    msg_ids, sequence_ids = _fetch_batch(backend, 2)

    first = build(backend, Out_Topic_A, 'output-first')
    backend.ack_with_publications(In_Sub_Key, msg_ids, sequence_ids, [first.pending])

    # The second delivery of the same batch published again under new message IDs ..
    second = build(backend, Out_Topic_A, 'output-second')

    with pytest.raises(PubSubAckConflict):
        backend.ack_with_publications(In_Sub_Key, msg_ids, sequence_ids, [second.pending])

    # .. which are not stored ..
    assert get_msg_ids(Out_Topic_A) == [first.pending.message_values['msg_id']]
    assert count_deliveries(Out_Sub_Key_A) == 1

    # .. and a second delivery that published nothing concludes without an error.
    backend.ack_with_publications(In_Sub_Key, msg_ids, sequence_ids, [])

    assert count_messages(Out_Topic_A) == 1
    assert count_deliveries(In_Sub_Key) == 0

# ################################################################################################################################
# ################################################################################################################################
