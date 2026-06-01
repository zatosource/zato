# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import threading
import time

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_subscribe_atomic.live')

_topic = 'subscribe.atomic.test.topic.1'

_settle_time = 0.1

# ################################################################################################################################
# ################################################################################################################################

def _create_subscription(admin:'any_', sec_base_id:'int') -> 'str':
    """ Creates a pull subscription for the subscriber and returns the sub_key.
    """
    result = admin.invoke('zato.pubsub.subscription.create', {
        'cluster_id': 1,
        'topic_name_list': [_topic],
        'sec_base_id': sec_base_id,
        'delivery_type': 'pull',
    })

    out = result['sub_key']
    return out

# ################################################################################################################################
# ################################################################################################################################

def _delete_subscription(admin:'any_', sub_key:'str') -> 'None':
    """ Deletes a subscription by looking up its ID from the sub_key.
    """
    sub_list = admin.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(sub_list, list):
        items:'anylist' = sub_list
    else:
        items = sub_list['zato_pubsub_subscription_get_list_response']

    for item in items:
        if item['sub_key'] == sub_key:
            _ = admin.invoke('zato.pubsub.subscription.delete', {'id': item['id']})
            return

# ################################################################################################################################
# ################################################################################################################################

def _get_pending_depth(admin:'any_', sub_key:'str') -> 'int':
    """ Returns the pending depth for a subscription.
    """
    browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
        'sub_key': sub_key,
        'state': 'pending',
    })

    out = browse_result['total']
    return out

# ################################################################################################################################
# ################################################################################################################################

def _publish_messages(publisher:'any_', count:'int') -> 'None':
    """ Publishes count messages to the test topic.
    """
    for idx in range(count):
        _ = publisher.publish(_topic, f'subscribe-atomic-payload-{idx}')

# ################################################################################################################################
# ################################################################################################################################

class TestPublishDuringSubscribeNoPhantomPending:
    """ Gap 1: concurrent publish during subscribe must not create phantom pending entries.
    """

    def test_publish_during_subscribe_no_phantom_pending(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_subscribe_atomic import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)

        # .. publish a burst from a thread while subscribing ..
        publish_count = 5
        errors:'anylist' = []

        def _publish_burst() -> 'None':
            try:
                _publish_messages(publisher, publish_count)
            except Exception as error:
                errors.append(error)

        publish_thread = threading.Thread(target=_publish_burst)

        # .. create subscription and start publishing concurrently ..
        publish_thread.start()
        sub_key = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        try:
            publish_thread.join()

            assert not errors, f'Publish thread raised: {errors}'

            time.sleep(_settle_time)

            # .. pull whatever messages are available ..
            pull_result = puller.pull(max_messages=100)
            pulled_count = pull_result['message_count']

            # .. after pulling, pending depth must be zero - no phantom entries ..
            pending = _get_pending_depth(admin, sub_key)

            assert pending == 0, f'Expected 0 pending after pull, got {pending} (pulled {pulled_count})'

        finally:
            _delete_subscription(admin, sub_key)

# ################################################################################################################################
# ################################################################################################################################

class TestNoMessagesLostAfterSubscribe:
    """ Gap 2: all messages published after subscribe must be delivered, no NOGROUP.
    """

    def test_no_messages_lost_after_subscribe(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_subscribe_atomic import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)

        # .. create subscription and wait for it to settle ..
        sub_key = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        try:
            time.sleep(_settle_time)

            # .. publish messages after subscription is established ..
            message_count = 7
            _publish_messages(publisher, message_count)

            time.sleep(_settle_time)

            # .. pull and verify all messages arrived.
            pull_result = puller.pull(max_messages=100)

            assert pull_result['message_count'] == message_count, \
                f'Expected {message_count} messages, got {pull_result["message_count"]}'

        finally:
            _delete_subscription(admin, sub_key)

# ################################################################################################################################
# ################################################################################################################################

class TestPendingDepthMatchesActualMessages:
    """ Gap 3: pending depth must match real message count, no phantom entries.
    """

    def test_pending_depth_matches_actual_messages(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_subscribe_atomic import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)

        # .. create subscription ..
        sub_key = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        try:
            time.sleep(_settle_time)

            # .. publish 5 messages ..
            message_count = 5
            _publish_messages(publisher, message_count)

            time.sleep(_settle_time)

            # .. pending depth must equal published count ..
            pending_before = _get_pending_depth(admin, sub_key)

            assert pending_before == message_count, \
                f'Expected {message_count} pending, got {pending_before}'

            # .. pull all messages ..
            pull_result = puller.pull(max_messages=100)

            assert pull_result['message_count'] == message_count

            # .. pending depth must be zero after pulling.
            pending_after = _get_pending_depth(admin, sub_key)

            assert pending_after == 0, f'Expected 0 pending after pull, got {pending_after}'

        finally:
            _delete_subscription(admin, sub_key)

# ################################################################################################################################
# ################################################################################################################################

class TestConcurrentSubscribeAndPublishNoStalePending:
    """ Gap 4: repeated concurrent subscribe + publish must never leave phantom pending entries.
    """

    def test_concurrent_subscribe_and_publish_no_stale_pending(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_subscribe_atomic import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)

        iteration_count = 10
        messages_per_iteration = 3

        for iteration in range(iteration_count):

            errors:'anylist' = []
            sub_key_holder:'anylist' = []

            def _subscribe() -> 'None':
                try:
                    sub_key = _create_subscription(admin, TestConfig.subscriber_sec_base_id)
                    sub_key_holder.append(sub_key)
                except Exception as error:
                    errors.append(error)

            def _publish() -> 'None':
                try:
                    _publish_messages(publisher, messages_per_iteration)
                except Exception as error:
                    errors.append(error)

            subscribe_thread = threading.Thread(target=_subscribe)
            publish_thread = threading.Thread(target=_publish)

            # .. start both threads simultaneously ..
            subscribe_thread.start()
            publish_thread.start()

            subscribe_thread.join()
            publish_thread.join()

            assert not errors, f'Iteration {iteration} raised: {errors}'
            assert sub_key_holder, f'Iteration {iteration}: subscription was not created'

            sub_key = sub_key_holder[0]

            try:
                time.sleep(_settle_time)

                # .. pull whatever is available ..
                _ = puller.pull(max_messages=100)

                # .. pending must be zero after pulling - no phantom entries ..
                pending = _get_pending_depth(admin, sub_key)

                assert pending == 0, \
                    f'Iteration {iteration}: expected 0 pending after pull, got {pending}'

            finally:
                _delete_subscription(admin, sub_key)

# ################################################################################################################################
# ################################################################################################################################

class TestIdempotentSubscribeNoCorruption:
    """ Edge case 5: creating a second subscription for the same security must not corrupt state.
    """

    def test_idempotent_subscribe_no_corruption(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_subscribe_atomic import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        # .. create first subscription ..
        sub_key_first = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        try:
            time.sleep(_settle_time)

            # .. create a second subscription for the same security - must not raise ..
            sub_key_second = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

            try:
                time.sleep(_settle_time)

                # .. publish messages - both subscriptions receive pending entries ..
                message_count = 3
                _publish_messages(publisher, message_count)

                time.sleep(_settle_time)

                # .. both subscriptions must have pending messages ..
                pending_first = _get_pending_depth(admin, sub_key_first)
                pending_second = _get_pending_depth(admin, sub_key_second)

                assert pending_first == message_count, \
                    f'Expected {message_count} pending for first sub, got {pending_first}'

                assert pending_second == message_count, \
                    f'Expected {message_count} pending for second sub, got {pending_second}'

                # .. clear both queues via admin API ..
                _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_first})
                _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_second})

                # .. both must be zero after clearing ..
                pending_first_after = _get_pending_depth(admin, sub_key_first)
                pending_second_after = _get_pending_depth(admin, sub_key_second)

                assert pending_first_after == 0, \
                    f'Expected 0 pending for first sub after clear, got {pending_first_after}'

                assert pending_second_after == 0, \
                    f'Expected 0 pending for second sub after clear, got {pending_second_after}'

            finally:
                _delete_subscription(admin, sub_key_second)

        finally:
            _delete_subscription(admin, sub_key_first)

# ################################################################################################################################
# ################################################################################################################################

class TestResubscribeAfterUnsubscribeNoStaleMessages:
    """ Edge case 6: unsubscribe + resubscribe must not leak stale messages.
    """

    def test_resubscribe_after_unsubscribe_no_stale_messages(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_subscribe_atomic import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)

        # .. create subscription ..
        sub_key = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        time.sleep(_settle_time)

        # .. publish 3 messages and pull them ..
        first_batch_count = 3
        _publish_messages(publisher, first_batch_count)

        time.sleep(_settle_time)

        pull_result = puller.pull(max_messages=100)

        assert pull_result['message_count'] == first_batch_count

        # .. delete subscription (unsubscribe) ..
        _delete_subscription(admin, sub_key)

        time.sleep(_settle_time)

        # .. publish 2 messages while no subscriber exists ..
        gap_count = 2
        _publish_messages(publisher, gap_count)

        time.sleep(_settle_time)

        # .. resubscribe ..
        sub_key_new = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        try:
            time.sleep(_settle_time)

            # .. publish 4 messages after resubscribe ..
            post_resub_count = 4
            _publish_messages(publisher, post_resub_count)

            time.sleep(_settle_time)

            # .. pull and verify only post-resubscribe messages arrive.
            pull_result = puller.pull(max_messages=100)

            assert pull_result['message_count'] == post_resub_count, \
                f'Expected {post_resub_count} messages, got {pull_result["message_count"]}'

        finally:
            _delete_subscription(admin, sub_key_new)

# ################################################################################################################################
# ################################################################################################################################

class TestZeroPendingDepthOnFreshSubscribe:
    """ Edge case 7: pending depth must be 0 immediately after subscribing to a topic with existing messages.
    """

    def test_zero_pending_depth_on_fresh_subscribe(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_subscribe_atomic import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        # .. publish 10 messages before any subscriber exists ..
        pre_sub_count = 10
        _publish_messages(publisher, pre_sub_count)

        time.sleep(_settle_time)

        # .. create subscription ..
        sub_key = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        try:
            time.sleep(_settle_time)

            # .. pending depth must be zero - pre-existing messages must not appear.
            pending = _get_pending_depth(admin, sub_key)

            assert pending == 0, f'Expected 0 pending on fresh subscribe, got {pending}'

        finally:
            _delete_subscription(admin, sub_key)

# ################################################################################################################################
# ################################################################################################################################
