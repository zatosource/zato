# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from exactly_once.harness import build, count_deliveries, First_Output_Topic, get_attempt, get_built_msg_id, get_lease_ms, \
    get_msg_ids, Input_Sub_Key, lease, new_backend, publish_input, Second_Output_Sub_Key, Second_Output_Topic
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.pending import new_fenced_ack, new_pending_atomic, new_pending_lease
from zato.common.pubsub.sql.writes import PubSubDuplicateMsgID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.pubsub.sql.pending import PendingAtomic, PendingLease
    from zato.common.pubsub.sql.publication import BuiltPublication
    from zato.common.typing_ import anylist, strintdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The message ID that an existing message of the first output topic stands for
_existing_msg_id = 'exactly-once.backend.batch.existing'

# The delivery attempt that no lease handed out, which an acknowledgement expects in vain
_stale_attempt = 5

# How many bytes the payloads of one lease of the batch scenarios may have in total
_lease_max_len = 10_000_000

# How many messages each of two leases of one batch may hand out
_shared_lease_max_messages = 2

# How many messages the input subscriber has for two leases of one batch
_shared_lease_message_count = 3

# ################################################################################################################################
# ################################################################################################################################

def _new_atomic(msg_id:'str', expected_attempt:'int', publication:'BuiltPublication') -> 'PendingAtomic':
    """ Returns a strict acknowledgement of one input message with one publication, as a pull acknowledgement submits it.
    """
    ack = new_fenced_ack(Input_Sub_Key, [msg_id], [expected_attempt])

    out = new_pending_atomic([publication.pending], ack, True)
    return out

# ################################################################################################################################

def _new_lease(now_ms:'int', max_messages:'int') -> 'PendingLease':
    """ Returns a lease of the messages of the input subscriber as of the given time.
    """
    lease_ms = get_lease_ms()
    leased_until_ms = now_ms + lease_ms

    out = new_pending_lease(Input_Sub_Key, max_messages, _lease_max_len, now_ms, leased_until_ms)
    return out

# ################################################################################################################################

def _write_batch(backend:'SQLPubSubBackend', batch:'anylist') -> 'None':
    """ Writes the items in one commit, as the commit queue writes the items of its concurrent callers.
    """
    backend._writer._write_transaction(backend.engine, batch)

# ################################################################################################################################

def _get_leased_attempts(pending:'PendingLease') -> 'strintdict':
    """ Returns the delivery attempt of each message that a lease of a batch handed out, by message ID.
    """
    out:'strintdict' = {}

    for row in pending.rows:
        out[row.msg_id] = pending.attempts[row.id]

    return out

# ################################################################################################################################

def _publish_inputs(backend:'SQLPubSubBackend', count:'int') -> 'strlist':
    """ Publishes the given number of input messages and returns their message IDs.
    """
    out:'strlist' = []

    for index in range(count):
        msg_id = publish_input(backend, f'input-{index}')
        out.append(msg_id)

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_conflict_isolated_in_batch_scenario() -> 'None':
    """ Of two acknowledgements with publications that share a commit with a plain publication, the one with an attempt
    that no lease handed out commits neither its publication nor its acknowledgement and alone receives the conflict,
    while the other one and the plain publication are committed.
    """
    backend = new_backend()
    first_msg_id, second_msg_id = _publish_inputs(backend, 2)

    now_ms = backend.clock.now_ms()
    attempts = lease(backend, now_ms)

    # The first acknowledgement holds the attempt of the lease and the second one does not ..
    committed_publication = build(backend, First_Output_Topic, 'committed')
    rejected_publication = build(backend, First_Output_Topic, 'rejected')
    plain_publication = build(backend, Second_Output_Topic, 'plain')

    committed = _new_atomic(first_msg_id, attempts[first_msg_id], committed_publication)
    rejected = _new_atomic(second_msg_id, _stale_attempt, rejected_publication)

    # .. all three share one commit, with the rejected acknowledgement first ..
    _write_batch(backend, [rejected, plain_publication.pending, committed])

    # .. the rejected acknowledgement alone receives the conflict ..
    assert isinstance(rejected.exception, PubSubAckConflict)
    assert committed.exception is None
    assert plain_publication.pending.exception is None

    # .. its message stays in the queue with the attempt of its lease and its publication is not written ..
    assert count_deliveries(Input_Sub_Key) == 1
    assert get_attempt(backend, second_msg_id) == attempts[second_msg_id]

    committed_msg_id = get_built_msg_id(committed_publication)
    assert get_msg_ids(First_Output_Topic) == [committed_msg_id]

    # .. and the plain publication reached its subscriber.
    plain_msg_id = get_built_msg_id(plain_publication)

    assert get_msg_ids(Second_Output_Topic) == [plain_msg_id]
    assert count_deliveries(Second_Output_Sub_Key) == 1

# ################################################################################################################################

def run_strict_duplicate_isolated_in_batch_scenario() -> 'None':
    """ Of two acknowledgements with publications in one commit, the one whose publication has the message ID
    of a different existing message commits neither its publication nor its acknowledgement and alone receives
    the duplicate message ID, while the other one is committed.
    """
    backend = new_backend()
    first_msg_id, second_msg_id = _publish_inputs(backend, 2)

    # A different message stands for the message ID already ..
    _ = backend.publish(First_Output_Topic, 'original', msg_id=_existing_msg_id)

    now_ms = backend.clock.now_ms()
    attempts = lease(backend, now_ms)

    # .. one acknowledgement publishes other content with it, and the other one publishes a new message ..
    committed_publication = build(backend, First_Output_Topic, 'committed')
    rejected_publication = build(backend, First_Output_Topic, 'different', msg_id=_existing_msg_id)

    committed = _new_atomic(first_msg_id, attempts[first_msg_id], committed_publication)
    rejected = _new_atomic(second_msg_id, attempts[second_msg_id], rejected_publication)

    # .. both share one commit ..
    _write_batch(backend, [rejected, committed])

    # .. the rejected acknowledgement alone receives the duplicate message ID ..
    assert isinstance(rejected.exception, PubSubDuplicateMsgID)
    assert committed.exception is None

    # .. its message stays in the queue ..
    assert count_deliveries(Input_Sub_Key) == 1
    assert get_attempt(backend, second_msg_id) == attempts[second_msg_id]

    # .. and the existing message is unchanged, followed by the publication of the committed acknowledgement alone.
    committed_msg_id = get_built_msg_id(committed_publication)
    assert get_msg_ids(First_Output_Topic) == [_existing_msg_id, committed_msg_id]

# ################################################################################################################################

def run_lease_after_ack_in_batch_scenario() -> 'None':
    """ A lease that shares a commit with an acknowledgement of the same subscriber does not hand out the message
    that the acknowledgement removed.
    """
    backend = new_backend()
    first_msg_id, second_msg_id = _publish_inputs(backend, 2)

    now_ms = backend.clock.now_ms()
    attempts = lease(backend, now_ms)

    # Both leases ran out, and the first message is acknowledged with the attempt of its lease ..
    lease_ms = get_lease_ms()
    later_ms = now_ms + lease_ms + 1

    publication = build(backend, First_Output_Topic, 'output')
    acknowledged = _new_atomic(first_msg_id, attempts[first_msg_id], publication)

    # .. in the same commit as a new lease, which is listed first ..
    pending_lease = _new_lease(later_ms, _shared_lease_max_messages)
    _write_batch(backend, [pending_lease, acknowledged])

    # .. so the acknowledgement is committed and the lease hands out the other message alone, with its next attempt.
    assert acknowledged.exception is None

    leased = _get_leased_attempts(pending_lease)
    second_attempt = attempts[second_msg_id] + 1

    assert leased == {second_msg_id: second_attempt}
    assert count_deliveries(Input_Sub_Key) == 1

# ################################################################################################################################

def run_two_leases_in_batch_scenario() -> 'None':
    """ Two leases of the same subscriber in one commit hand out no message twice.
    """
    backend = new_backend()
    msg_ids = _publish_inputs(backend, _shared_lease_message_count)

    now_ms = backend.clock.now_ms()

    first_lease = _new_lease(now_ms, _shared_lease_max_messages)
    second_lease = _new_lease(now_ms, _shared_lease_max_messages)

    _write_batch(backend, [first_lease, second_lease])

    first_leased = _get_leased_attempts(first_lease)
    second_leased = _get_leased_attempts(second_lease)

    # The first lease takes as many messages as it may, and the second one takes the rest ..
    assert len(first_leased) == _shared_lease_max_messages
    assert len(second_leased) == _shared_lease_message_count - _shared_lease_max_messages

    # .. so that each message is handed out once, with its first attempt.
    leased_msg_ids:'strlist' = []

    for leased in (first_leased, second_leased):
        for msg_id, attempt in leased.items():
            leased_msg_ids.append(msg_id)
            assert attempt == 1

    assert sorted(leased_msg_ids) == sorted(msg_ids)

# ################################################################################################################################
# ################################################################################################################################
