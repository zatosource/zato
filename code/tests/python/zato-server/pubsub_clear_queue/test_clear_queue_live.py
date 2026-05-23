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

logger = logging.getLogger('zato.test.pubsub_clear_queue.live')

_topic_1 = 'clear.test.topic.1'
_topic_2 = 'clear.test.topic.2'

_settle_time = 2.0

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

    raise RuntimeError(f'No subscription found for username: {username}')

# ################################################################################################################################
# ################################################################################################################################

def _publish_messages(publish_client:'any_', topic_name:'str', count:'int') -> 'strlist':
    """ Publishes `count` messages and returns their msg_ids.
    """
    msg_ids:'strlist' = []

    for idx in range(count):
        result = publish_client.publish(topic_name, f'clear-test-payload-{idx}')
        msg_id = result['msg_id']
        msg_ids.append(msg_id)

    return msg_ids

# ################################################################################################################################
# ################################################################################################################################

class TestClearViaBrowse:
    """ Clear via service, then verify browse shows empty queue.
    """

    def test_clear_then_browse_empty(self, zato_server:'any_') -> 'None':

        from _client import AdminClient, PublishClient
        from config import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. publish 10 messages ..
        _ = _publish_messages(publisher, _topic_1, 10)
        time.sleep(_settle_time)

        # .. clear the queue ..
        clear_result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})
        logger.info('Clear result: %s', clear_result)

        # .. browse and verify empty.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'pending',
        })

        assert browse_result['total'] == 0
        assert browse_result['rows'] == []

# ################################################################################################################################
# ################################################################################################################################

class TestClearThenPublishNew:
    """ After clearing, new messages should arrive and be fetchable.
    """

    def test_clear_then_new_messages(self, zato_server:'any_') -> 'None':

        from _client import AdminClient, PublishClient, PullClient
        from config import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. publish and clear old messages ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 5 new messages ..
        _ = _publish_messages(publisher, _topic_1, 5)
        time.sleep(_settle_time)

        # .. pull and verify exactly 5 new messages.
        pull_result = puller.pull(max_messages=50)
        assert pull_result['message_count'] == 5

# ################################################################################################################################
# ################################################################################################################################

class TestClearReturnsCorrectCount:
    """ Verify cleared_count matches the number of published messages.
    """

    def test_cleared_count(self, zato_server:'any_') -> 'None':

        from _client import AdminClient, PublishClient
        from config import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. drain any leftover messages first ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 20 messages ..
        _ = _publish_messages(publisher, _topic_1, 20)
        time.sleep(_settle_time)

        # .. clear and check count.
        clear_result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})
        assert clear_result['cleared_count'] == 20

# ################################################################################################################################
# ################################################################################################################################

class TestClearEmptyQueueViaService:
    """ Clearing an empty queue returns cleared_count: 0, no error.
    """

    def test_clear_empty_queue(self, zato_server:'any_') -> 'None':

        from _client import AdminClient
        from config import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        sub_key = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. clear again.
        result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})
        assert result['cleared_count'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestClearWithPartiallyDelivered:
    """ Publish 5, pull 2 (delivered), clear, verify remaining are cleared.
    """

    def test_clear_after_partial_pull(self, zato_server:'any_') -> 'None':

        from _client import AdminClient, PublishClient, PullClient
        from config import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 5 ..
        _ = _publish_messages(publisher, _topic_1, 5)
        time.sleep(_settle_time)

        # .. pull 2 (they are delivered and removed from the queue) ..
        _ = puller.pull(max_messages=2)

        # .. clear remaining ..
        clear_result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. the remaining 3 should be cleared ..
        assert clear_result['cleared_count'] == 3

        # .. verify queue is empty.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'pending',
        })

        assert browse_result['total'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestDiskFilesCleanedUp:
    """ Verify on-disk message files are removed after clearing.
    """

    def test_disk_cleanup(self, zato_server:'any_') -> 'None':

        from _client import AdminClient, PublishClient
        from config import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 10 messages ..
        _ = _publish_messages(publisher, _topic_1, 10)
        time.sleep(_settle_time)

        # .. verify files exist on disk ..
        pubsub_messages_dir = os.path.join(TestConfig.server_directory, 'work', 'pubsub-messages')
        topic_dir = os.path.join(pubsub_messages_dir, _topic_1)

        if os.path.isdir(topic_dir):
            files_before = os.listdir(topic_dir)
            assert len(files_before) > 0

        # .. clear ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. verify files are gone (or directory is empty).
        if os.path.isdir(topic_dir):
            files_after = os.listdir(topic_dir)
            assert len(files_after) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestClearOneSubscriberLeavesOther:
    """ Two subscribers on the same topic - clearing one does not affect the other.
    """

    def test_clear_one_leaves_other(self, zato_server:'any_') -> 'None':

        from _client import AdminClient, PublishClient, PullClient
        from config import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller_b = PullClient(TestConfig.base_url, TestConfig.puller_b_username, TestConfig.puller_b_password)

        sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)
        sub_key_b = _get_sub_key(admin, TestConfig.puller_b_username)

        # .. ensure both empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_b})

        # .. publish 5 messages to topic_1 (both A and B are subscribed) ..
        _ = _publish_messages(publisher, _topic_1, 5)
        time.sleep(_settle_time)

        # .. clear subscriber A's queue ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})

        # .. subscriber B should still have 5 pending messages ..
        browse_b = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_b,
            'state': 'pending',
        })

        assert browse_b['total'] == 5

        # .. B can still pull them.
        pull_result = puller_b.pull(max_messages=50)
        assert pull_result['message_count'] == 5

# ################################################################################################################################
# ################################################################################################################################
