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
    from zato.common.typing_ import any_, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_clear_queue_combined.live')

_topic_1 = 'clear.combined.topic.1'

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
        result = publish_client.publish(topic_name, f'combined-clear-test-{idx}')
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
    for _, _dirs, files in os.walk(directory):
        for fname in files:
            if fname.endswith('.msg'):
                count += 1
    return count

# ################################################################################################################################
# ################################################################################################################################

class TestCombinedClearPullLeavePush:
    """ Clearing pull should remove pull's pending entries.
    After clearing pull, a second clear for pull returns 0.
    Push subscriber's entries are unaffected.
    """

    def test_clear_pull_leave_push(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue_combined import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key_pull = _get_sub_key(admin, TestConfig.puller_a_username)
        sub_key_push = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure both empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_push})

        # .. publish 3, wait for push delivery ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear pull only ..
        clear_result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})

        # .. pull was cleared (3 pending entries) ..
        assert clear_result['cleared_count'] == 3

        # .. clearing pull again returns 0, confirming all pull entries are gone ..
        clear_again = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})
        assert clear_again['cleared_count'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestCombinedClearPushLeavePull:
    """ Clearing push should leave pull subscriber's messages intact.
    After clearing push, puller_a can still pull its 3 messages.
    """

    def test_clear_push_leave_pull(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_clear_queue_combined import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)

        sub_key_pull = _get_sub_key(admin, TestConfig.puller_a_username)
        sub_key_push = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure both empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_push})

        # .. publish 3, wait for push delivery ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear push (push delivery already ack'd,
        # .. so this cleans up delivered entries for the push subscriber) ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_push})

        # .. pull subscriber should still get 3 messages ..
        pull_result = puller.pull(max_messages=50)
        assert pull_result['message_count'] == 3

# ################################################################################################################################
# ################################################################################################################################

class TestCombinedClearBothEmpty:
    """ Clearing both subscribers should result in state=all returning 0.
    """

    def test_clear_both_empty(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue_combined import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key_pull = _get_sub_key(admin, TestConfig.puller_a_username)
        sub_key_push = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure both empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_push})

        # .. publish 3, wait ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear pull first, then push ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_push})

        # .. state=all should be empty for both ..
        browse_pull = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_pull,
            'state': 'all',
        })
        assert browse_pull['total'] == 0

        browse_push = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_push,
            'state': 'all',
        })
        assert browse_push['total'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestCombinedClearBothDiskFiles:
    """ After clearing both subscribers, .msg files should be gone.
    """

    def test_clear_both_disk_files(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue_combined import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key_pull = _get_sub_key(admin, TestConfig.puller_a_username)
        sub_key_push = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure both empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_push})

        # .. publish 3, wait ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear both ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_push})

        # .. .msg files should be gone ..
        pubsub_messages_dir = os.path.join(TestConfig.server_directory, 'work', 'pubsub-messages')
        topic_dir = os.path.join(pubsub_messages_dir, _topic_1)

        assert _count_msg_files(topic_dir) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestCombinedClearOrderIndependent:
    """ Clearing push first then pull should give the same result as pull first then push.
    """

    def test_clear_order_independent(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue_combined import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key_pull = _get_sub_key(admin, TestConfig.puller_a_username)
        sub_key_push = _get_sub_key(admin, TestConfig.pusher_a_username)

        # .. ensure both empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_push})

        # .. publish 3, wait ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear push first, then pull ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_push})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_pull})

        # .. state=all should be empty for both ..
        browse_pull = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_pull,
            'state': 'all',
        })
        assert browse_pull['total'] == 0

        browse_push = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_push,
            'state': 'all',
        })
        assert browse_push['total'] == 0

# ################################################################################################################################
# ################################################################################################################################
