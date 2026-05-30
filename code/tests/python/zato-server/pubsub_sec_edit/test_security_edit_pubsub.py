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
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_sec_edit')

_settle_time = 1.0

_new_username = 'test.secedit.subscriber.renamed'
_new_sec_name = 'test.secedit.subscriber.renamed'

# ################################################################################################################################
# ################################################################################################################################

def _get_admin() -> 'any_':
    from zato.common.test.client import AdminClient
    from zato.common.test.config_pubsub_sec_edit import TestConfig
    admin = AdminClient(TestConfig.base_url, TestConfig.invoke_password)
    return admin

# ################################################################################################################################

def _get_publisher() -> 'any_':
    from zato.common.test.client import PublishClient
    from zato.common.test.config_pubsub_sec_edit import TestConfig
    publisher = PublishClient(TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)
    return publisher

# ################################################################################################################################

def _get_puller() -> 'any_':
    from zato.common.test.client import PullClient
    from zato.common.test.config_pubsub_sec_edit import TestConfig
    puller = PullClient(TestConfig.base_url, TestConfig.subscriber_username, TestConfig.subscriber_password)
    return puller

# ################################################################################################################################

def _get_puller_new_username() -> 'any_':
    from zato.common.test.client import PullClient
    from zato.common.test.config_pubsub_sec_edit import TestConfig
    puller = PullClient(TestConfig.base_url, _new_username, TestConfig.subscriber_password)
    return puller

# ################################################################################################################################

def _edit_subscriber_username(admin:'any_') -> 'None':
    """ Edits the subscriber's username via the admin API.
    """
    from zato.common.test.config_pubsub_sec_edit import TestConfig

    _ = admin.invoke('zato.security.basic-auth.edit', {
        'id': TestConfig.subscriber_sec_base_id,
        'name': TestConfig.subscriber_sec_name,
        'is_active': True,
        'username': _new_username,
        'realm': 'testrealm',
        'cluster_id': 1,
    })

# ################################################################################################################################

def _edit_subscriber_sec_name(admin:'any_') -> 'None':
    """ Edits the subscriber's security definition name via the admin API.
    """
    from zato.common.test.config_pubsub_sec_edit import TestConfig

    _ = admin.invoke('zato.security.basic-auth.edit', {
        'id': TestConfig.subscriber_sec_base_id,
        'name': _new_sec_name,
        'is_active': True,
        'username': _new_username,
        'realm': 'testrealm',
        'cluster_id': 1,
    })

# ################################################################################################################################
# ################################################################################################################################

class TestSecurityEditPubSub:
    """ Verifies that editing a security definition's username or name correctly
    updates pub/sub in-memory state (Gaps 26 and 27).
    """

# ################################################################################################################################

    def test_01_baseline_publish_subscribe_works(self, zato_server:'any_') -> 'None':
        """ Setup validation: subscriber can pull messages before any edit.
        """
        publisher = _get_publisher()
        puller = _get_puller()

        puller.drain()

        _ = publisher.publish('secedit.topic.single', 'baseline-payload')

        time.sleep(_settle_time)

        result = puller.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message, got {message_count}'

# ################################################################################################################################

    def test_02_username_change_pull_still_works(self, zato_server:'any_') -> 'None':
        """ GAP 26: After editing the subscriber's username, pull with new credentials
        succeeds - proves SubscriptionsStore.update_username moved the sub_key mapping.
        """
        admin = _get_admin()
        puller = _get_puller()

        puller.drain()

        # .. change the username ..
        _edit_subscriber_username(admin)

        time.sleep(_settle_time)

        # .. pull with new credentials must succeed ..
        puller_new = _get_puller_new_username()
        result = puller_new.pull(max_messages=50)

        # .. message_count can be 0 (empty queue is fine), the point is no 401 ..
        assert 'message_count' in result, f'Expected successful pull response, got {result}'

# ################################################################################################################################

    def test_03_username_change_publish_permitted(self, zato_server:'any_') -> 'None':
        """ GAP 27: After username edit, publish a new message and pull with new
        credentials - proves PatternMatcher.change_client_id moved the permissions.
        """
        publisher = _get_publisher()
        puller_new = _get_puller_new_username()

        puller_new.drain()

        _ = publisher.publish('secedit.topic.single', 'after-username-change')

        time.sleep(_settle_time)

        result = puller_new.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message after username change, got {message_count}'

# ################################################################################################################################

    def test_04_old_username_pull_fails(self, zato_server:'any_') -> 'None':
        """ GAP 26+27 negative: Pull with old credentials returns 401 - proves
        old username is fully gone from both stores.
        """
        puller_old = _get_puller()

        try:
            _ = puller_old.pull(max_messages=50)
            assert False, 'Expected pull with old credentials to fail'
        except Exception as exc:
            # .. 401 proves the old credentials are rejected ..
            assert '401' in str(exc), f'Expected 401 error, got: {exc}'

# ################################################################################################################################

    def test_05_sec_name_change_pull_still_works(self, zato_server:'any_') -> 'None':
        """ GAP 26 (sec_name sub-case): After editing the sec def name (not username),
        pull still works - proves update_sec_name kept the mapping consistent.
        """
        admin = _get_admin()
        publisher = _get_publisher()
        puller_new = _get_puller_new_username()

        puller_new.drain()

        # .. change the sec def name ..
        _edit_subscriber_sec_name(admin)

        time.sleep(_settle_time)

        # .. publish and pull - must still work ..
        _ = publisher.publish('secedit.topic.single', 'after-sec-name-change')

        time.sleep(_settle_time)

        result = puller_new.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 1, f'Expected at least 1 message after sec_name change, got {message_count}'

# ################################################################################################################################

    def test_06_full_round_trip_after_both_changes(self, zato_server:'any_') -> 'None':
        """ GAP 26+27 combined: Publish to both topics, pull all messages with
        final credentials - proves end-to-end correctness after username and
        sec_name changes.
        """
        publisher = _get_publisher()
        puller_new = _get_puller_new_username()

        puller_new.drain()

        _ = publisher.publish('secedit.topic.single', 'final-round-trip-single')
        _ = publisher.publish('secedit.topic.multi', 'final-round-trip-multi')

        time.sleep(_settle_time)

        result = puller_new.pull(max_messages=50)
        message_count = result['message_count']

        assert message_count >= 2, f'Expected at least 2 messages in final round trip, got {message_count}'

# ################################################################################################################################
# ################################################################################################################################
