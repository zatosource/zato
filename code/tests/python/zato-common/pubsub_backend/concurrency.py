# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# gevent
import gevent
from gevent.event import Event

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from common import delete_all_rows, get_delivery_rows, get_message_rows, write_in_one_commit
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import ModuleCtx
from zato.common.test.audit_log_ import new_test_audit_log
from zato.common.pubsub.sql.pending import new_pending_ack
from zato.common.pubsub.sql.errors import PubSubTopicUnavailable
from zato.common.pubsub.sql.publication import build_publication
from zato.common.pubsub.sql.writes import PubSubDuplicateMsgID, PubSubWriter
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.audit_log.api import AuditLog
    from zato.common.pubsub.sql.backend import PublishResult
    from zato.common.typing_ import any_, anydict, anylist, callable_, intlist, strlist
    from zato_common_core.zato_common_core import SubscriptionList

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

# The topic and subscriber of the concurrent-clear assertion.
_clear_topic = 'pubsub.backend.test.concurrency.clear'
_clear_sub_key = 'zpsk.test.concurrency.clear'

Env_Commits_In_Flight = ModuleCtx.Env_Commits_In_Flight

# How many pending messages the cleared queue holds before the clear starts.
_clear_backlog = 200

# How many commits may be in progress at once in the flow of disjoint acknowledgements.
_single_commit_in_flight = '1'

# The message that the held acknowledgement of that flow is about, which no subscriber has.
_missing_msg_id = 'zpsm.test.concurrency.missing'

# How many message IDs the two overlapping commits share, and the prefix of the IDs
_overlap_count = 50
_overlap_msg_id_prefix = 'zpsm.test.concurrency.overlap'

# How many commits the two overlapping commits are written in when neither is rolled back and run again
_overlap_commit_count = 2

# How many messages the topic of the delete and rename flows holds before the change begins
_change_published_count = 20

# The name the rename flow gives the topic
_renamed_topic = 'pubsub.backend.test.concurrency.renamed'

# How often and how many times the delete and rename flows check that the held commit is waiting
_hold_wait_interval = 0.05
_hold_wait_attempts = 200

# ################################################################################################################################
# ################################################################################################################################

class _RecordingWriter(PubSubWriter):
    """ A writer that records how many items each of its transactions held.
    """

    def __init__(self, audit_log:'AuditLog', subscription_list:'SubscriptionList') -> 'None':
        super().__init__(audit_log, subscription_list)
        self.transaction_sizes:'intlist' = []

        # When set, the next commit waits for this event before it writes anything
        self.hold_event:'Event | None' = None

    def _write_batch(self, batch:'anylist') -> 'None':

        # A commit that is held keeps the lane busy, so the items that arrive in the meantime wait for the next one ..
        if self.hold_event is not None:
            hold_event = self.hold_event
            self.hold_event = None
            _ = hold_event.wait()

        # .. which writes all of them.
        super()._write_batch(batch)

    def _write_transaction(self, engine:'Engine', batch:'anylist') -> 'anylist':
        self.transaction_sizes.append(len(batch))
        out = super()._write_transaction(engine, batch)
        return out

# ################################################################################################################################
# ################################################################################################################################

def _new_backend() -> 'tuple[SQLPubSubBackend, _RecordingWriter]':
    """ Returns a backend whose writes are recorded, subscribed to the shared topic by both subscribers.
    """
    delete_all_rows()

    audit_log = new_test_audit_log()
    backend = SQLPubSubBackend(audit_log=audit_log)

    writer = _RecordingWriter(audit_log, backend.subscription_list)
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

def _publish_duplicate(backend:'SQLPubSubBackend', msg_id:'str', data:'str') -> 'str':
    """ Publishes a message under a given identifier and tells whether it was stored or rejected.
    """
    try:
        _ = backend.publish(_topic, data, msg_id=msg_id)
    except PubSubDuplicateMsgID:
        out = 'rejected'
    else:
        out = 'stored'

    return out

# ################################################################################################################################

def _run_duplicate_flow() -> 'None':
    """ A different message under an identifier that exists already fails its own publisher alone,
    the same message under it is a repeated publication that succeeds with no new deliveries,
    and the others in its commit succeed.
    """
    backend, _ignored = _new_backend()

    existing_msg_id = 'zpsm.test.concurrency.duplicate'
    original_data = 'original-message'
    _ = backend.publish(_topic, original_data, msg_id=existing_msg_id)

    greenlets:'anylist' = []

    for index in range(_caller_count):

        # Every tenth caller reuses the identifier with different content, every fifth with the same content.
        if index % 10 == 0:
            msg_id = existing_msg_id
            data = 'different-message'
        elif index % 5 == 0:
            msg_id = existing_msg_id
            data = original_data
        else:
            msg_id = f'zpsm.test.concurrency.unique.{index}'
            data = 'unique-message'

        greenlet = gevent.spawn(_publish_duplicate, backend, msg_id, data)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    unique_count = 0

    for index, greenlet in enumerate(greenlets):

        outcome = greenlet.value

        if index % 10 == 0:
            assert outcome == 'rejected', index
        elif index % 5 == 0:
            assert outcome == 'stored', index
        else:
            assert outcome == 'stored', index
            unique_count += 1

    # The original and every unique message are stored once each, with one delivery row each.
    message_rows = get_message_rows(_topic)
    assert len(message_rows) == unique_count + 1

    delivery_rows = get_delivery_rows(_sub_key_1)
    assert len(delivery_rows) == unique_count + 1

# ################################################################################################################################

def _publish_or_fail(backend:'SQLPubSubBackend', data:'str') -> 'str':
    """ Publishes a message and tells whether it was stored or failed.
    """
    try:
        _ = backend.publish(_topic, data)
    except DBAPIError:
        out = 'failed'
    else:
        out = 'stored'

    return out

# ################################################################################################################################

def _run_rejected_value_flow() -> 'None':
    """ A payload that PostgreSQL cannot store fails its own publisher alone, and the other publications
    of its commit are stored.
    """
    backend, writer = _new_backend()

    greenlets:'anylist' = []

    for index in range(_caller_count):

        # One caller publishes a NUL character, which a text column of PostgreSQL rejects.
        if index == _caller_count // 2:
            data = 'rejected\x00message'
        else:
            data = f'accepted-message-{index}'

        greenlet = gevent.spawn(_publish_or_fail, backend, data)
        greenlets.append(greenlet)

    _ = gevent.joinall(greenlets, raise_error=True)

    outcomes:'strlist' = []

    for greenlet in greenlets:
        outcomes.append(greenlet.value)

    assert outcomes.count('failed') == 1, outcomes
    assert outcomes[_caller_count // 2] == 'failed'

    # Every stored publication has its message and its delivery rows ..
    stored_count = _caller_count - 1

    assert len(get_message_rows(_topic)) == stored_count
    assert len(get_delivery_rows(_sub_key_1)) == stored_count
    assert len(get_delivery_rows(_sub_key_2)) == stored_count

    # .. and the publications shared their commits.
    assert max(writer.transaction_sizes) > 1, writer.transaction_sizes

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

def _run_disjoint_ack_flow() -> 'None':
    """ One commit with the acknowledgements of two subscribers, each about a different message,
    removes only the two delivery rows they are about.
    """
    # A single commit in progress at a time, on each database, is what makes the acknowledgements wait together ..
    os.environ[Env_Commits_In_Flight] = _single_commit_in_flight

    try:
        backend, writer = _new_backend()
    finally:
        del os.environ[Env_Commits_In_Flight]

    first = backend.publish(_topic, 'disjoint-message-1')
    second = backend.publish(_topic, 'disjoint-message-2')

    # .. while a commit of an acknowledgement of a message that does not exist is held in progress ..
    hold_event = Event()
    writer.hold_event = hold_event

    held_ack = new_pending_ack(_sub_key_1, [_missing_msg_id], None)
    held_greenlet = gevent.spawn(writer.ack, held_ack)
    gevent.sleep(0)

    # .. each subscriber acknowledges a different message, and both wait for the next commit ..
    first_ack = new_pending_ack(_sub_key_1, [first.msg_id], None)
    second_ack = new_pending_ack(_sub_key_2, [second.msg_id], None)

    first_greenlet = gevent.spawn(writer.ack, first_ack)
    second_greenlet = gevent.spawn(writer.ack, second_ack)
    gevent.sleep(0)

    writer.transaction_sizes.clear()
    hold_event.set()

    _ = gevent.joinall([held_greenlet, first_greenlet, second_greenlet], raise_error=True)

    # .. which writes both of them ..
    assert writer.transaction_sizes == [1, 2], writer.transaction_sizes

    # .. each acknowledgement removed its own row alone ..
    assert first_ack.removed_count == 1
    assert second_ack.removed_count == 1

    # .. the other message of each subscriber is still in its queue ..
    first_remaining = get_delivery_rows(_sub_key_1)
    second_remaining = get_delivery_rows(_sub_key_2)

    assert len(first_remaining) == 1
    assert len(second_remaining) == 1

    message_ids_by_msg_id:'anydict' = {}

    for row in get_message_rows(_topic):
        message_ids_by_msg_id[row.msg_id] = row.id

    assert first_remaining[0].message_id == message_ids_by_msg_id[second.msg_id]
    assert second_remaining[0].message_id == message_ids_by_msg_id[first.msg_id]

    # .. so neither message is fully delivered and both keep their payloads.
    assert first_ack.fully_delivered_count == 0
    assert second_ack.fully_delivered_count == 0

    for row in get_message_rows(_topic):
        assert row.payload is not None

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

def _run_concurrent_clear_flow() -> 'None':
    """ A clear of a queue with a backlog removes every delivery row of the queue and reports how many it removed.
    """
    delete_all_rows()

    backend = SQLPubSubBackend(audit_log=new_test_audit_log())
    backend.subscribe(_clear_sub_key, _clear_topic)

    # A backlog to clear, published through the writer ..
    for index in range(_clear_backlog):
        _ = backend.publish(_clear_topic, f'clear-seed-{index}')

    assert len(get_delivery_rows(_clear_sub_key)) == _clear_backlog

    # .. which the clear removes as a whole.
    cleared = backend.clear_queue(_clear_sub_key)

    assert cleared['cleared_count'] == _clear_backlog
    assert get_delivery_rows(_clear_sub_key) == []

# ################################################################################################################################

def _run_overlapping_batches_flow() -> 'None':
    """ Two concurrent commits that publish the same message IDs in opposite orders write the dedup records
    in the order of their keys, so neither waits for a lock that the other waits for. Both commit on their first attempt,
    each message is stored once, and the commit that follows the other repeats each of its messages.
    """
    backend, writer = _new_backend()

    msg_ids:'strlist' = []

    for index in range(_overlap_count):
        msg_ids.append(f'{_overlap_msg_id_prefix}.{index}')

    forward:'anylist' = []
    backward:'anylist' = []

    for msg_id in msg_ids:
        built = build_publication(backend, _topic, f'overlap-message-{msg_id}', msg_id=msg_id)
        forward.append(built.pending)

    for msg_id in reversed(msg_ids):
        built = build_publication(backend, _topic, f'overlap-message-{msg_id}', msg_id=msg_id)
        backward.append(built.pending)

    greenlets = [
        gevent.spawn(write_in_one_commit, backend, forward),
        gevent.spawn(write_in_one_commit, backend, backward),
    ]
    _ = gevent.joinall(greenlets, raise_error=True)

    # Neither commit was rolled back on a deadlock and run again ..
    assert len(writer.transaction_sizes) == _overlap_commit_count, writer.transaction_sizes

    # .. each message is stored once with one delivery row per subscriber ..
    assert len(get_message_rows(_topic)) == _overlap_count
    assert len(get_delivery_rows(_sub_key_1)) == _overlap_count
    assert len(get_delivery_rows(_sub_key_2)) == _overlap_count

    # .. and each publication of the commit that followed is a repeat.
    repeat_count = 0

    for pending in forward + backward:
        assert pending.exception is None
        if pending.is_repeat:
            repeat_count += 1

    assert repeat_count == _overlap_count

# ################################################################################################################################

def _wait_until_held(writer:'_RecordingWriter') -> 'None':
    """ Returns once the commit that the writer was told to hold is waiting.
    """
    for _ in range(_hold_wait_attempts):
        if writer.hold_event is None:
            return
        gevent.sleep(_hold_wait_interval)

    raise Exception('The commit was not held')

# ################################################################################################################################

def _change_topic_while_publishing(backend:'SQLPubSubBackend', writer:'_RecordingWriter', change:'callable_',
    *args:'any_') -> 'None':
    """ Runs a change of the topic's rows while a publication accepted before it has its commit held, and checks that
    the change waits for that publication and refuses the publications that arrive while it runs.
    """
    _ = _publish_concurrently(backend, _change_published_count)

    # A publication is accepted and its commit is held ..
    hold_event = Event()
    writer.hold_event = hold_event

    held_publisher = gevent.spawn(backend.publish, _topic, 'held-message')
    _wait_until_held(writer)

    # .. so the change waits for it ..
    changer = gevent.spawn(change, *args)
    gevent.sleep(_hold_wait_interval)

    assert not changer.ready()

    # .. and a publication that arrives meanwhile is refused ..
    try:
        _ = backend.publish(_topic, 'refused-message')
    except PubSubTopicUnavailable:
        pass
    else:
        raise Exception('A publication to a topic being changed was accepted')

    # .. until the held publication commits and the change completes.
    _ = hold_event.set()
    _ = gevent.joinall([held_publisher, changer], raise_error=True)

# ################################################################################################################################

def _run_concurrent_topic_delete_flow() -> 'None':
    """ A topic delete waits until the publications accepted before it are committed, deletes their rows with all the others,
    refuses the publications that arrive while it runs, and accepts the publications that arrive after it.
    """
    backend, writer = _new_backend()

    _change_topic_while_publishing(backend, writer, backend.delete_topic, _topic)

    # No rows of the topic remain, including those of the held publication ..
    assert get_message_rows(_topic) == []
    assert get_delivery_rows(_sub_key_1) == []
    assert get_delivery_rows(_sub_key_2) == []

    # .. after which the topic accepts publications again.
    _ = backend.publish(_topic, 'message-after-delete')
    assert len(get_message_rows(_topic)) == 1

# ################################################################################################################################

def _run_concurrent_topic_rename_flow() -> 'None':
    """ A topic rename waits until the publications accepted before it under the old name are committed, moves their rows
    to the new name with all the others, refuses the publications under the old name that arrive while it runs,
    and accepts the publications under the old name that arrive after it.
    """
    backend, writer = _new_backend()

    _change_topic_while_publishing(backend, writer, backend.rename_topic, _topic, _renamed_topic)

    # Each message is under the new name, including that of the held publication ..
    renamed_count = _change_published_count + 1

    assert get_message_rows(_topic) == []
    assert len(get_message_rows(_renamed_topic)) == renamed_count

    # .. with the deliveries of both subscribers under that name too ..
    for sub_key in (_sub_key_1, _sub_key_2):

        delivery_rows = get_delivery_rows(sub_key)
        assert len(delivery_rows) == renamed_count

        for row in delivery_rows:
            assert row.topic_name == _renamed_topic

    # .. after which the old name accepts publications again.
    _ = backend.publish(_topic, 'message-after-rename')
    assert len(get_message_rows(_topic)) == 1

# ################################################################################################################################

def run_concurrency_scenario() -> 'None':
    """ Concurrent publications and acknowledgements, written in shared commits.
    """
    _run_concurrent_publish_flow()
    _run_duplicate_flow()
    _run_overlapping_batches_flow()
    _run_rejected_value_flow()
    _run_concurrent_ack_flow()
    _run_disjoint_ack_flow()
    _run_concurrent_claim_flow()
    _run_concurrent_clear_flow()
    _run_concurrent_topic_delete_flow()
    _run_concurrent_topic_rename_flow()

# ################################################################################################################################
# ################################################################################################################################
