# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time

if 0:
    from zato.common.typing_ import any_, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_clear_queue_concurrent.live')

_topic_1 = 'clear.concurrent.topic.1'

_settle_time = 0.1

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
            out = item['sub_key']
            return out

    raise RuntimeError(f'No subscription found for username: {username}')

# ################################################################################################################################
# ################################################################################################################################

def _publish_messages(publish_client:'any_', topic_name:'str', count:'int') -> 'strlist':
    """ Publishes `count` messages and returns their msg_ids.
    """
    msg_ids:'strlist' = []

    for idx in range(count):
        result = publish_client.publish(topic_name, f'concurrent-clear-test-{idx}')
        msg_id = result['msg_id']
        msg_ids.append(msg_id)

    return msg_ids

# ################################################################################################################################
# ################################################################################################################################
#
# Gap: Concurrent publish during clear_queue can lose new messages
#
# The old code did DEL sub_pending_key after iterating all messages.
# A publish landing between the last per-message cleanup and the DEL
# would have its sub_pending entry wiped, making the message invisible
# to browse-queue despite existing in the stream.
#
# ################################################################################################################################
# ################################################################################################################################

class TestPublishDuringClearIsNotLost:

    def test_publish_during_clear_not_lost(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_clear_queue_concurrent import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.puller_username, TestConfig.puller_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_username)

        # .. ensure the queue is empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3 messages ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear the queue ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. immediately publish 2 new messages (no sleep, simulating concurrent publish) ..
        _ = _publish_messages(publisher, _topic_1, 2)
        time.sleep(_settle_time)

        # .. pull and verify exactly 2 new messages are available ..
        pull_result = puller.pull(max_messages=50)
        assert pull_result['message_count'] == 2

        # .. verify the queue is now empty after pulling.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'pending',
        })

        assert browse_result['total'] == 0

# ################################################################################################################################
# ################################################################################################################################
#
# Gap: Sub_pending consistency after clear + publish
#
# After clearing, sub_pending must accurately reflect only messages
# published after the clear. It must not be wiped by a stale DEL.
#
# ################################################################################################################################
# ################################################################################################################################

class TestSubPendingConsistencyAfterClear:

    def test_sub_pending_consistency(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue_concurrent import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_username)

        # .. ensure the queue is empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3 messages ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear the queue ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 2 new messages ..
        _ = _publish_messages(publisher, _topic_1, 2)
        time.sleep(_settle_time)

        # .. browse pending must show exactly 2.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'pending',
        })

        assert browse_result['total'] == 2

# ################################################################################################################################
# ################################################################################################################################
#
# Gap: Multiple rapid clear+publish cycles must never lose messages
#
# Repeated clear+publish cycles stress the sub_pending set management.
# Each cycle publishes, clears, immediately publishes again, then pulls.
# Every post-clear message must be pullable.
#
# ################################################################################################################################
# ################################################################################################################################

class TestRapidClearPublishCycles:

    def test_rapid_cycles(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_clear_queue_concurrent import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.puller_username, TestConfig.puller_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_username)

        # .. ensure the queue is empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. run 5 cycles of publish-clear-publish-pull ..
        for _ in range(5):

            # .. publish 2 messages ..
            _ = _publish_messages(publisher, _topic_1, 2)
            time.sleep(_settle_time)

            # .. clear the queue ..
            _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

            # .. immediately publish 1 new message ..
            _ = _publish_messages(publisher, _topic_1, 1)
            time.sleep(_settle_time)

            # .. pull and verify the new message is available ..
            pull_result = puller.pull(max_messages=50)
            assert pull_result['message_count'] == 1

        # .. after all cycles, the queue must be empty.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'pending',
        })

        assert browse_result['total'] == 0

# ################################################################################################################################
# ################################################################################################################################
