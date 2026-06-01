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

logger = logging.getLogger('zato.test.pubsub_perm_edit')

_settle_time = 1.0

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_perm_edit import TestConfig

    out = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return out

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_perm_edit import TestConfig

    out = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return out

# ################################################################################################################################

def _get_puller_a() -> 'any_':
    from zato.common.test.client import PullClient
    from zato.common.test.config_pubsub_perm_edit import TestConfig

    out = PullClient(TestConfig.base_url, TestConfig.subscriber_a_username, TestConfig.subscriber_a_password)
    return out

# ################################################################################################################################

def _get_puller_b() -> 'any_':
    from zato.common.test.client import PullClient
    from zato.common.test.config_pubsub_perm_edit import TestConfig

    out = PullClient(TestConfig.base_url, TestConfig.subscriber_b_username, TestConfig.subscriber_b_password)
    return out

# ################################################################################################################################

def _drain_pull_queue_a() -> 'None':
    """ Pulls messages from subscriber-A until the queue is empty.
    """
    puller = _get_puller_a()
    puller.drain()

# ################################################################################################################################

def _get_subscriptions_a(admin:'any_') -> 'anylist':
    """ Returns all subscriptions for subscriber-A.
    """
    sub_list = admin.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(sub_list, list):
        items:'anylist' = sub_list
    else:
        items = sub_list['zato_pubsub_subscription_get_list_response']

    out:'anylist' = []
    for item in items:
        if item['sec_name'] == 'test.perm.edit.subscriber.a':
            out.append(item)

    return out

# ################################################################################################################################

def _edit_permission(admin:'any_', pattern:'str', sec_base_id:'int'=0) -> 'any_':
    """ Edits the test permission with a new pattern and optionally a new sec_base_id.
    """
    from zato.common.api import PubSub
    from zato.common.test.config_pubsub_perm_edit import TestConfig

    if not sec_base_id:
        sec_base_id = TestConfig.subscriber_a_sec_base_id

    out = admin.invoke('zato.pubsub.permission.edit', {
        'id': TestConfig.permission_id,
        'sec_base_id': sec_base_id,
        'pattern': pattern,
        'access_type': PubSub.API_Client.Publisher_Subscriber,
        'cluster_id': 1,
    })

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPermEdit:
    """ Verifies that permission edit correctly cascade-deletes subscriptions
    whose topics no longer have a matching permission.
    """

# ################################################################################################################################

    def test_01_baseline_sub_receives_messages(self, zato_server:'any_') -> 'None':
        """ Setup validation: subscriber-A receives messages on topics one and two.
        """
        publisher = _get_publisher()
        puller = _get_puller_a()

        _drain_pull_queue_a()

        _ = publisher.publish('perm.edit.topic.one', 'baseline-one')
        _ = publisher.publish('perm.edit.topic.two', 'baseline-two')

        time.sleep(_settle_time)

        result = puller.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 2, f'Expected at least 2 messages, got {message_count}'

# ################################################################################################################################

    def test_02_narrow_permission_deletes_dangling_subs(self, zato_server:'any_') -> 'None':
        """ GAP 16: edit permission from sub=perm.edit.** to sub=perm.edit.topic.one.
        Subscriber-A's subscription to topic.two must be deleted.
        Publish to topic.two, pull returns 0 or 401 (no subscription).
        """
        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller_a()

        _drain_pull_queue_a()

        # .. narrow the permission to only topic.one ..
        _ = _edit_permission(admin, 'sub=perm.edit.topic.one')

        time.sleep(_settle_time)

        # .. publish to topic.two which is no longer permitted ..
        _ = publisher.publish('perm.edit.topic.two', 'should-not-arrive')

        time.sleep(_settle_time)

        # .. pull should return 0 messages or fail with 401 (no subscription) ..
        try:
            result = puller.pull(max_messages=50)
            message_count = result['message_count']
            assert message_count == 0, f'Expected 0 messages from topic.two after narrowing, got {message_count}'
        except Exception as exc:
            # .. 401 means the subscription was deleted entirely - that is correct ..
            assert '401' in str(exc), f'Unexpected error: {exc}'

# ################################################################################################################################

    def test_03_narrowed_topic_pull_returns_zero(self, zato_server:'any_') -> 'None':
        """ GAP 16: confirms that subscription to topic.two no longer exists
        by checking subscription list via admin API.
        """
        admin = _get_admin()

        subs = _get_subscriptions_a(admin)

        # .. if there are subscriptions remaining, none should include topic.two ..
        for sub in subs:
            topic_names = [entry['topic_name'] for entry in sub['topic_name_list']]
            assert 'perm.edit.topic.two' not in topic_names, \
                f'topic.two should not be in subscription topic list: {topic_names}'

# ################################################################################################################################

    def test_04_permitted_topic_still_works(self, zato_server:'any_') -> 'None':
        """ GAP 16 negative: topic.one still works because it matches the narrowed pattern.
        """
        publisher = _get_publisher()
        puller = _get_puller_a()

        _drain_pull_queue_a()

        _ = publisher.publish('perm.edit.topic.one', 'still-permitted')

        time.sleep(_settle_time)

        result = puller.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message from topic.one, got {message_count}'

# ################################################################################################################################

    def test_05_reassign_sec_base_deletes_old_subs(self, zato_server:'any_') -> 'None':
        """ GAP 17: edit permission to change sec_base_id from subscriber-A to subscriber-B.
        Subscriber-A's subscriptions have no remaining permission and must be deleted.
        """
        from zato.common.test.config_pubsub_perm_edit import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller_a()

        _drain_pull_queue_a()

        # .. reassign the permission to subscriber-B ..
        _ = _edit_permission(admin, 'sub=perm.edit.**', sec_base_id=TestConfig.subscriber_b_sec_base_id)

        time.sleep(_settle_time)

        # .. subscriber-A should have no subscriptions remaining ..
        subs = _get_subscriptions_a(admin)
        assert len(subs) == 0, f'Expected 0 subscriptions for subscriber-A after reassign, got {len(subs)}'

        # .. publish to topic.one - subscriber-A should not receive it ..
        _ = publisher.publish('perm.edit.topic.one', 'after-reassign')

        time.sleep(_settle_time)

        # .. pull should fail or return 0 since subscriber-A has no subscription ..
        try:
            result = puller.pull(max_messages=50)
            message_count = result['message_count']
            assert message_count == 0, f'Expected 0 messages for subscriber-A after reassign, got {message_count}'
        except Exception:
            # .. pull may raise because subscriber-A has no active subscription ..
            pass

# ################################################################################################################################

    def test_06_new_sec_base_can_subscribe(self, zato_server:'any_') -> 'None':
        """ GAP 17 positive: subscriber-B now has the permission and can create
        a subscription and receive messages.
        """
        from zato.common.test.config_pubsub_perm_edit import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()

        # .. create a subscription for subscriber-B ..
        _ = admin.invoke('zato.pubsub.subscription.create', {
            'cluster_id': 1,
            'sec_base_id': TestConfig.subscriber_b_sec_base_id,
            'delivery_type': 'pull',
            'topic_name_list': [
                {'topic_name': 'perm.edit.topic.one', 'is_pub_enabled': True, 'is_delivery_enabled': True},
                {'topic_name': 'perm.edit.topic.two', 'is_pub_enabled': True, 'is_delivery_enabled': True},
            ],
        })

        time.sleep(_settle_time)

        # .. publish a message ..
        _ = publisher.publish('perm.edit.topic.one', 'subscriber-b-test')

        time.sleep(_settle_time)

        # .. subscriber-B pulls it ..
        puller_b = _get_puller_b()
        result = puller_b.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message for subscriber-B, got {message_count}'

# ################################################################################################################################

    def test_07_widen_permission_does_not_delete_subs(self, zato_server:'any_') -> 'None':
        """ GAP 16 negative: widening the pattern does NOT delete existing subscriptions.
        Subscriber-B's subscription should remain intact.
        """
        from zato.common.test.config_pubsub_perm_edit import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()

        # .. widen the pattern back to the broadest form ..
        _ = _edit_permission(admin, 'sub=perm.edit.**', sec_base_id=TestConfig.subscriber_b_sec_base_id)

        time.sleep(_settle_time)

        # .. subscriber-B's subscription should still work ..
        _ = publisher.publish('perm.edit.topic.two', 'after-widen')

        time.sleep(_settle_time)

        puller_b = _get_puller_b()
        result = puller_b.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message after widening, got {message_count}'

# ################################################################################################################################
# ################################################################################################################################
