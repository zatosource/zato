# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Zato
from exactly_once.harness import build, count_deliveries, count_messages, First_Output_Sub_Key, First_Output_Topic, \
    get_attempt, get_built_msg_id, get_lease_ms, get_msg_ids, Input_Sub_Key, lease, lease_repeatedly, new_backend, \
    publish_input, Second_Output_Sub_Key, Second_Output_Topic
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.writes import PubSubDuplicateMsgID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import AckPulledResult, SQLPubSubBackend
    from zato.common.pubsub.sql.publication import built_publication_list

# ################################################################################################################################
# ################################################################################################################################

# The message ID that an existing message of the first output topic has
_taken_msg_id = 'exactly-once.backend.taken'

# ################################################################################################################################
# ################################################################################################################################

def _consume(
    backend:'SQLPubSubBackend',
    msg_id:'str',
    delivery_attempt:'int',
    publications:'built_publication_list',
    ) -> 'AckPulledResult':
    """ Acknowledges one message of the input subscriber with the given attempt, together with the publications.
    """
    consumed = [(msg_id, delivery_attempt)]

    out = backend.ack_pulled_with_publications(Input_Sub_Key, consumed, publications)
    return out

# ################################################################################################################################
# ################################################################################################################################

def run_ack_with_publications_scenario() -> 'None':
    """ A leased message acknowledged with two publications to two topics leaves the queue,
    and each subscriber of the two topics receives one delivery.
    """
    backend = new_backend()
    msg_id = publish_input(backend, 'input')

    now_ms = backend.clock.now_ms()
    attempts = lease(backend, now_ms)
    attempt = attempts[msg_id]

    first = build(backend, First_Output_Topic, 'output-first')
    second = build(backend, Second_Output_Topic, 'output-second')

    first_msg_id = get_built_msg_id(first)
    second_msg_id = get_built_msg_id(second)

    result = _consume(backend, msg_id, attempt, [first, second])

    # The message is acknowledged ..
    assert attempt == 1
    assert result.removed_count == 1
    assert result.published == [first_msg_id, second_msg_id]
    assert count_deliveries(Input_Sub_Key) == 0

    # .. and both publications are stored, each with a delivery of its own.
    assert get_msg_ids(First_Output_Topic) == [first_msg_id]
    assert get_msg_ids(Second_Output_Topic) == [second_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 1
    assert count_deliveries(Second_Output_Sub_Key) == 1

# ################################################################################################################################

def run_stale_attempt_scenario() -> 'None':
    """ An acknowledgement with the attempt of a lease that ran out and was followed by another lease is rejected
    and stores nothing, while the acknowledgement with the current attempt commits.
    """
    backend = new_backend()
    msg_id = publish_input(backend, 'input')

    # The message is leased twice, the second time after the first lease ran out ..
    now_ms = backend.clock.now_ms()
    lease_result = lease_repeatedly(backend, now_ms, 2)

    assert lease_result.attempts[msg_id] == 2

    # .. so the acknowledgement of the first lease is rejected ..
    stale = build(backend, First_Output_Topic, 'output-stale')

    with pytest.raises(PubSubAckConflict):
        _ = _consume(backend, msg_id, 1, [stale])

    # .. stores no publication and leaves the row of the second lease in place ..
    assert count_messages(First_Output_Topic) == 0
    assert get_attempt(backend, msg_id) == 2

    # .. while the acknowledgement of the second lease commits.
    current = build(backend, First_Output_Topic, 'output-current')
    current_msg_id = get_built_msg_id(current)

    result = _consume(backend, msg_id, 2, [current])

    assert result.removed_count == 1
    assert get_msg_ids(First_Output_Topic) == [current_msg_id]
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################

def run_repeated_call_scenario() -> 'None':
    """ An acknowledgement sent again with the same publications, after the reply to the first one was lost,
    commits nothing, raises nothing and reports no removed row, and each publication is stored once.
    """
    backend = new_backend()
    msg_id = publish_input(backend, 'input')

    now_ms = backend.clock.now_ms()
    attempts = lease(backend, now_ms)
    attempt = attempts[msg_id]

    first = build(backend, First_Output_Topic, 'output-first')
    second = build(backend, Second_Output_Topic, 'output-second')

    first_msg_id = get_built_msg_id(first)
    second_msg_id = get_built_msg_id(second)

    # The first call commits ..
    first_result = _consume(backend, msg_id, attempt, [first, second])
    assert first_result.removed_count == 1

    # .. and the same request sent again, built anew from the same input, commits nothing.
    first_again = build(backend, First_Output_Topic, 'output-first', msg_id=first_msg_id)
    second_again = build(backend, Second_Output_Topic, 'output-second', msg_id=second_msg_id)

    repeated_result = _consume(backend, msg_id, attempt, [first_again, second_again])

    assert repeated_result.removed_count == 0
    assert repeated_result.published == [first_msg_id, second_msg_id]

    assert get_msg_ids(First_Output_Topic) == [first_msg_id]
    assert get_msg_ids(Second_Output_Topic) == [second_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 1
    assert count_deliveries(Second_Output_Sub_Key) == 1

# ################################################################################################################################

def run_concluded_with_other_publications_scenario() -> 'None':
    """ After the current copy of a message committed its publication, an earlier copy with a publication
    of its own is rejected and its publication is not stored.
    """
    backend = new_backend()
    msg_id = publish_input(backend, 'input')

    now_ms = backend.clock.now_ms()
    _ = lease_repeatedly(backend, now_ms, 2)

    # The current copy commits ..
    current = build(backend, First_Output_Topic, 'output-current')
    current_msg_id = get_built_msg_id(current)

    _ = _consume(backend, msg_id, 2, [current])

    # .. and the earlier copy, which published something else, is rejected.
    earlier = build(backend, First_Output_Topic, 'output-earlier')

    with pytest.raises(PubSubAckConflict):
        _ = _consume(backend, msg_id, 1, [earlier])

    assert get_msg_ids(First_Output_Topic) == [current_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 1

# ################################################################################################################################

def run_concluded_with_same_publications_scenario() -> 'None':
    """ After the current copy of a message committed its publication, an earlier copy that derived the same publication
    from the same input commits nothing and raises nothing.
    """
    backend = new_backend()
    msg_id = publish_input(backend, 'input')

    now_ms = backend.clock.now_ms()
    _ = lease_repeatedly(backend, now_ms, 2)

    derived_msg_id = f'{msg_id}.output'

    # The current copy commits ..
    current = build(backend, First_Output_Topic, 'output', msg_id=derived_msg_id)
    _ = _consume(backend, msg_id, 2, [current])

    # .. and the earlier copy with the same publication concludes without an error.
    earlier = build(backend, First_Output_Topic, 'output', msg_id=derived_msg_id)
    result = _consume(backend, msg_id, 1, [earlier])

    assert result.removed_count == 0
    assert result.published == [derived_msg_id]

    assert get_msg_ids(First_Output_Topic) == [derived_msg_id]
    assert count_deliveries(First_Output_Sub_Key) == 1

# ################################################################################################################################

def run_different_content_scenario() -> 'None':
    """ A publication whose message ID belongs to a message with different content rolls the whole acknowledgement back.
    """
    backend = new_backend()
    msg_id = publish_input(backend, 'input')

    _ = backend.publish(First_Output_Topic, 'original', msg_id=_taken_msg_id)

    now_ms = backend.clock.now_ms()
    attempts = lease(backend, now_ms)
    attempt = attempts[msg_id]

    taken = build(backend, First_Output_Topic, 'different', msg_id=_taken_msg_id)
    other = build(backend, Second_Output_Topic, 'output-second')

    with pytest.raises(PubSubDuplicateMsgID):
        _ = _consume(backend, msg_id, attempt, [taken, other])

    # No publication is stored ..
    assert get_msg_ids(First_Output_Topic) == [_taken_msg_id]
    assert count_messages(Second_Output_Topic) == 0

    # .. and the consumed message remains in the queue.
    assert count_deliveries(Input_Sub_Key) == 1

# ################################################################################################################################

def run_lease_ran_out_scenario() -> 'None':
    """ A message whose lease ran out, and which no other pull handed out since, is acknowledged
    with the attempt of that lease.
    """
    backend = new_backend()
    msg_id = publish_input(backend, 'input')

    # The lease is taken at a time such that it ran out before now ..
    lease_ms = get_lease_ms()
    now_ms = backend.clock.now_ms()
    lease_now_ms = now_ms - lease_ms - lease_ms

    attempts = lease(backend, lease_now_ms)
    attempt = attempts[msg_id]

    # .. and the acknowledgement with its attempt commits.
    output = build(backend, First_Output_Topic, 'output')
    output_msg_id = get_built_msg_id(output)

    result = _consume(backend, msg_id, attempt, [output])

    assert attempt == 1
    assert result.removed_count == 1
    assert get_msg_ids(First_Output_Topic) == [output_msg_id]
    assert count_deliveries(Input_Sub_Key) == 0

# ################################################################################################################################
# ################################################################################################################################
