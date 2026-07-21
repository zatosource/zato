# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time

# Zato
from zato.common.test import pubsub_db

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_ack_atomicity')

_topic_shared = 'ack.test.shared'
_topic_sole   = 'ack.test.sole'

_settle_time = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _get_sub_key(admin_client:'any_', username:'str') -> 'str':
    """ Looks up the sub_key for a given security username via the admin API.
    """
    result = admin_client.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    # .. the response may be a list or a single dict ..
    if isinstance(result, list):
        items:'anylist' = result
    else:
        items = result['zato_pubsub_subscription_get_list_response']

    for item in items:
        sec_name = item['sec_name']
        if sec_name == username:
            return item['sub_key']

    raise Exception(f'No subscription found for username: {username}')

# ################################################################################################################################
# ################################################################################################################################

def _get_sub_id(admin_client:'any_', username:'str') -> 'int':
    """ Looks up the subscription ID for a given security username via the admin API.
    """
    result = admin_client.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    # .. the response may be a list or a single dict ..
    if isinstance(result, list):
        items:'anylist' = result
    else:
        items = result['zato_pubsub_subscription_get_list_response']

    for item in items:
        sec_name = item['sec_name']
        if sec_name == username:
            return item['id']

    raise Exception(f'No subscription found for username: {username}')

# ################################################################################################################################
# ################################################################################################################################

def _publish_messages(publish_client:'any_', topic_name:'str', count:'int') -> 'strlist':
    """ Publishes `count` messages to the given topic and returns their msg_ids.
    """
    msg_ids:'strlist' = []

    for idx in range(count):
        result = publish_client.publish(topic_name, f'ack-atomicity-payload-{idx}')
        msg_id = result['msg_id']
        msg_ids.append(msg_id)

    return msg_ids

# ################################################################################################################################
# ################################################################################################################################

def _clear_all_queues(admin:'any_') -> 'None':
    """ Clears all subscriber queues to ensure test isolation.
    """
    from zato.common.test.config_pubsub_ack_atomicity import TestConfig

    sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)
    sub_key_b = _get_sub_key(admin, TestConfig.puller_b_username)

    _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})
    _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_b})

    time.sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################
#
# Gap: concurrent acks for the same message by different subscribers
#
# Publish 1 message to a topic with 2 subscribers. Both pull (which acks).
# Verify: nothing pending, the payload dropped, no errors.
#
# ################################################################################################################################
# ################################################################################################################################

class TestConcurrentAckTwoSubscribers:

    def test_concurrent_ack_two_subscribers(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_ack_atomicity import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller_a = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)
        puller_b = PullClient(TestConfig.base_url, TestConfig.puller_b_username, TestConfig.puller_b_password)

        # .. ensure all queues are empty ..
        _clear_all_queues(admin)

        sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)
        sub_key_b = _get_sub_key(admin, TestConfig.puller_b_username)

        # .. publish 1 message to the shared topic ..
        msg_ids = _publish_messages(publisher, _topic_shared, 1)
        time.sleep(_settle_time)

        # .. both subscribers pull (and ack) ..
        result_a = puller_a.pull(max_messages=50)
        result_b = puller_b.pull(max_messages=50)

        # .. puller_a is subscribed to both topics, only 1 was published to shared ..
        assert result_a['message_count'] >= 1
        assert result_b['message_count'] == 1

        # .. let the payload cleanup complete ..
        time.sleep(_settle_time)

        # .. verify the payload was dropped once both subscribers acked ..
        assert pubsub_db.count_messages_with_payload(msg_ids) == 0

        # .. verify both queues report empty.
        browse_a = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_a,
            'state': 'pending',
        })

        browse_b = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_b,
            'state': 'pending',
        })

        assert browse_a['total'] == 0
        assert browse_b['total'] == 0

# ################################################################################################################################
# ################################################################################################################################
#
# Gap: Double ack for the same (message, sub_key) pair
#
# Publish 1 message, pull it, then pull again (second pull sees empty).
# Verify: no error, nothing pending, payload gone.
#
# ################################################################################################################################
# ################################################################################################################################

class TestDoublePullSameSubscriber:

    def test_double_pull_same_subscriber(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_ack_atomicity import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller_a = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)

        # .. ensure all queues are empty ..
        _clear_all_queues(admin)

        sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. publish 1 message to the sole topic ..
        msg_ids = _publish_messages(publisher, _topic_sole, 1)
        time.sleep(_settle_time)

        # .. first pull delivers and acks ..
        result_first = puller_a.pull(max_messages=50)
        assert result_first['message_count'] == 1

        # .. let the payload cleanup complete ..
        time.sleep(_settle_time)

        # .. second pull should see nothing, no error ..
        result_second = puller_a.pull(max_messages=50)
        assert result_second['message_count'] == 0

        # .. verify the payload is gone ..
        assert pubsub_db.count_messages_with_payload(msg_ids) == 0

        # .. verify pending is empty.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_a,
            'state': 'pending',
        })

        assert browse_result['total'] == 0

# ################################################################################################################################
# ################################################################################################################################
#
# Gap: ack interleaves with clear_queue
#
# Publish 5 messages to a topic with 1 subscriber. Pull 2 (acks them).
# Immediately clear_queue. Verify: queue empty, browse pending=0, all payloads gone.
#
# ################################################################################################################################
# ################################################################################################################################

class TestAckDuringClearQueue:

    def test_ack_during_clear_queue(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_ack_atomicity import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller_a = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)

        # .. ensure all queues are empty ..
        _clear_all_queues(admin)

        sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. publish 5 messages to the sole topic ..
        msg_ids = _publish_messages(publisher, _topic_sole, 5)
        time.sleep(_settle_time)

        # .. pull 2 (acks them) ..
        _ = puller_a.pull(max_messages=2)

        # .. clear the remaining queue ..
        clear_result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})
        logger.info('Clear result: %s', clear_result)

        # .. let the payload cleanup complete ..
        time.sleep(_settle_time)

        # .. verify pending is empty ..
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_a,
            'state': 'pending',
        })

        assert browse_result['total'] == 0

        # .. verify all the payloads are gone.
        with_payload = pubsub_db.count_messages_with_payload(msg_ids)
        assert with_payload == 0

# ################################################################################################################################
# ################################################################################################################################
#
# Gap: Cleanup correctness after atomic ack with multiple subscribers
#
# Publish 3 messages to shared topic. Sub A pulls all 3 (acks).
# Verify: sub B still has 3 pending, the payloads still exist, B can pull them.
#
# ################################################################################################################################
# ################################################################################################################################

class TestMultiSubAckPreservesOther:

    def test_multi_sub_ack_preserves_other(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_ack_atomicity import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller_a = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)
        puller_b = PullClient(TestConfig.base_url, TestConfig.puller_b_username, TestConfig.puller_b_password)

        # .. ensure all queues are empty ..
        _clear_all_queues(admin)

        sub_key_b = _get_sub_key(admin, TestConfig.puller_b_username)

        # .. publish 3 messages to the shared topic ..
        msg_ids = _publish_messages(publisher, _topic_shared, 3)
        time.sleep(_settle_time)

        # .. sub A pulls all (acks them) - may also get messages from sole topic ..
        result_a = puller_a.pull(max_messages=50)
        assert result_a['message_count'] >= 3

        # .. sub B should still have 3 pending ..
        browse_b = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_b,
            'state': 'pending',
        })

        assert browse_b['total'] == 3

        # .. the payloads must still exist because B has not acked ..
        with_payload = pubsub_db.count_messages_with_payload(msg_ids)
        assert with_payload == 3

        # .. B can pull them all.
        result_b = puller_b.pull(max_messages=50)
        assert result_b['message_count'] == 3

# ################################################################################################################################
# ################################################################################################################################
#
# Gap: the payload survives until the last subscriber acks
#
# Publish 1 message to shared topic (2 subs). Sub A pulls (acks).
# Verify the payload still exists. Sub B pulls (acks). Verify the payload is gone.
#
# ################################################################################################################################
# ################################################################################################################################

class TestPayloadLifetime:

    def test_payload_lifetime(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_ack_atomicity import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller_a = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)
        puller_b = PullClient(TestConfig.base_url, TestConfig.puller_b_username, TestConfig.puller_b_password)

        # .. ensure all queues are empty ..
        _clear_all_queues(admin)

        # .. publish 1 message to the shared topic ..
        msg_ids = _publish_messages(publisher, _topic_shared, 1)
        time.sleep(_settle_time)

        # .. sub A pulls (acks) - may also get messages from sole topic ..
        result_a = puller_a.pull(max_messages=50)
        assert result_a['message_count'] >= 1

        # .. the payload must still exist because B has not acked ..
        with_payload_after_a = pubsub_db.count_messages_with_payload(msg_ids)
        assert with_payload_after_a == 1

        # .. sub B pulls (acks the last subscriber) ..
        result_b = puller_b.pull(max_messages=50)
        assert result_b['message_count'] == 1

        # .. let the payload cleanup complete ..
        time.sleep(_settle_time)

        # .. now the payload must be gone.
        with_payload_after_b = pubsub_db.count_messages_with_payload(msg_ids)
        assert with_payload_after_b == 0

# ################################################################################################################################
# ################################################################################################################################
#
# Gap: ack interleaves with unsubscribe
#
# Publish 3 messages, pull 1 (ack it), then unsubscribe.
# Verify: nothing stays pending, the sole-subscriber payloads are dropped.
# This test must run last because it deletes and re-creates puller_a's subscription.
#
# ################################################################################################################################
# ################################################################################################################################

class TestZZ_AckDuringUnsubscribe:

    def test_ack_during_unsubscribe(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_ack_atomicity import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller_a = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)

        # .. ensure all queues are empty ..
        _clear_all_queues(admin)

        # .. publish 3 messages to the sole topic ..
        msg_ids = _publish_messages(publisher, _topic_sole, 3)
        time.sleep(_settle_time)

        # .. pull 1 (acks it) ..
        result = puller_a.pull(max_messages=1)
        assert result['message_count'] >= 1

        # .. look up the subscription ID and delete it ..
        sub_id = _get_sub_id(admin, TestConfig.puller_a_username)

        try:
            _ = admin.invoke('zato.pubsub.subscription.delete', {'id': sub_id})

            # .. let cleanup complete ..
            time.sleep(_settle_time)

            # .. verify the sole topic's payloads are gone ..
            with_payload = pubsub_db.count_messages_with_payload(msg_ids)
            assert with_payload == 0

        finally:
            # .. re-create the subscription so the environment stays consistent.
            _ = admin.invoke('zato.pubsub.subscription.create', {
                'cluster_id': 1,
                'topic_name_list': [_topic_sole, _topic_shared],
                'sec_base_id': TestConfig.puller_a_sec_base_id,
                'delivery_type': 'pull',
            })

# ################################################################################################################################
# ################################################################################################################################
