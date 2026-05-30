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

logger = logging.getLogger('zato.test.pubsub_topic_rename')

_settle_time = 3.0

_original_topic_name = 'test.rename.topic1'
_renamed_topic_name  = 'test.rename.topic1.renamed'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_topic_rename import TestConfig
    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_topic_rename import TestConfig
    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _get_puller() -> 'any_':
    from zato.common.test.client import PullClient
    from zato.common.test.config_pubsub_topic_rename import TestConfig
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

class TestTopicRename:
    """ Verifies that topic rename and deactivation propagate correctly
    through all in-memory structures and Redis.
    """

# ################################################################################################################################

    def test_01_initial_state(self, zato_server:'any_') -> 'None':
        """ Verify the topic exists and there is a subscription to it.
        """
        admin = _get_admin()

        # .. verify the topic exists ..
        topic_id = _get_topic_id(admin, _original_topic_name)
        assert topic_id > 0

        # .. verify the subscriber has a subscription ..
        subs = _get_subscriptions(admin, 'test.rename.subscriber')
        assert len(subs) == 1, f'Expected 1 subscription, got {len(subs)}'

# ################################################################################################################################

    def test_02_publish_before_rename(self, zato_server:'any_') -> 'None':
        """ Verify we can publish and pull before any rename.
        """
        publisher = _get_publisher()
        puller = _get_puller()

        _ = publisher.publish(_original_topic_name, 'pre-rename-message')
        time.sleep(_settle_time)

        result = puller.pull(max_messages=10)
        message_count = result['message_count']
        assert message_count >= 1, f'Expected at least 1 message, got {message_count}'

# ################################################################################################################################

    def test_03_rename_topic(self, zato_server:'any_') -> 'None':
        """ Rename the topic and verify the ODB reflects the new name.
        """
        admin = _get_admin()

        topic_id = _get_topic_id(admin, _original_topic_name)

        _ = admin.invoke('zato.pubsub.topic.edit', {
            'id': topic_id,
            'cluster_id': 1,
            'name': _renamed_topic_name,
            'is_active': True,
        })

        time.sleep(_settle_time)

        # .. verify the old name is gone and the new name exists ..
        topic_list = admin.invoke('zato.pubsub.topic.get-list', {'cluster_id': 1})

        if isinstance(topic_list, list):
            items = topic_list
        else:
            items = topic_list['zato_pubsub_topic_get_list_response']

        topic_names:'anylist' = []
        for item in items:
            topic_names.append(item['name'])

        assert _renamed_topic_name in topic_names, f'Renamed topic not found in {topic_names}'
        assert _original_topic_name not in topic_names, f'Old topic name still present in {topic_names}'

# ################################################################################################################################

    def test_04_publish_and_pull_after_rename(self, zato_server:'any_') -> 'None':
        """ Publish to the renamed topic and pull messages.
        This proves pubsub_subs was re-keyed (GAP 6) and Redis streams were renamed.
        """
        publisher = _get_publisher()
        puller = _get_puller()

        _ = publisher.publish(_renamed_topic_name, 'post-rename-message')
        time.sleep(_settle_time)

        result = puller.pull(max_messages=10)
        message_count = result['message_count']
        assert message_count >= 1, f'Expected at least 1 message after rename, got {message_count}'

# ################################################################################################################################

    def test_05_subscription_shows_new_topic_name(self, zato_server:'any_') -> 'None':
        """ Verify the subscription's topic list reflects the renamed topic.
        """
        admin = _get_admin()

        subs = _get_subscriptions(admin, 'test.rename.subscriber')
        assert len(subs) == 1, f'Expected 1 subscription, got {len(subs)}'

        topic_name_list = subs[0]['topic_name_list']

        topic_names:'anylist' = []
        for entry in topic_name_list:
            topic_names.append(entry['topic_name'])

        assert _renamed_topic_name in topic_names, f'Renamed topic not in subscription topic list: {topic_names}'
        assert _original_topic_name not in topic_names, f'Old topic still in subscription topic list: {topic_names}'

# ################################################################################################################################

    def test_06_deactivate_blocks_publishing(self, zato_server:'any_') -> 'None':
        """ Set is_active=False and verify that publishing is rejected (GAP 8).
        """
        admin = _get_admin()
        publisher = _get_publisher()

        topic_id = _get_topic_id(admin, _renamed_topic_name)

        # .. deactivate the topic ..
        _ = admin.invoke('zato.pubsub.topic.edit', {
            'id': topic_id,
            'cluster_id': 1,
            'name': _renamed_topic_name,
            'is_active': False,
        })

        time.sleep(_settle_time)

        # .. attempt to publish - should be rejected ..
        try:
            _ = publisher.publish(_renamed_topic_name, 'should-be-rejected')
            was_rejected = False
        except Exception as publish_error:
            error_text = str(publish_error)
            was_rejected = '403' in error_text
            if not was_rejected:
                raise

        assert was_rejected, 'Publishing to an inactive topic should have been rejected with 403'

# ################################################################################################################################

    def test_07_reactivate_resumes_publishing(self, zato_server:'any_') -> 'None':
        """ Set is_active=True and verify that publishing works again.
        """
        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        topic_id = _get_topic_id(admin, _renamed_topic_name)

        # .. reactivate the topic ..
        _ = admin.invoke('zato.pubsub.topic.edit', {
            'id': topic_id,
            'cluster_id': 1,
            'name': _renamed_topic_name,
            'is_active': True,
        })

        time.sleep(_settle_time)

        # .. publish should succeed now ..
        _ = publisher.publish(_renamed_topic_name, 'post-reactivation-message')
        time.sleep(_settle_time)

        result = puller.pull(max_messages=10)
        message_count = result['message_count']
        assert message_count >= 1, f'Expected at least 1 message after reactivation, got {message_count}'

# ################################################################################################################################
# ################################################################################################################################
