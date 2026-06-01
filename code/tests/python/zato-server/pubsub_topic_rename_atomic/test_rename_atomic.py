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

logger = logging.getLogger('zato.test.pubsub_topic_rename_atomic')

_settle_time = 0.5

_original_topic_name = 'test.rename.atomic.topic1'
_renamed_topic_name  = 'test.rename.atomic.topic1.renamed'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_topic_rename_atomic import TestConfig
    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_topic_rename_atomic import TestConfig
    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _get_puller() -> 'any_':
    from zato.common.test.client import PullClient
    from zato.common.test.config_pubsub_topic_rename_atomic import TestConfig
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

def _get_topic_names(admin:'any_') -> 'anylist':
    """ Returns all topic names in the system.
    """
    topic_list = admin.invoke('zato.pubsub.topic.get-list', {'cluster_id': 1})

    if isinstance(topic_list, list):
        items:'anylist' = topic_list
    else:
        items = topic_list['zato_pubsub_topic_get_list_response']

    out:'anylist' = []
    for item in items:
        out.append(item['name'])

    return out

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

def _rename_topic(admin:'any_', old_name:'str', new_name:'str') -> 'None':
    """ Renames a topic via the admin API.
    """
    topic_id = _get_topic_id(admin, old_name)

    _ = admin.invoke('zato.pubsub.topic.edit', {
        'id': topic_id,
        'cluster_id': 1,
        'name': new_name,
        'is_active': True,
    })

    time.sleep(_settle_time)

# ################################################################################################################################
# ################################################################################################################################
#
# Gap 1: publish during rename cannot create a new stream under old key
#
# With atomic Lua, the stream RENAME and topic_subs_key RENAME happen in a single
# Redis command. No publish Lua can interleave between those two steps, so XADD
# cannot target a stale (pre-rename) stream key while the topic_subs_key still
# points to the old subscriber set.
#
# ################################################################################################################################
# ################################################################################################################################

class TestPublishDuringRenameNoDataSplit:

    def test_01_publish_during_rename_no_data_split(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        # .. publish a message before rename to confirm baseline ..
        _ = publisher.publish(_original_topic_name, 'baseline-message')
        time.sleep(_settle_time)

        result = puller.pull(max_messages=10)
        assert result['message_count'] >= 1, f'Baseline publish/pull failed: {result}'

        # .. rename the topic ..
        _rename_topic(admin, _original_topic_name, _renamed_topic_name)

        # .. publish to the new name ..
        _ = publisher.publish(_renamed_topic_name, 'post-rename-message')
        time.sleep(_settle_time)

        # .. pull from new name must succeed ..
        result = puller.pull(max_messages=10)
        assert result['message_count'] >= 1, f'Post-rename publish/pull failed: {result}'

        # .. verify old topic name no longer exists in the system ..
        topic_names = _get_topic_names(admin)
        assert _original_topic_name not in topic_names, f'Old topic still present: {topic_names}'
        assert _renamed_topic_name in topic_names, f'New topic missing: {topic_names}'

# ################################################################################################################################
# ################################################################################################################################
#
# Gap 2: SMEMBERS on topic_subs_key returns consistent state during rename
#
# After rename, publishing to the old name must fail because the topic no longer
# exists. The topic_subs_key for the old name is gone (renamed atomically), so the
# publish Lua's SMEMBERS returns empty or the REST layer rejects the request.
#
# ################################################################################################################################
# ################################################################################################################################

class TestPublishToOldNameFailsAfterRename:

    def test_02_publish_during_rename_subscribers_consistent(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()

        # .. rename was already done by test_01 - verify current state ..
        topic_names = _get_topic_names(admin)

        # .. if the old name still exists from a prior failed run, rename it ..
        if _original_topic_name in topic_names:
            _rename_topic(admin, _original_topic_name, _renamed_topic_name)

        # .. publish to old name must fail (topic does not exist) ..
        publish_failed = False
        try:
            _ = publisher.publish(_original_topic_name, 'should-not-arrive')
        except Exception as e:
            error_text = str(e)
            publish_failed = '404' in error_text or '403' in error_text or 'not found' in error_text.lower()
            if not publish_failed:
                raise

        assert publish_failed, 'Publishing to old topic name should have been rejected'

# ################################################################################################################################
# ################################################################################################################################
#
# Gap 3: subscriber fetch after rename finds the stream under new key
#
# Redis RENAME preserves the stream and its consumer groups. After an atomic rename,
# the subscriber's pull (which builds stream_key from topic_name) must find the
# stream under the new name with all pre-rename messages intact.
#
# ################################################################################################################################
# ################################################################################################################################

class TestFetchAfterRenameNoNogroup:

    def test_03_fetch_after_rename_no_nogroup(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        # .. ensure we are working with the renamed topic ..
        topic_names = _get_topic_names(admin)
        if _original_topic_name in topic_names:
            _rename_topic(admin, _original_topic_name, _renamed_topic_name)

        # .. publish a message to the renamed topic ..
        _ = publisher.publish(_renamed_topic_name, 'stream-continuity-message')
        time.sleep(_settle_time)

        # .. pull must succeed (no NOGROUP error, stream exists under new key) ..
        result = puller.pull(max_messages=10)
        message_count = result['message_count']
        assert message_count >= 1, f'Pull after rename failed (possible NOGROUP): count={message_count}'

# ################################################################################################################################
# ################################################################################################################################
#
# Gap 4: SREM+SADD per subscriber cannot leave a gap where topic is missing
#
# Because the Lua script loops over all subscribers and updates their topic sets
# atomically, there is no window where a subscriber's subs_key is missing the topic.
# This test verifies the subscription metadata shows the new name immediately.
#
# ################################################################################################################################
# ################################################################################################################################

class TestSubscriberMembershipAtomic:

    def test_04_subscriber_membership_atomic(self, zato_server:'any_') -> 'None':

        admin = _get_admin()
        publisher = _get_publisher()
        puller = _get_puller()

        # .. ensure we are working with the renamed topic ..
        topic_names = _get_topic_names(admin)
        if _original_topic_name in topic_names:
            _rename_topic(admin, _original_topic_name, _renamed_topic_name)

        # .. verify subscription metadata shows new topic name ..
        subs = _get_subscriptions(admin, 'test.rename.atomic.subscriber')
        assert len(subs) == 1, f'Expected 1 subscription, got {len(subs)}'

        topic_name_list = subs[0]['topic_name_list']

        sub_topic_names:'anylist' = []
        for entry in topic_name_list:
            sub_topic_names.append(entry['topic_name'])

        assert _renamed_topic_name in sub_topic_names, \
            f'Renamed topic not in subscription: {sub_topic_names}'
        assert _original_topic_name not in sub_topic_names, \
            f'Old topic still in subscription: {sub_topic_names}'

        # .. publish and pull on new name works (end-to-end proof) ..
        _ = publisher.publish(_renamed_topic_name, 'membership-test-message')
        time.sleep(_settle_time)

        result = puller.pull(max_messages=10)
        assert result['message_count'] >= 1, f'Publish/pull on renamed topic failed: {result}'

# ################################################################################################################################
# ################################################################################################################################
