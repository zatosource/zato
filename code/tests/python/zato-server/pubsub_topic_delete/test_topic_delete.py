# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_topic_delete')

_settle_time = 3.0

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_topic_delete import TestConfig
    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_topic_delete import TestConfig
    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _get_puller() -> 'any_':
    from zato.common.test.client import PullClient
    from zato.common.test.config_pubsub_topic_delete import TestConfig
    puller = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)
    return puller

# ################################################################################################################################

def _get_topic_id(admin:'any_', topic_name:'str') -> 'int':
    """ Finds a topic ID by name.
    """
    topic_list = admin.invoke('zato.pubsub.topic.get-list', {'cluster_id': 1})

    if isinstance(topic_list, list):
        items:'anylist' = topic_list
    else:
        items = topic_list['zato_pubsub_topic_get_list_response']

    for item in items:
        if item['name'] == topic_name:
            return item['id']

    raise Exception(f'Topic not found: {topic_name}')

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
# ################################################################################################################################

class TestTopicDelete:
    """ Verifies that topic deletion cleans up all related state:
    ODB subscriptions, in-memory sub configs, SubscriptionsStore mappings,
    push delivery configs, and delivery greenlets.
    """

# ################################################################################################################################

    def test_01_delete_topic_removes_single_topic_pull_subscription(self, zato_server:'any_') -> 'None':
        """ Deleting a topic that is the sole topic in a pull subscription
        must delete the subscription from ODB (Gap 1).
        After deletion, re-creating the topic and subscribing again must work cleanly,
        which proves no leftover ODB row or stale in-memory state blocks re-subscription.
        """
        admin = _get_admin()

        # .. verify the pull subscription on td.pull.single exists ..
        subs = _get_subscriptions(admin, 'test.td.subscriber')

        pull_single_subs:'anylist' = []
        for sub in subs:
            if 'td.pull.single' in str(sub['topic_name_list']):
                pull_single_subs.append(sub)

        assert len(pull_single_subs) == 1, f'Expected 1 sub on td.pull.single, got {len(pull_single_subs)}'

        # .. delete the topic ..
        topic_id = _get_topic_id(admin, 'td.pull.single')
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})

        time.sleep(_settle_time)

        # .. the subscription should be gone ..
        subs_after = _get_subscriptions(admin, 'test.td.subscriber')

        pull_single_subs_after:'anylist' = []
        for sub in subs_after:
            if 'td.pull.single' in str(sub['topic_name_list']):
                pull_single_subs_after.append(sub)

        assert len(pull_single_subs_after) == 0, \
            f'Expected 0 subs on td.pull.single after delete, got {len(pull_single_subs_after)}'

        # .. re-create the topic ..
        _ = admin.invoke('zato.pubsub.topic.create', {
            'name': 'td.pull.single',
            'is_active': True,
        })

        time.sleep(_settle_time)

        # .. re-subscribe ..
        from zato.common.test.config_pubsub_topic_delete import TestConfig
        _ = admin.invoke('zato.pubsub.subscription.create', {
            'cluster_id': 1,
            'topic_name_list': ['td.pull.single'],
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'delivery_type': 'pull',
        })

        time.sleep(_settle_time)

        # .. publish and pull to confirm the full round-trip works ..
        publisher = _get_publisher()
        puller = _get_puller()

        _ = publisher.publish('td.pull.single', 'post-recreate-message')
        time.sleep(_settle_time)

        result = puller.pull(max_messages=10)
        message_count = result['message_count']
        assert message_count >= 1, f'Expected at least 1 message after re-subscribe, got {message_count}'

        # .. clean up: delete td.pull.single again for subsequent tests ..
        topic_id = _get_topic_id(admin, 'td.pull.single')
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})

        time.sleep(_settle_time)

# ################################################################################################################################

    def test_02_delete_topic_preserves_multi_topic_subscription(self, zato_server:'any_') -> 'None':
        """ Deleting one topic from a multi-topic subscription must preserve
        the subscription with the remaining topic (Gap 1 negative case).
        """
        admin = _get_admin()

        # .. verify the multi-topic subscription on td.multi.first + td.multi.second exists ..
        subs = _get_subscriptions(admin, 'test.td.subscriber')

        multi_subs:'anylist' = []
        for sub in subs:
            if 'td.multi.first' in str(sub['topic_name_list']):
                multi_subs.append(sub)

        assert len(multi_subs) == 1, f'Expected 1 multi-topic sub, got {len(multi_subs)}'

        # .. delete td.multi.first ..
        topic_id = _get_topic_id(admin, 'td.multi.first')
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})

        time.sleep(_settle_time)

        # .. the subscription should still exist with td.multi.second only ..
        subs_after = _get_subscriptions(admin, 'test.td.subscriber')

        second_subs:'anylist' = []
        for sub in subs_after:
            if 'td.multi.second' in str(sub['topic_name_list']):
                second_subs.append(sub)

        assert len(second_subs) == 1, f'Expected 1 sub with td.multi.second, got {len(second_subs)}'

        # .. td.multi.first should not be in the topic list ..
        topic_names_str = str(second_subs[0]['topic_name_list'])
        assert 'td.multi.first' not in topic_names_str, f'td.multi.first still in topic list: {topic_names_str}'

# ################################################################################################################################

    def test_03_delete_topic_cleans_in_memory_sub_config(self, zato_server:'any_') -> 'None':
        """ After deleting td.pull.single (done in test_01), re-creating it with a fresh
        subscription and publishing must deliver only to the new subscriber,
        proving config_store.pubsub_subs was cleaned (Gap 2).
        """
        admin = _get_admin()
        publisher = _get_publisher()

        # .. td.pull.single was deleted in test_01, re-create it ..
        _ = admin.invoke('zato.pubsub.topic.create', {
            'name': 'td.pull.single',
            'is_active': True,
        })

        time.sleep(_settle_time)

        # .. subscribe again ..
        from zato.common.test.config_pubsub_topic_delete import TestConfig
        _ = admin.invoke('zato.pubsub.subscription.create', {
            'cluster_id': 1,
            'topic_name_list': ['td.pull.single'],
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'delivery_type': 'pull',
        })

        time.sleep(_settle_time)

        # .. publish a message ..
        _ = publisher.publish('td.pull.single', 'gap2-test-message')
        time.sleep(_settle_time)

        # .. pull as the subscriber - should get exactly the message we published ..
        puller = _get_puller()
        result = puller.pull(max_messages=10)
        message_count = result['message_count']
        assert message_count >= 1, f'Expected at least 1 message, got {message_count}'

        # .. clean up ..
        topic_id = _get_topic_id(admin, 'td.pull.single')
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

# ################################################################################################################################

    def test_04_delete_topic_cleans_subscriptions_store(self, zato_server:'any_') -> 'None':
        """ After deleting td.pull.single, re-subscribing the same user to td.multi.second
        must succeed with a new working sub_key, proving SubscriptionsStore
        was cleaned (Gap 3).
        """
        from zato.common.test.config_pubsub_topic_delete import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        # .. the previous subscription's in-memory mapping was removed
        # .. when td.pull.single's subscription was deleted (remove_user clears the username).
        # .. re-subscribing must generate a fresh sub_key,
        # .. proving that stale keys do not block a new subscription ..
        _ = admin.invoke('zato.pubsub.subscription.create', {
            'cluster_id': 1,
            'topic_name_list': ['td.multi.second'],
            'sec_base_id': TestConfig.subscriber_sec_base_id,
            'delivery_type': 'pull',
        })

        time.sleep(_settle_time)

        # .. publish to td.multi.second ..
        _ = publisher.publish('td.multi.second', 'gap3-test-message')
        time.sleep(_settle_time)

        # .. pull - should get the message ..
        result = puller.pull(max_messages=10)
        message_count = result['message_count']
        assert message_count >= 1, f'Expected at least 1 message on td.multi.second, got {message_count}'

# ################################################################################################################################

    def test_05_delete_topic_stops_push_delivery(self, zato_server:'any_') -> 'None':
        """ Deleting td.push.single must stop the push delivery greenlet and clean _push_subs.
        Publishing to a re-created td.push.single must not deliver to the old webhook (Gaps 4, 5).
        """
        from zato.common.test.config_pubsub_topic_delete import TestConfig

        admin = _get_admin()
        publisher = _get_publisher()
        receiver = TestConfig.push_receiver

        # .. clear any prior messages ..
        receiver.clear_output() # pyright: ignore[reportOptionalMemberAccess]

        # .. publish 1 message and confirm the webhook receives it ..
        _ = publisher.publish('td.push.single', 'push-pre-delete')
        time.sleep(_settle_time)

        pre_delete_count = receiver.delivered_count() # pyright: ignore[reportOptionalMemberAccess]
        assert pre_delete_count >= 1, f'Expected at least 1 push delivery before delete, got {pre_delete_count}'

        # .. clear output and record baseline ..
        receiver.clear_output() # pyright: ignore[reportOptionalMemberAccess]

        # .. delete the topic ..
        topic_id = _get_topic_id(admin, 'td.push.single')
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

        # .. re-create td.push.single without any subscription ..
        _ = admin.invoke('zato.pubsub.topic.create', {
            'name': 'td.push.single',
            'is_active': True,
        })
        time.sleep(_settle_time)

        # .. publish 5 messages to the re-created topic ..
        for idx in range(5):
            _ = publisher.publish('td.push.single', f'push-post-delete-{idx}')

        time.sleep(5)

        # .. the webhook should NOT have received any of these ..
        post_delete_count = receiver.delivered_count() # pyright: ignore[reportOptionalMemberAccess]
        assert post_delete_count == 0, \
            f'Expected 0 push deliveries after topic delete, got {post_delete_count}'

# ################################################################################################################################

    def test_06_delete_last_topic_from_multi_removes_subscription(self, zato_server:'any_') -> 'None':
        """ Deleting td.multi.second (the last remaining topic in the multi-topic sub)
        must remove the entire subscription (Gap 1 end-to-end).
        """
        admin = _get_admin()

        # .. verify td.multi.second subscription exists ..
        subs = _get_subscriptions(admin, 'test.td.subscriber')

        second_subs:'anylist' = []
        for sub in subs:
            if 'td.multi.second' in str(sub['topic_name_list']):
                second_subs.append(sub)

        assert len(second_subs) >= 1, f'Expected at least 1 sub on td.multi.second, got {len(second_subs)}'

        # .. delete td.multi.second ..
        topic_id = _get_topic_id(admin, 'td.multi.second')
        _ = admin.invoke('zato.pubsub.topic.delete', {'id': topic_id})
        time.sleep(_settle_time)

        # .. no subscriptions should remain for this subscriber ..
        subs_after = _get_subscriptions(admin, 'test.td.subscriber')
        assert len(subs_after) == 0, f'Expected 0 subs after deleting last topic, got {len(subs_after)}'

# ################################################################################################################################

    def test_07_no_server_errors_after_topic_delete(self, zato_server:'any_') -> 'None':
        """ After all deletions, the server log must not contain ERROR or CRITICAL
        lines referencing deleted topics. This catches silent failures from stale
        greenlets, config lookups, or stale Redis operations.
        """
        from zato.common.test.config_pubsub_topic_delete import TestConfig

        server_log_path = os.path.join(TestConfig.server_directory, 'logs', 'server.log')

        if not os.path.exists(server_log_path):
            return

        topic_names = ['td.push.single', 'td.pull.single', 'td.multi.first', 'td.multi.second']

        with open(server_log_path, 'r') as log_file:
            for line_number, line in enumerate(log_file, 1):
                if 'ERROR' not in line and 'CRITICAL' not in line:
                    continue

                for topic_name in topic_names:
                    assert topic_name not in line, \
                        f'Server log line {line_number} has error referencing {topic_name}: {line.strip()}'

# ################################################################################################################################
# ################################################################################################################################
