# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import time

if 0:
    from zato.common.typing_ import any_, anydict, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_clear_queue_push.live')

_topic_1 = 'clear.push.topic.1'
_topic_2 = 'clear.push.topic.2'

_settle_time = 2.0

# ################################################################################################################################
# ################################################################################################################################

def _get_sub_key(admin_client:'any_', username:'str') -> 'str':
    """ Looks up the sub_key for a given security username via the admin API.
    """
    result = admin_client.invoke('zato.pubsub.subscription.get-list', {'cluster_id': 1})

    if isinstance(result, list):
        items:'anylist' = result
    else:
        items = result['zato_pubsub_subscription_get_list_response']

    for item in items:
        sec_name = item['sec_name']
        if sec_name == username:
            return item['sub_key']

    raise RuntimeError(f'No subscription found for username: {username}')

# ################################################################################################################################
# ################################################################################################################################

def _publish_messages(publish_client:'any_', topic_name:'str', count:'int') -> 'strlist':
    """ Publishes `count` messages and returns their msg_ids.
    """
    msg_ids:'strlist' = []

    for idx in range(count):
        result = publish_client.publish(topic_name, f'push-clear-test-{idx}')
        msg_id = result['msg_id']
        msg_ids.append(msg_id)

    return msg_ids

# ################################################################################################################################
# ################################################################################################################################

def _count_msg_files(directory:'str') -> 'int':
    """ Counts .msg files recursively in a directory.
    """
    count = 0
    if not os.path.isdir(directory):
        return 0
    for root, _dirs, files in os.walk(directory):
        for fname in files:
            if fname.endswith('.msg'):
                count += 1
    return count

# ################################################################################################################################
# ################################################################################################################################

class TestPushClearBasic:
    """ Publish to a push-only topic, wait for delivery, clear, verify state=all is empty.
    """

    def test_push_clear_basic(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue_push import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3 messages, wait for push delivery ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear (push delivery may have already ack'd everything,
        # .. so cleared_count can be 0 or more) ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. state=all should be empty.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'all',
        })

        assert browse_result['total'] == 0
        assert browse_result['rows'] == []

# ################################################################################################################################
# ################################################################################################################################

class TestPushClearEmpty:
    """ Clearing an empty push queue returns cleared_count: 0, no error.
    """

    def test_push_clear_empty(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient
        from zato.common.test.config_pubsub_clear_queue_push import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        sub_key = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. clear again.
        result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})
        assert result['cleared_count'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestPushClearDiskFiles:
    """ Verify that after clearing a push subscriber's queue, no .msg files remain.
    Push delivery acks messages and deletes disk files on its own,
    so this test verifies the combined effect.
    """

    def test_push_disk_files_gone(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue_push import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3, wait for push delivery ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear to remove any remaining stream/pending entries ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. verify .msg files are gone (push ack deletes them during delivery,
        # .. clear_queue removes any that might remain).
        pubsub_messages_dir = os.path.join(TestConfig.server_directory, 'work', 'pubsub-messages')
        topic_dir = os.path.join(pubsub_messages_dir, _topic_1)

        assert _count_msg_files(topic_dir) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestPushClearThenPublishNew:
    """ Clear after push delivery, publish more, verify the new batch is also clearable.
    """

    def test_push_clear_then_new(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue_push import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3, wait, clear ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3 more, wait ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear again ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. state=all should be empty.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'all',
        })

        assert browse_result['total'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestPushClearStateAllEmpty:
    """ After clearing a push subscriber, browse state=all returns zero entries.
    """

    def test_push_state_all_empty(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue_push import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3 to topic_2, wait ..
        _ = _publish_messages(publisher, _topic_2, 3)
        time.sleep(_settle_time)

        # .. clear ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. browse state=all on topic_2 should be empty.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'all',
        })

        assert browse_result['total'] == 0
        assert browse_result['rows'] == []

# ################################################################################################################################
# ################################################################################################################################
