# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import threading
import time

# Zato
from zato.common.test import pubsub_db

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_unsub_atomic')

_settle_time = 0.5

_topic_concurrent = 'unsub.atomic.concurrent'
_topic_burst      = 'unsub.atomic.burst'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _get_subscriptions(admin:'any_', sec_name:'str') -> 'anylist':
    """ Returns all subscriptions for a given security definition name.
    """
    sub_list = admin.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(sub_list, list):
        items:'anylist' = sub_list
    else:
        items = sub_list['zato_pubsub_subscription_get_list_response']

    out:'anylist' = []

    for item in items:
        if item['sec_name'] == sec_name:
            out.append(item)

    return out

# ################################################################################################################################

def _get_sub_key(admin:'any_', topic_name:'str') -> 'str':
    """ Returns the sub_key for the test subscriber on the given topic.
    """
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    subscriptions = _get_subscriptions(admin, TestConfig.subscriber_username)

    for subscription in subscriptions:
        topic_name_list = subscription['topic_name_list']

        for topic_entry in topic_name_list:
            if topic_entry['topic_name'] == topic_name:

                out = subscription['sub_key']
                return out

    raise Exception(f'No subscription found for topic: {topic_name}')

# ################################################################################################################################

def _get_sub_id(admin:'any_', topic_name:'str') -> 'int':
    """ Returns the subscription ID for the test subscriber on the given topic.
    """
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    subscriptions = _get_subscriptions(admin, TestConfig.subscriber_username)

    for subscription in subscriptions:
        topic_name_list = subscription['topic_name_list']

        for topic_entry in topic_name_list:
            if topic_entry['topic_name'] == topic_name:

                out = subscription['id']
                return out

    raise Exception(f'No subscription found for topic: {topic_name}')

# ################################################################################################################################

def _recreate_subscription(admin:'any_', topic_name:'str') -> 'None':
    """ Re-creates the subscription for the test subscriber on the given topic.
    """
    from zato.common.test.config_pubsub_unsub_atomic import TestConfig

    _ = admin.invoke('zato.pubsub.subscription.create', {
        'cluster_id': 1,
        'topic_name_list': [topic_name],
        'sec_base_id': TestConfig.subscriber_sec_base_id,
        'delivery_type': 'pull',
    })

# ################################################################################################################################
# ################################################################################################################################

class TestNoStalePendingAfterConcurrentPublishAndUnsub:
    """ Proves the primary race is closed: concurrent publish + unsubscribe
    cannot leave stale delivery rows behind.

    Gap: between removing the subscription row and cleaning up the pending
    deliveries, a publish could read the subscriber list before the removal
    and add a delivery row the cleanup then misses. After fix, unsubscribe
    removes the subscription row first, then sweeps the delivery rows.
    """

    def test_01_no_stale_pending_after_concurrent_publish_and_unsub(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        sub_key = _get_sub_key(admin, _topic_concurrent)
        sub_id = _get_sub_id(admin, _topic_concurrent)

        # .. publish messages from a background thread while the main thread unsubscribes ..
        publish_count = 5

        def _publish_loop() -> 'None':
            for _ in range(publish_count):
                try:
                    _ = publisher.publish(_topic_concurrent, 'race-test-payload')
                except Exception:
                    pass

        publish_thread = threading.Thread(target=_publish_loop)
        publish_thread.start()

        # .. delete the subscription (triggers unsubscribe internally) ..
        try:
            _ = admin.invoke('zato.pubsub.subscription.delete', {'id': sub_id})
        except Exception as error:
            logger.warning('subscription.delete raised: %s', error)

        publish_thread.join()
        time.sleep(_settle_time)

        # .. after unsubscribe, no delivery rows may remain for the sub_key ..
        pending_count = pubsub_db.count_pending(sub_key)

        assert pending_count == 0, \
            f'Stale delivery rows found for sub_key after unsub: {pending_count}'

        # .. and the subscription state must be gone too ..
        assert pubsub_db.get_subscribed_topics(sub_key) == [], \
            f'Subscription state still exists after unsub: {sub_key}'

        # .. re-create the subscription for test isolation.
        _recreate_subscription(admin, _topic_concurrent)
        time.sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################

class TestUnsubDuringBurstPublish:
    """ Burst variant: 10 rapid publishes concurrent with unsub.
    After unsub completes, no delivery rows remain for the sub_key.

    Gap: same as test_01 but with higher message volume to increase
    the probability of interleaving under the old non-atomic code.
    """

    def test_02_unsub_during_burst_publish(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        sub_key = _get_sub_key(admin, _topic_burst)
        sub_id = _get_sub_id(admin, _topic_burst)

        # .. publish 10 messages in rapid succession from a background thread ..
        publish_count = 10

        def _publish_loop() -> 'None':
            for _ in range(publish_count):
                try:
                    _ = publisher.publish(_topic_burst, 'burst-race-payload')
                except Exception:
                    pass

        publish_thread = threading.Thread(target=_publish_loop)
        publish_thread.start()

        # .. delete the subscription mid-burst ..
        try:
            _ = admin.invoke('zato.pubsub.subscription.delete', {'id': sub_id})
        except Exception as error:
            logger.warning('subscription.delete raised: %s', error)

        publish_thread.join()
        time.sleep(_settle_time)

        # .. no delivery rows may remain for the sub_key ..
        pending_count = pubsub_db.count_pending(sub_key)

        assert pending_count == 0, \
            f'Stale delivery rows found after burst unsub: {pending_count}'

        # .. and the subscription state must be gone too ..
        assert pubsub_db.get_subscribed_topics(sub_key) == [], \
            f'Subscription state still exists after burst unsub: {sub_key}'

        # .. re-create the subscription for test isolation.
        _recreate_subscription(admin, _topic_burst)
        time.sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadsDroppedAfterUnsub:
    """ Functional consequence: publish a message to a 1-subscriber topic,
    unsubscribe immediately, verify the payload is dropped from the message row.

    Gap: if a stale delivery row were left behind, the payload would never
    be dropped because the pending count would never reach zero. This test
    proves that after the atomic fix, payload cleanup proceeds correctly.
    """

    def test_03_payloads_dropped_after_unsub(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        sub_id = _get_sub_id(admin, _topic_concurrent)

        # .. publish 1 message so its payload is retained for the subscriber ..
        result = publisher.publish(_topic_concurrent, 'payload-cleanup-race-payload')
        msg_id = result['msg_id']
        time.sleep(_settle_time)

        # .. delete the subscription (triggers unsubscribe + payload cleanup) ..
        _ = admin.invoke('zato.pubsub.subscription.delete', {'id': sub_id})
        time.sleep(_settle_time)

        # .. verify the payload was dropped from the message row ..
        with_payload = pubsub_db.count_messages_with_payload([msg_id])

        assert with_payload == 0, \
            f'Expected the payload of {msg_id} to be dropped after unsub'

        # .. re-create the subscription for test isolation.
        _recreate_subscription(admin, _topic_concurrent)
        time.sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################
