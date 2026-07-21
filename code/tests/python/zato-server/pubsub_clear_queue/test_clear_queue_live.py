# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time

# Zato
from zato.common.test import pubsub_db

if 0:
    from zato.common.typing_ import any_, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_clear_queue.live')

_topic_1 = 'clear.test.topic.1'
_topic_2 = 'clear.test.topic.2'

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

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

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

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

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

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. drain any leftover messages first ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3 messages (maxlen=3 in tests, so publish exactly maxlen) ..
        _ = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear and check count (at least 3, may include delivered leftovers from prior tests on shared topics).
        clear_result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})
        assert clear_result['cleared_count'] >= 3

# ################################################################################################################################
# ################################################################################################################################

class TestClearEmptyQueueViaService:
    """ Clearing an empty queue returns cleared_count: 0, no error.
    """

    def test_clear_empty_queue(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

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
    """ Publish 3, pull 2 (delivered), clear, verify remaining are cleared.
    Uses topic_2 (sole subscriber) so maxlen=3 fits exactly.
    """

    def test_clear_after_partial_pull(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3 to topic_2 (sole subscriber, maxlen=3) ..
        _ = _publish_messages(publisher, _topic_2, 3)
        time.sleep(_settle_time)

        # .. pull 2 (they are delivered and acked) ..
        _ = puller.pull(max_messages=2)

        # .. clear remaining ..
        clear_result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. at least 1 remaining should be cleared ..
        assert clear_result['cleared_count'] >= 1

        # .. verify queue is empty.
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key,
            'state': 'pending',
        })

        assert browse_result['total'] == 0

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadsDroppedOnClear:
    """ Verify stored payloads are dropped after clearing.
    Uses topic_2 (sole subscriber) so payloads can be fully removed.
    """

    def test_payloads_dropped(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. publish 3 messages to topic_2 (sole subscriber) ..
        msg_ids = _publish_messages(publisher, _topic_2, 3)
        time.sleep(_settle_time)

        # .. verify the payloads are stored in the database ..
        assert pubsub_db.count_messages_with_payload(msg_ids) == 3

        # .. clear ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key})

        # .. verify the payloads are gone while the rows stay behind as traces.
        assert pubsub_db.count_messages_with_payload(msg_ids) == 0
        assert pubsub_db.count_message_rows(msg_ids) == 3

# ################################################################################################################################
# ################################################################################################################################

class TestClearOneSubscriberLeavesOther:
    """ Two subscribers on the same topic - clearing one does not affect the other.
    """

    def test_clear_one_leaves_other(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

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

class TestClearLeavesDeliveredTraces:
    """ Clear removes everything pending while the cleared messages remain visible
    in state=all as payload-less delivered traces.
    Uses topic_2 where only A is subscribed.
    """

    def test_clear_state_all_keeps_traces(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})

        # .. publish 3 messages to topic_2 (only A is subscribed) ..
        msg_ids = _publish_messages(publisher, _topic_2, 3)
        time.sleep(_settle_time)

        # .. clear the queue ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})

        # .. browse state=pending should be empty ..
        browse_result = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_a,
            'state': 'pending',
        })

        assert browse_result['total'] == 0
        assert browse_result['rows'] == []

        # .. while the cleared messages stay behind as payload-less traces.
        assert pubsub_db.count_message_rows(msg_ids) == 3
        assert pubsub_db.count_messages_with_payload(msg_ids) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadSurvivesForOtherSub:
    """ Payloads stay in the database when another subscriber still needs them.
    """

    def test_clear_one_payload_other_keeps(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)
        sub_key_b = _get_sub_key(admin, TestConfig.puller_b_username)

        # .. ensure both empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_b})

        # .. publish 3 messages to topic_1 (both A and B subscribed) ..
        msg_ids = _publish_messages(publisher, _topic_1, 3)
        time.sleep(_settle_time)

        # .. clear A's queue ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})

        # .. B should still have 3 pending ..
        browse_b = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_b,
            'state': 'pending',
        })

        assert browse_b['total'] == 3

        # .. and the payloads must still be there because B has not acknowledged them ..
        assert pubsub_db.count_messages_with_payload(msg_ids) == 3

        # .. now clear B too ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_b})

        # .. B has nothing pending anymore and the payloads are dropped.
        browse_b_pending = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_b,
            'state': 'pending',
        })

        assert browse_b_pending['total'] == 0
        assert pubsub_db.count_messages_with_payload(msg_ids) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestNoTrimmingOnPublish:
    """ Nothing trims a queue on publish - all 4 messages stay pending until cleared,
    then all 4 remain as payload-less traces.
    Uses topic_2 where only A is subscribed.
    """

    def test_publish_four_then_clear(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})

        # .. publish 4 messages to topic_2 - no message is evicted ..
        msg_ids = _publish_messages(publisher, _topic_2, 4)
        time.sleep(_settle_time)

        # .. all 4 are pending ..
        browse_before = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_a,
            'state': 'pending',
        })

        assert browse_before['total'] == 4

        # .. clear ..
        clear_result = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})
        assert clear_result['cleared_count'] == 4

        # .. nothing is pending anymore and all 4 rows stay behind as traces.
        browse_after = admin.invoke('zato.pubsub.subscription.browse-queue', {
            'sub_key': sub_key_a,
            'state': 'pending',
        })

        assert browse_after['total'] == 0
        assert browse_after['rows'] == []

        assert pubsub_db.count_message_rows(msg_ids) == 4
        assert pubsub_db.count_messages_with_payload(msg_ids) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestClearThenPublishNewUnderMaxlen:
    """ Publish 2 (under maxlen=3), clear, then publish 3 more. New messages should be pullable.
    Uses topic_2 where only A is subscribed.
    """

    def test_clear_then_new_under_maxlen(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient, PullClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
        puller = PullClient(TestConfig.base_url, TestConfig.puller_a_username, TestConfig.puller_a_password)

        sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})

        # .. publish 2 to topic_2 ..
        _ = _publish_messages(publisher, _topic_2, 2)
        time.sleep(_settle_time)

        # .. clear ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})

        # .. publish 3 new messages to topic_2 ..
        _ = _publish_messages(publisher, _topic_2, 3)
        time.sleep(_settle_time)

        # .. pull and verify exactly 3.
        pull_result = puller.pull(max_messages=50)
        assert pull_result['message_count'] == 3

# ################################################################################################################################
# ################################################################################################################################

class TestClearDropsPayloadsSoleSub:
    """ Payloads should be dropped when clearing the sole subscriber's queue,
    with no pending delivery rows left behind.
    """

    def test_payloads_gone_after_clear(self, zato_server:'any_') -> 'None':

        from zato.common.test.client import AdminClient, PublishClient
        from zato.common.test.config_pubsub_clear_queue import TestConfig

        admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
        publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

        sub_key_a = _get_sub_key(admin, TestConfig.puller_a_username)

        # .. ensure empty ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})

        # .. publish 3 messages to topic_2 (only A is subscribed) ..
        msg_ids = _publish_messages(publisher, _topic_2, 3)
        time.sleep(_settle_time)

        # .. verify the payloads are stored ..
        assert pubsub_db.count_messages_with_payload(msg_ids) == 3

        # .. clear ..
        _ = admin.invoke('zato.pubsub.subscription.clear-queue', {'sub_key': sub_key_a})

        # .. verify the payloads are gone and nothing is pending anymore.
        assert pubsub_db.count_messages_with_payload(msg_ids) == 0
        assert pubsub_db.count_pending(sub_key_a, _topic_2) == 0

# ################################################################################################################################
# ################################################################################################################################
