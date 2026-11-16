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
from exactly_once.harness import build, count_deliveries, count_messages, First_Output_Sub_Key, First_Output_Topic, \
    get_built_msg_id, get_msg_ids, Input_Sub_Key, new_backend, publish_input, Second_Output_Sub_Key, Second_Output_Topic
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

def _fetch_batch(backend:'SQLPubSubBackend', count:'int') -> 'strlist':
    """ Publishes the given number of input messages and returns the message IDs of the batch
    that a push delivery of the input subscriber reads.
    """
    for index in range(count):
        data = f'input-{index}'
        _ = publish_input(backend, data)

    messages = backend.fetch_pending(Input_Sub_Key)
    message_count = len(messages)

    assert message_count == count

    out:'strlist' = []

    for message in messages:
        out.append(message['msg_id'])

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_atomic_rollback_scenario() -> 'None':
    """ A push batch whose transaction fails on its second publication commits neither publication nor its acknowledgement,
    and the same batch committed again afterwards stores each publication once and acknowledges both messages.
    """
    backend = new_backend()
    msg_ids = _fetch_batch(backend, 2)

    first = build(backend, First_Output_Topic, 'output-first')
    second = build(backend, Second_Output_Topic, 'output-second')

    second_values = second.pending.message_values

    # A column that may not be NULL fails the insert of the second publication ..
    data_size = second_values['data_size']
    second_values['data_size'] = None

    publications:'anylist' = [first.pending, second.pending]

    with pytest.raises(DBAPIError):
        backend.ack_with_publications(Input_Sub_Key, msg_ids, publications)

    # .. so neither publication is stored ..
    assert count_messages(First_Output_Topic) == 0
    assert count_messages(Second_Output_Topic) == 0

    # .. and both messages remain in the queue and are read again.
    pending = backend.fetch_pending(Input_Sub_Key)
    pending_count = len(pending)

    assert count_deliveries(Input_Sub_Key) == 2
    assert pending_count == 2

    # The same items committed again find nothing of the failed transaction ..
    second_values['data_size'] = data_size
    backend.ack_with_publications(Input_Sub_Key, msg_ids, publications)

    # .. each publication is stored once ..
    assert count_messages(First_Output_Topic) == 1
    assert count_messages(Second_Output_Topic) == 1
    assert count_deliveries(First_Output_Sub_Key) == 1
    assert count_deliveries(Second_Output_Sub_Key) == 1

    # .. and both messages are acknowledged.
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################

def run_repeat_in_batch_scenario() -> 'None':
    """ A publication of a push batch that repeats an existing message with the same content creates no second message,
    while the acknowledgement and the other publication of the batch are committed.
    """
    backend = new_backend()
    msg_ids = _fetch_batch(backend, 1)

    repeated_msg_id = 'exactly-once.backend.repeated'
    _ = backend.publish(First_Output_Topic, 'output-first', msg_id=repeated_msg_id)

    repeated = build(backend, First_Output_Topic, 'output-first', msg_id=repeated_msg_id)
    other = build(backend, Second_Output_Topic, 'output-second')

    publications:'anylist' = [repeated.pending, other.pending]
    backend.ack_with_publications(Input_Sub_Key, msg_ids, publications)

    # The repetition is recognized ..
    assert repeated.pending.is_repeat
    assert get_msg_ids(First_Output_Topic) == [repeated_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 1

    # .. while the rest of the batch is committed.
    assert count_messages(Second_Output_Topic) == 1
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################

def run_batch_committed_twice_scenario() -> 'None':
    """ A push batch that is committed a second time with publications of its own, which is what a delivery that started
    before the first commit produces, is rejected, and one without publications commits nothing.
    """
    backend = new_backend()
    msg_ids = _fetch_batch(backend, 2)

    first = build(backend, First_Output_Topic, 'output-first')
    first_msg_id = get_built_msg_id(first)

    first_publications:'anylist' = [first.pending]
    backend.ack_with_publications(Input_Sub_Key, msg_ids, first_publications)

    # The second delivery of the same batch published again under new message IDs ..
    second = build(backend, First_Output_Topic, 'output-second')
    second_publications:'anylist' = [second.pending]

    with pytest.raises(PubSubAckConflict):
        backend.ack_with_publications(Input_Sub_Key, msg_ids, second_publications)

    # .. which are not stored ..
    assert get_msg_ids(First_Output_Topic) == [first_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 1

    # .. and a second delivery that published nothing concludes without an error.
    backend.ack_with_publications(Input_Sub_Key, msg_ids, [])

    assert count_messages(First_Output_Topic) == 1
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################
# ################################################################################################################################
