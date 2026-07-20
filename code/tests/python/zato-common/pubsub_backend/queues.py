# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from common import delete_all_rows, get_delivery_rows, get_message_rows
from zato.common.pubsub.sql.backend import SQLPubSubBackend
from zato.common.pubsub.sql.config import ModuleCtx as PubSubDBCtx

# ################################################################################################################################
# ################################################################################################################################

# The topics and subscribers all the queue-management assertions share.
_topic_1 = 'pubsub.backend.test.queues.1'
_topic_2 = 'pubsub.backend.test.queues.2'
_sub_key_1 = 'zpsk.test.queues.1'
_sub_key_2 = 'zpsk.test.queues.2'

# ################################################################################################################################
# ################################################################################################################################

def _run_subscription_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Subscriptions are per (subscriber, topic) pair, case-insensitive on the topic name,
    and listable from both directions.
    """
    delete_all_rows()

    # Topic names are normalized to lowercase no matter how they are spelled ..
    backend.subscribe(_sub_key_1, 'PubSub.Backend.Test.Queues.1')
    backend.subscribe(_sub_key_1, _topic_2)
    backend.subscribe(_sub_key_2, _topic_1)

    # .. so lookups in any spelling find them ..
    assert set(backend.get_subscribed_topics(_sub_key_1)) == {_topic_1, _topic_2}
    assert set(backend.get_topic_subscribers('PUBSUB.BACKEND.TEST.QUEUES.1')) == {_sub_key_1, _sub_key_2}

    # .. and unsubscribing removes exactly the one pair.
    backend.unsubscribe(_sub_key_1, _topic_2)

    assert backend.get_subscribed_topics(_sub_key_1) == [_topic_1]
    assert backend.get_subscribed_topics(_sub_key_2) == [_topic_1]

# ################################################################################################################################

def _run_unsubscribe_cleanup_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Unsubscribing cleans up the pair's pending deliveries and drops the payloads
    of messages no other subscriber needs anymore.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic_1)
    backend.subscribe(_sub_key_2, _topic_1)

    _ = backend.publish(_topic_1, 'message-1')
    _ = backend.publish(_topic_1, 'message-2')

    # The first subscriber leaves - its deliveries vanish but the payloads stay
    # because the second subscriber still needs them ..
    backend.unsubscribe(_sub_key_1, _topic_1)

    assert get_delivery_rows(_sub_key_1) == []
    assert len(get_delivery_rows(_sub_key_2)) == 2

    message_rows = get_message_rows(_topic_1)
    assert len(message_rows) == 2

    for row in message_rows:
        assert row.payload is not None

    # .. and once the second subscriber leaves too, the payloads are dropped.
    backend.unsubscribe(_sub_key_2, _topic_1)

    message_rows = get_message_rows(_topic_1)
    assert len(message_rows) == 2

    for row in message_rows:
        assert row.payload is None

# ################################################################################################################################

def _run_clear_queue_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Clearing a queue removes everything the subscriber has pending, across all its topics.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic_1)
    backend.subscribe(_sub_key_1, _topic_2)

    for index in range(3):
        _ = backend.publish(_topic_1, f'topic-1-message-{index}')

    for index in range(2):
        _ = backend.publish(_topic_2, f'topic-2-message-{index}')

    result = backend.clear_queue(_sub_key_1)

    assert result['cleared_count'] == 5
    assert backend.fetch_messages(_sub_key_1) == []

    # The subscriber was the only one, so all the payloads are gone as well.
    for topic_name in (_topic_1, _topic_2):
        for row in get_message_rows(topic_name):
            assert row.payload is None

    # Clearing an already empty queue is a no-op.
    result = backend.clear_queue(_sub_key_1)
    assert result['cleared_count'] == 0

# ################################################################################################################################

def _run_bounded_batches_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Bulk operations produce the same results when they have to run
    in many small batches instead of one statement.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic_1)

    for index in range(5):
        _ = backend.publish(_topic_1, f'batched-message-{index}')

    # A batch size smaller than the queue forces multiple rounds ..
    os.environ[PubSubDBCtx.Env_Batch_Size] = '2'

    try:
        result = backend.clear_queue(_sub_key_1)
    finally:
        del os.environ[PubSubDBCtx.Env_Batch_Size]

    # .. and the outcome is the same as with one big statement.
    assert result['cleared_count'] == 5
    assert backend.fetch_messages(_sub_key_1) == []

    for row in get_message_rows(_topic_1):
        assert row.payload is None

# ################################################################################################################################

def _run_audit_flags_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Topic audit flags are per-backend state - turning a topic's audit log off
    registers it, turning it back on or forgetting it unregisters it.
    """
    assert _topic_1 not in backend.audit_disabled_topics

    backend.set_topic_audit_flag(_topic_1, False)
    assert _topic_1 in backend.audit_disabled_topics

    backend.set_topic_audit_flag(_topic_1, True)
    assert _topic_1 not in backend.audit_disabled_topics

    backend.set_topic_audit_flag(_topic_1, False)
    backend.delete_topic_audit_flag(_topic_1)
    assert _topic_1 not in backend.audit_disabled_topics

# ################################################################################################################################

def _run_message_details_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Single messages can be looked up in full and deleted per subscriber,
    with the row disappearing entirely once no subscriber needs it.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic_1)
    backend.subscribe(_sub_key_2, _topic_1)

    result = backend.publish(_topic_1, 'message-to-inspect', correl_id='correlation-details-1')

    # The details include the payload and the optional metadata ..
    details = backend.get_message_details(_topic_1, result.msg_id)

    assert details is not None
    assert details['msg_id'] == result.msg_id
    assert details['data'] == 'message-to-inspect'
    assert details['correl_id'] == 'correlation-details-1'

    # .. a lookup of something that does not exist returns None ..
    assert backend.get_message_details(_topic_1, 'zpsm.no-such-message') is None

    # .. deleting for one subscriber keeps the row because the other still needs it ..
    was_removed = backend.delete_message(_sub_key_1, _topic_1, result.msg_id)

    assert was_removed is False
    assert backend.get_message_details(_topic_1, result.msg_id) is not None

    # .. and deleting for the last subscriber removes the row entirely, trace included.
    was_removed = backend.delete_message(_sub_key_2, _topic_1, result.msg_id)

    assert was_removed is True
    assert backend.get_message_details(_topic_1, result.msg_id) is None
    assert get_message_rows(_topic_1) == []

# ################################################################################################################################

def _run_topic_operations_flow(backend:'SQLPubSubBackend') -> 'None':
    """ Renaming a topic carries its messages, deliveries and subscriptions over,
    and deleting a topic removes all three.
    """
    delete_all_rows()

    backend.subscribe(_sub_key_1, _topic_1)

    _ = backend.publish(_topic_1, 'message-before-rename-1')
    _ = backend.publish(_topic_1, 'message-before-rename-2')

    # Only topics with any message rows are reported as holding data ..
    assert backend.get_topics_with_messages() == [_topic_1]

    # .. the rename moves everything over to the new name ..
    renamed_topic = 'pubsub.backend.test.queues.renamed'
    backend.rename_topic(_topic_1, renamed_topic)

    assert get_message_rows(_topic_1) == []
    assert len(get_message_rows(renamed_topic)) == 2

    assert backend.get_topic_subscribers(_topic_1) == []
    assert backend.get_topic_subscribers(renamed_topic) == [_sub_key_1]
    assert backend.get_subscribed_topics(_sub_key_1) == [renamed_topic]

    # .. the pending messages are still deliverable after the rename ..
    messages = backend.fetch_messages(_sub_key_1)

    assert len(messages) == 2
    assert messages[0]['topic_name'] == renamed_topic

    # .. and deleting the topic removes its messages, deliveries and subscriptions.
    backend.delete_topic(renamed_topic)

    assert get_message_rows(renamed_topic) == []
    assert get_delivery_rows(_sub_key_1) == []
    assert backend.get_subscribed_topics(_sub_key_1) == []
    assert backend.fetch_messages(_sub_key_1) == []

# ################################################################################################################################

def run_queues_scenario() -> 'None':
    """ Queue management every backend must support - subscriptions, unsubscribe cleanup,
    queue clearing, single-message operations and whole-topic operations.
    """
    backend = SQLPubSubBackend()

    _run_subscription_flow(backend)
    _run_unsubscribe_cleanup_flow(backend)
    _run_clear_queue_flow(backend)
    _run_bounded_batches_flow(backend)
    _run_message_details_flow(backend)
    _run_topic_operations_flow(backend)
    _run_audit_flags_flow(backend)

# ################################################################################################################################
# ################################################################################################################################
