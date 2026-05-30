# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

_topic = 'newsub.test.topic.1'
_settle_time = 0.5

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

class TestNewSubscriberDepth:
    """ Verifies that new subscribers only see messages published after their subscription was created.
    """

# ################################################################################################################################

    def test_new_subscriber_has_zero_pending_on_existing_topic(self, zato_server:'any_') -> 'None':
        """ A new subscriber on a topic with pre-existing messages should have zero pending.
        """
        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_new_sub import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        # .. publish messages before subscription exists ..
        pre_count = 10
        for idx in range(pre_count):
            _ = publisher.publish(_topic, f'pre-existing-{idx}')

        time.sleep(_settle_time)

        # .. now create the subscription ..
        sub_key = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        try:
            time.sleep(_settle_time)

            # .. the new subscriber should see zero pending ..
            pending = _get_pending_depth(admin, sub_key)
            assert pending == 0, f'Expected 0 pending, got {pending}'

        finally:
            _delete_subscription(admin, sub_key)

# ################################################################################################################################

    def test_new_subscriber_receives_only_post_subscription_messages(self, zato_server:'any_') -> 'None':
        """ A new subscriber should only see messages published after the subscription was created.
        """
        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_new_sub import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        # .. publish messages before subscription exists ..
        pre_count = 5
        for idx in range(pre_count):
            _ = publisher.publish(_topic, f'before-sub-{idx}')

        time.sleep(_settle_time)

        # .. create the subscription ..
        sub_key = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        try:
            # .. publish messages after subscription exists ..
            post_count = 3
            for idx in range(post_count):
                _ = publisher.publish(_topic, f'after-sub-{idx}')

            time.sleep(_settle_time)

            # .. only the post-subscription messages should be pending ..
            pending = _get_pending_depth(admin, sub_key)
            assert pending == post_count, f'Expected {post_count} pending, got {pending}'

        finally:
            _delete_subscription(admin, sub_key)

# ################################################################################################################################

    def test_new_subscriber_pulls_only_new_messages_via_rest(self, zato_server:'any_') -> 'None':
        """ A new subscriber pulling via REST should only receive messages published after subscription.
        """
        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_new_sub import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)

        # .. publish messages before subscription exists ..
        pre_count = 5
        for idx in range(pre_count):
            _ = publisher.publish(_topic, f'pre-pull-{idx}')

        time.sleep(_settle_time)

        # .. create the subscription ..
        sub_key = _create_subscription(admin, TestConfig.subscriber_sec_base_id)

        try:
            # .. publish messages after subscription exists ..
            post_data = []
            post_count = 4
            for idx in range(post_count):
                payload = f'post-pull-{idx}'
                _ = publisher.publish(_topic, payload)
                post_data.append(payload)

            time.sleep(_settle_time)

            # .. pull messages via REST ..
            pull_result = puller.pull(max_messages=100)
            received_count = pull_result['message_count']
            messages = pull_result['messages']

            # .. we should only get the post-subscription messages ..
            assert received_count == post_count, f'Expected {post_count} messages, got {received_count}'

            received_data = []
            for message in messages:
                received_data.append(message['data'])

            for payload in post_data:
                assert payload in received_data, f'Missing expected message: {payload}'

        finally:
            _delete_subscription(admin, sub_key)

# ################################################################################################################################
# ################################################################################################################################
