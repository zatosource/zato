# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_sub_edit')

_settle_time = 0.5

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_sub_edit import TestConfig

    out = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return out

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_sub_edit import TestConfig

    out = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return out

# ################################################################################################################################

def _get_puller() -> 'any_':
    from zato.common.test.client import PullClient
    from zato.common.test.config_pubsub_sub_edit import TestConfig

    out = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)
    return out

# ################################################################################################################################

def _get_subscriptions(admin:'any_') -> 'anylist':
    """ Returns all subscriptions for the test subscriber.
    """
    sub_list = admin.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(sub_list, list):
        items:'anylist' = sub_list
    else:
        items = sub_list['zato_pubsub_subscription_get_list_response']

    out:'anylist' = []
    for item in items:
        if item['sec_name'] == 'test.sub.edit.subscriber':
            out.append(item)

    return out

# ################################################################################################################################

def _get_subscription_topic_names(admin:'any_') -> 'list[str]':
    """ Returns a sorted list of topic names from the subscriber's first subscription.
    """
    subs = _get_subscriptions(admin)
    assert subs, 'No subscriptions found for test.se.subscriber'

    topic_name_list = subs[0]['topic_name_list']

    out:'list[str]' = []
    for entry in topic_name_list:
        out.append(entry['topic_name'])
    out.sort()

    return out

# ################################################################################################################################

def _edit_subscription_topics(admin:'any_', topic_names:'list[str]') -> 'any_':
    """ Edits the subscriber's subscription to use the given list of topic names.
    """
    from zato.common.test.config_pubsub_sub_edit import TestConfig

    subs = _get_subscriptions(admin)
    assert subs, 'No subscriptions found for test.sub.edit.subscriber'

    subscription = subs[0]

    topic_name_list:'anylist' = []
    for topic_name in topic_names:
        topic_entry = {
            'topic_name': topic_name,
            'is_pub_enabled': True,
            'is_delivery_enabled': True,
        }
        topic_name_list.append(topic_entry)

    out = admin.invoke('zato.pubsub.subscription.edit', {
        'sub_key': subscription['sub_key'],
        'cluster_id': 1,
        'topic_name_list': topic_name_list,
        'sec_base_id': TestConfig.subscriber_sec_base_id,
        'delivery_type': subscription['delivery_type'],
        'is_pub_active': True,
        'is_delivery_active': True,
    })

    return out

# ################################################################################################################################

def _drain_pull_queue() -> 'None':
    """ Pulls messages until the queue is empty.
    """
    puller = _get_puller()
    puller.drain()

# ################################################################################################################################

def _get_outgoing_rest_id(admin:'any_', connection_name:'str') -> 'int':
    """ Looks up an outgoing REST connection ID by name.
    """
    result = admin.invoke('zato.http-soap.get-list', {
        'cluster_id': 1,
        'connection': 'outgoing',
        'transport': 'plain_http',
    })

    if isinstance(result, list):
        items:'anylist' = result
    else:
        items = result['zato_http_soap_get_list_response']

    for item in items:
        if item['name'] == connection_name:
            return item['id']

    raise Exception(f'Outgoing REST connection not found: {connection_name}')

# ################################################################################################################################
# ################################################################################################################################

class TestSubEdit:
    """ Verifies that subscription edit correctly propagates through
    Redis, in-memory config, _push_subs, and delivery greenlets.
    """

# ################################################################################################################################

    def test_01_initial_publish_and_pull(self, zato_server:'any_') -> 'None':
        """ Baseline: publish to topic.one and topic.two, pull receives both.
        """
        publisher = _get_publisher()
        puller = _get_puller()

        # .. drain any pre-existing messages ..
        _drain_pull_queue()

        # .. publish to both initial topics ..
        _ = publisher.publish('sub.edit.topic.one', 'baseline-message-one')
        _ = publisher.publish('sub.edit.topic.two', 'baseline-message-two')

        time.sleep(_settle_time)

        result = puller.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 2, f'Expected at least 2 messages, got {message_count}'

# ################################################################################################################################

    def test_02_remove_topic_still_pulls_remaining(self, zato_server:'any_') -> 'None':
        """ GAP 12: edit sub to remove topic.two, keep topic.one.
        Publish to topic.one, pull succeeds.
        """
        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        _drain_pull_queue()

        # .. edit to keep only topic.one ..
        _ = _edit_subscription_topics(admin, ['sub.edit.topic.one'])

        time.sleep(_settle_time)

        # .. publish to topic.one and pull ..
        _ = publisher.publish('sub.edit.topic.one', 'after-remove-topic-two')

        time.sleep(_settle_time)

        result = puller.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message from topic.one, got {message_count}'

# ################################################################################################################################

    def test_03_removed_topic_no_longer_delivered(self, zato_server:'any_') -> 'None':
        """ GAP 12: publish to topic.two (removed), pull returns 0 new messages.
        Proves Redis consumer group for topic.two was cleaned up.
        """
        publisher = _get_publisher()
        puller = _get_puller()

        _drain_pull_queue()

        # .. publish to the removed topic ..
        _ = publisher.publish('sub.edit.topic.two', 'should-not-arrive')

        time.sleep(_settle_time)

        result = puller.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count == 0, f'Expected 0 messages from removed topic.two, got {message_count}'

# ################################################################################################################################

    def test_04_add_new_topic_receives_messages(self, zato_server:'any_') -> 'None':
        """ GAP 13: edit sub to add topic.three. Publish to topic.three, pull receives message.
        Proves Redis subscribe was called for new topic.
        """
        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        _drain_pull_queue()

        # .. edit to include topic.one and topic.three ..
        _ = _edit_subscription_topics(admin, ['sub.edit.topic.one', 'sub.edit.topic.three'])

        time.sleep(_settle_time)

        # .. publish to topic.three ..
        _ = publisher.publish('sub.edit.topic.three', 'new-topic-message')

        time.sleep(_settle_time)

        result = puller.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message from topic.three, got {message_count}'

# ################################################################################################################################

    def test_05_add_topic_four_and_verify_full_set(self, zato_server:'any_') -> 'None':
        """ GAP 13: edit sub to add topic.four. Publish to all current topics, pull receives all.
        """
        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        _drain_pull_queue()

        # .. edit to include topic.one, topic.three, and topic.four ..
        _ = _edit_subscription_topics(admin, ['sub.edit.topic.one', 'sub.edit.topic.three', 'sub.edit.topic.four'])

        time.sleep(_settle_time)

        # .. publish to all three ..
        _ = publisher.publish('sub.edit.topic.one', 'full-set-one')
        _ = publisher.publish('sub.edit.topic.three', 'full-set-three')
        _ = publisher.publish('sub.edit.topic.four', 'full-set-four')

        time.sleep(_settle_time)

        result = puller.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 3, f'Expected at least 3 messages from full set, got {message_count}'

# ################################################################################################################################

    def test_06_subscription_api_reflects_edit(self, zato_server:'any_') -> 'None':
        """ GAP 12 + 13: get-list shows the correct topic_name_list after edits.
        """
        admin = _get_admin()

        topic_names = _get_subscription_topic_names(admin)

        assert 'sub.edit.topic.one' in topic_names, f'topic.one missing from {topic_names}'
        assert 'sub.edit.topic.three' in topic_names, f'topic.three missing from {topic_names}'
        assert 'sub.edit.topic.four' in topic_names, f'topic.four missing from {topic_names}'
        assert 'sub.edit.topic.two' not in topic_names, f'topic.two should not be in {topic_names}'

# ################################################################################################################################

    def test_07_edit_does_not_leak_redis_state(self, zato_server:'any_') -> 'None':
        """ GAP 12: after removing topic.two earlier, re-add it.
        Publish and pull succeeds - proves old consumer group was cleaned and new one works.
        """
        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        _drain_pull_queue()

        # .. re-add topic.two alongside the current set ..
        _ = _edit_subscription_topics(admin, ['sub.edit.topic.one', 'sub.edit.topic.two', 'sub.edit.topic.three', 'sub.edit.topic.four'])

        time.sleep(_settle_time)

        # .. publish to topic.two ..
        _ = publisher.publish('sub.edit.topic.two', 're-added-topic-two')

        time.sleep(_settle_time)

        result = puller.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message from re-added topic.two, got {message_count}'

# ################################################################################################################################

    def test_08_switch_to_push_starts_delivery(self, zato_server:'any_') -> 'None':
        """ GAP 14 + 15: edit the subscription to change delivery_type from pull to push.
        Publish a message, verify the webhook receiver gets it.
        """
        from zato.common.test.config_pubsub_sub_edit import TestConfig
        from zato.common.test.receiver import WebhookReceiver

        admin = _get_admin()
        publisher = _get_publisher()

        _drain_pull_queue()

        # .. look up the outgoing REST connection ID ..
        endpoint_id = _get_outgoing_rest_id(admin, 'test.sub.edit.out.webhook')

        # .. get current subscription ..
        subs = _get_subscriptions(admin)
        assert subs, 'No subscriptions found'
        subscription = subs[0]

        # .. build topic list with flags ..
        topic_name_list:'anylist' = []
        for entry in subscription['topic_name_list']:
            topic_entry = {
                'topic_name': entry['topic_name'],
                'is_pub_enabled': True,
                'is_delivery_enabled': True,
            }
            topic_name_list.append(topic_entry)

        # .. create a fresh receiver to track only push-delivered messages ..
        receiver = WebhookReceiver(TestConfig.webhook_port, TestConfig.webhook_output_directory)
        receiver.clear_output()

        # .. edit to push delivery ..
        _ = admin.invoke('zato.pubsub.subscription.edit', {
            'sub_key': subscription['sub_key'],
            'cluster_id': 1,
            'topic_name_list': topic_name_list,
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'delivery_type': 'push',
            'push_type': 'rest',
            'rest_push_endpoint_id': endpoint_id,
            'is_pub_active': True,
            'is_delivery_active': True,
        })

        time.sleep(_settle_time)

        # .. publish a message ..
        _ = publisher.publish('sub.edit.topic.one', 'push-delivery-test')

        # .. wait for delivery to the webhook ..
        delivered = receiver.wait_for_delivery(expected_count=1, timeout=10.0)
        delivered_count = len(delivered)

        assert delivered_count >= 1, f'Expected at least 1 push-delivered message, got {delivered_count}'

# ################################################################################################################################

    def test_09_switch_back_to_pull_stops_push(self, zato_server:'any_') -> 'None':
        """ GAP 14 + 15: edit back to pull. Publish a message, verify webhook receiver
        does NOT get it but pull does.
        """
        from zato.common.test.config_pubsub_sub_edit import TestConfig
        from zato.common.test.receiver import WebhookReceiver

        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        # .. get current subscription ..
        subs = _get_subscriptions(admin)
        assert subs, 'No subscriptions found'
        subscription = subs[0]

        # .. build topic list with flags ..
        topic_name_list:'anylist' = []
        for entry in subscription['topic_name_list']:
            topic_entry = {
                'topic_name': entry['topic_name'],
                'is_pub_enabled': True,
                'is_delivery_enabled': True,
            }
            topic_name_list.append(topic_entry)

        # .. edit back to pull ..
        _ = admin.invoke('zato.pubsub.subscription.edit', {
            'sub_key': subscription['sub_key'],
            'cluster_id': 1,
            'topic_name_list': topic_name_list,
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'delivery_type': 'pull',
            'is_pub_active': True,
            'is_delivery_active': True,
        })

        time.sleep(_settle_time)

        # .. clear webhook output and drain pull queue ..
        receiver = WebhookReceiver(TestConfig.webhook_port, TestConfig.webhook_output_directory)
        receiver.clear_output()
        _drain_pull_queue()

        # .. publish a message ..
        _ = publisher.publish('sub.edit.topic.one', 'pull-only-after-switch-back')

        time.sleep(_settle_time)

        # .. verify webhook did NOT receive it ..
        webhook_count = receiver.delivered_count()
        assert webhook_count == 0, f'Expected 0 webhook deliveries after switch to pull, got {webhook_count}'

        # .. verify pull DOES receive it ..
        result = puller.pull(max_messages=50)
        message_count = result['message_count']
        assert message_count >= 1, f'Expected at least 1 pull message after switch back, got {message_count}'

# ################################################################################################################################
# ################################################################################################################################
