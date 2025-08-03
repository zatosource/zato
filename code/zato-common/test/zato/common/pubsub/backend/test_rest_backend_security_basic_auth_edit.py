# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
import warnings

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.server.rest import PubSubRESTServer
from zato.common.pubsub.models import Subscription
from zato.broker.client import BrokerClient

# ################################################################################################################################
# ################################################################################################################################

class RESTBackendSecurityBasicAuthEditTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        self.broker_client = BrokerClient()
        self.rest_server = PubSubRESTServer('localhost', 8080)
        self.backend = RESTBackend(self.rest_server, self.broker_client)

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.old_username = 'old_user'
        self.new_username = 'new_user'
        self.old_sec_name = 'old_sec_name'
        self.new_sec_name = 'new_sec_name'
        self.password = 'test_password'

        self.username_only_cid = 'test-cid-username-only'
        self.username_only_old = 'username_only_old'
        self.username_only_new = 'username_only_new'

        self.sec_name_only_cid = 'test-cid-sec-name-only'
        self.sec_name_only_old = 'sec_name_only_old'
        self.sec_name_only_new = 'sec_name_only_new'

        self.both_changed_cid = 'test-cid-both-changed'
        self.both_old_username = 'both_old_username'
        self.both_new_username = 'both_new_username'
        self.both_old_sec_name = 'both_old_sec_name'
        self.both_new_sec_name = 'both_new_sec_name'

        self.no_changes_cid = 'test-cid-no-changes'
        self.no_changes_username = 'no_changes_username'
        self.no_changes_sec_name = 'no_changes_sec_name'

        self.multiple_topics_cid = 'test-cid-multiple-topics'
        self.multiple_topics_old_sec_name = 'multiple_topics_old_sec_name'
        self.multiple_topics_new_sec_name = 'multiple_topics_new_sec_name'
        self.multiple_topics_username = 'multiple_topics_username'

        self.nonexistent_sec_name_cid = 'test-cid-nonexistent'
        self.nonexistent_old_sec_name = 'nonexistent_old_sec_name'
        self.nonexistent_new_sec_name = 'nonexistent_new_sec_name'
        self.nonexistent_username = 'nonexistent_username'

        self.special_chars_cid = 'test-cid-special'
        self.special_chars_old_username = 'old@domain.com'
        self.special_chars_new_username = 'new@domain.com'
        self.special_chars_old_sec_name = 'old-sec-name'
        self.special_chars_new_sec_name = 'new-sec-name'

        self.unicode_cid = 'test-cid-unicode'
        self.unicode_old_username = 'old_user_ñ'
        self.unicode_new_username = 'new_user_ü'
        self.unicode_old_sec_name = 'old_sec_ñ'
        self.unicode_new_sec_name = 'new_sec_ü'

        self.numeric_cid = 12345
        self.numeric_old_username = 'numeric_old_user'
        self.numeric_new_username = 'numeric_new_user'

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_username_changed_only(self):

        # Setup initial user
        self.rest_server.users[self.username_only_old] = self.password

        # Add permissions to pattern matcher
        permissions = [{'pattern': 'test.topic.*', 'access_type': 'pub'}]
        self.backend.pattern_matcher.add_client(self.username_only_old, permissions)

        # Create the broker message with username change only
        msg = {
            'cid': self.username_only_cid,
            'has_sec_name_changed': False,
            'has_username_changed': True,
            'old_sec_name': self.username_only_old,
            'new_sec_name': self.username_only_new,
            'old_username': self.username_only_old,
            'new_username': self.username_only_new
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert old username was removed and new username was added
        self.assertNotIn(self.username_only_old, self.rest_server.users)
        self.assertIn(self.username_only_new, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.username_only_new], self.password)

        # Assert pattern matcher was updated
        self.assertNotIn(self.username_only_old, self.backend.pattern_matcher._clients)
        self.assertIn(self.username_only_new, self.backend.pattern_matcher._clients)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_sec_name_changed_only(self):

        # Setup initial subscription
        topic_name = 'test.topic'
        subscription = Subscription()
        subscription.topic_name = topic_name
        subscription.sec_name = self.sec_name_only_old
        subscription.sub_key = 'test_sub_key'

        self.backend.subs_by_topic[topic_name] = {self.sec_name_only_old: subscription}

        # Create the broker message with sec_name change only
        msg = {
            'cid': self.sec_name_only_cid,
            'has_sec_name_changed': True,
            'has_username_changed': False,
            'old_sec_name': self.sec_name_only_old,
            'new_sec_name': self.sec_name_only_new,
            'old_username': 'unchanged_username',
            'new_username': 'unchanged_username'
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert subscription was moved to new sec_name
        self.assertNotIn(self.sec_name_only_old, self.backend.subs_by_topic[topic_name])
        self.assertIn(self.sec_name_only_new, self.backend.subs_by_topic[topic_name])

        # Assert subscription object was updated
        updated_subscription = self.backend.subs_by_topic[topic_name][self.sec_name_only_new]
        self.assertEqual(updated_subscription.sec_name, self.sec_name_only_new)
        self.assertEqual(updated_subscription.topic_name, topic_name)
        self.assertEqual(updated_subscription.sub_key, 'test_sub_key')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_both_changed(self):

        # Setup initial user
        self.rest_server.users[self.both_old_username] = self.password

        # Setup initial subscription
        topic_name = 'test.topic'
        subscription = Subscription()
        subscription.topic_name = topic_name
        subscription.sec_name = self.both_old_sec_name
        subscription.sub_key = 'test_sub_key'

        self.backend.subs_by_topic[topic_name] = {self.both_old_sec_name: subscription}

        # Add permissions to pattern matcher
        permissions = [{'pattern': 'test.topic.*', 'access_type': 'pub'}]
        self.backend.pattern_matcher.add_client(self.both_old_username, permissions)

        # Create the broker message with both changes
        msg = {
            'cid': self.both_changed_cid,
            'has_sec_name_changed': True,
            'has_username_changed': True,
            'old_sec_name': self.both_old_sec_name,
            'new_sec_name': self.both_new_sec_name,
            'old_username': self.both_old_username,
            'new_username': self.both_new_username
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert username was changed
        self.assertNotIn(self.both_old_username, self.rest_server.users)
        self.assertIn(self.both_new_username, self.rest_server.users)
        self.assertEqual(self.rest_server.users[self.both_new_username], self.password)

        # Assert pattern matcher was updated
        self.assertNotIn(self.both_old_username, self.backend.pattern_matcher._clients)
        self.assertIn(self.both_new_username, self.backend.pattern_matcher._clients)

        # Assert subscription was moved to new sec_name
        self.assertNotIn(self.both_old_sec_name, self.backend.subs_by_topic[topic_name])
        self.assertIn(self.both_new_sec_name, self.backend.subs_by_topic[topic_name])

        # Assert subscription object was updated
        updated_subscription = self.backend.subs_by_topic[topic_name][self.both_new_sec_name]
        self.assertEqual(updated_subscription.sec_name, self.both_new_sec_name)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_no_changes(self):

        # Setup initial user
        self.rest_server.users[self.no_changes_username] = self.password

        # Setup initial subscription
        topic_name = 'test.topic'
        subscription = Subscription()
        subscription.topic_name = topic_name
        subscription.sec_name = self.no_changes_sec_name
        subscription.sub_key = 'test_sub_key'

        self.backend.subs_by_topic[topic_name] = {self.no_changes_sec_name: subscription}

        # Store initial state
        initial_users = dict(self.rest_server.users)
        initial_subs = dict(self.backend.subs_by_topic)

        # Create the broker message with no changes
        msg = {
            'cid': self.no_changes_cid,
            'has_sec_name_changed': False,
            'has_username_changed': False,
            'old_sec_name': self.no_changes_sec_name,
            'new_sec_name': self.no_changes_sec_name,
            'old_username': self.no_changes_username,
            'new_username': self.no_changes_username
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert nothing changed
        self.assertEqual(self.rest_server.users, initial_users)
        self.assertEqual(self.backend.subs_by_topic, initial_subs)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_multiple_topics_with_sec_name_change(self):

        # Setup initial subscriptions across multiple topics
        topic1 = 'test.topic1'
        topic2 = 'test.topic2'
        topic3 = 'test.topic3'

        subscription1 = Subscription()
        subscription1.topic_name = topic1
        subscription1.sec_name = self.multiple_topics_old_sec_name
        subscription1.sub_key = 'test_sub_key1'

        subscription2 = Subscription()
        subscription2.topic_name = topic2
        subscription2.sec_name = self.multiple_topics_old_sec_name
        subscription2.sub_key = 'test_sub_key2'

        subscription3 = Subscription()
        subscription3.topic_name = topic3
        subscription3.sec_name = 'different_sec_name'
        subscription3.sub_key = 'test_sub_key3'

        self.backend.subs_by_topic[topic1] = {self.multiple_topics_old_sec_name: subscription1}
        self.backend.subs_by_topic[topic2] = {self.multiple_topics_old_sec_name: subscription2}
        self.backend.subs_by_topic[topic3] = {'different_sec_name': subscription3}

        # Create the broker message with sec_name change
        msg = {
            'cid': self.multiple_topics_cid,
            'has_sec_name_changed': True,
            'has_username_changed': False,
            'old_sec_name': self.multiple_topics_old_sec_name,
            'new_sec_name': self.multiple_topics_new_sec_name,
            'old_username': self.multiple_topics_username,
            'new_username': self.multiple_topics_username
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert subscriptions in topic1 and topic2 were updated
        self.assertNotIn(self.multiple_topics_old_sec_name, self.backend.subs_by_topic[topic1])
        self.assertIn(self.multiple_topics_new_sec_name, self.backend.subs_by_topic[topic1])
        self.assertEqual(self.backend.subs_by_topic[topic1][self.multiple_topics_new_sec_name].sec_name, self.multiple_topics_new_sec_name)

        self.assertNotIn(self.multiple_topics_old_sec_name, self.backend.subs_by_topic[topic2])
        self.assertIn(self.multiple_topics_new_sec_name, self.backend.subs_by_topic[topic2])
        self.assertEqual(self.backend.subs_by_topic[topic2][self.multiple_topics_new_sec_name].sec_name, self.multiple_topics_new_sec_name)

        # Assert subscription in topic3 was not affected
        self.assertIn('different_sec_name', self.backend.subs_by_topic[topic3])
        self.assertEqual(self.backend.subs_by_topic[topic3]['different_sec_name'].sec_name, 'different_sec_name')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_nonexistent_sec_name(self):

        # Setup initial subscription with different sec_name
        topic_name = 'test.topic'
        subscription = Subscription()
        subscription.topic_name = topic_name
        subscription.sec_name = 'existing_sec_name'
        subscription.sub_key = 'test_sub_key'

        self.backend.subs_by_topic[topic_name] = {'existing_sec_name': subscription}

        # Store initial state
        initial_subs = dict(self.backend.subs_by_topic)

        # Create the broker message with nonexistent old sec_name
        msg = {
            'cid': self.nonexistent_sec_name_cid,
            'has_sec_name_changed': True,
            'has_username_changed': False,
            'old_sec_name': self.nonexistent_old_sec_name,
            'new_sec_name': self.nonexistent_new_sec_name,
            'old_username': self.nonexistent_username,
            'new_username': self.nonexistent_username
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert nothing changed since old sec_name doesn't exist
        self.assertEqual(self.backend.subs_by_topic, initial_subs)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_nonexistent_username(self):

        # Create the broker message with nonexistent username
        msg = {
            'cid': 'test-cid-nonexistent-user',
            'has_sec_name_changed': False,
            'has_username_changed': True,
            'old_sec_name': 'sec_name',
            'new_sec_name': 'sec_name',
            'old_username': 'nonexistent_old_user',
            'new_username': 'nonexistent_new_user'
        }

        # Store initial state
        initial_users = dict(self.rest_server.users)

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert users dict was not modified
        self.assertEqual(self.rest_server.users, initial_users)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_with_special_characters(self):

        # Setup initial user
        self.rest_server.users[self.special_chars_old_username] = self.password

        # Setup initial subscription
        topic_name = 'test.topic'
        subscription = Subscription()
        subscription.topic_name = topic_name
        subscription.sec_name = self.special_chars_old_sec_name
        subscription.sub_key = 'test_sub_key'

        self.backend.subs_by_topic[topic_name] = {self.special_chars_old_sec_name: subscription}

        # Create the broker message with special characters
        msg = {
            'cid': self.special_chars_cid,
            'has_sec_name_changed': True,
            'has_username_changed': True,
            'old_sec_name': self.special_chars_old_sec_name,
            'new_sec_name': self.special_chars_new_sec_name,
            'old_username': self.special_chars_old_username,
            'new_username': self.special_chars_new_username
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert username was changed
        self.assertNotIn(self.special_chars_old_username, self.rest_server.users)
        self.assertIn(self.special_chars_new_username, self.rest_server.users)

        # Assert subscription was moved to new sec_name
        self.assertNotIn(self.special_chars_old_sec_name, self.backend.subs_by_topic[topic_name])
        self.assertIn(self.special_chars_new_sec_name, self.backend.subs_by_topic[topic_name])

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_with_unicode_characters(self):

        # Setup initial user
        self.rest_server.users[self.unicode_old_username] = self.password

        # Setup initial subscription
        topic_name = 'test.topic'
        subscription = Subscription()
        subscription.topic_name = topic_name
        subscription.sec_name = self.unicode_old_sec_name
        subscription.sub_key = 'test_sub_key'

        self.backend.subs_by_topic[topic_name] = {self.unicode_old_sec_name: subscription}

        # Create the broker message with unicode characters
        msg = {
            'cid': self.unicode_cid,
            'has_sec_name_changed': True,
            'has_username_changed': True,
            'old_sec_name': self.unicode_old_sec_name,
            'new_sec_name': self.unicode_new_sec_name,
            'old_username': self.unicode_old_username,
            'new_username': self.unicode_new_username
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert username was changed
        self.assertNotIn(self.unicode_old_username, self.rest_server.users)
        self.assertIn(self.unicode_new_username, self.rest_server.users)

        # Assert subscription was moved to new sec_name
        self.assertNotIn(self.unicode_old_sec_name, self.backend.subs_by_topic[topic_name])
        self.assertIn(self.unicode_new_sec_name, self.backend.subs_by_topic[topic_name])

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_with_numeric_cid(self):

        # Setup initial user
        self.rest_server.users[self.numeric_old_username] = self.password

        # Create the broker message with numeric CID
        msg = {
            'cid': self.numeric_cid,
            'has_sec_name_changed': False,
            'has_username_changed': True,
            'old_sec_name': 'sec_name',
            'new_sec_name': 'sec_name',
            'old_username': self.numeric_old_username,
            'new_username': self.numeric_new_username
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert username was changed regardless of CID type
        self.assertNotIn(self.numeric_old_username, self.rest_server.users)
        self.assertIn(self.numeric_new_username, self.rest_server.users)

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_preserves_subscription_properties(self):

        # Setup initial subscription with all properties
        topic_name = 'test.topic'
        subscription = Subscription()
        subscription.topic_name = topic_name
        subscription.sec_name = 'old_sec_name'
        subscription.sub_key = 'preserved_sub_key'
        subscription.creation_time = 'preserved_creation_time'

        self.backend.subs_by_topic[topic_name] = {'old_sec_name': subscription}

        # Create the broker message
        msg = {
            'cid': 'test-cid-preserve',
            'has_sec_name_changed': True,
            'has_username_changed': False,
            'old_sec_name': 'old_sec_name',
            'new_sec_name': 'new_sec_name',
            'old_username': 'username',
            'new_username': 'username'
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert all subscription properties were preserved except sec_name
        updated_subscription = self.backend.subs_by_topic[topic_name]['new_sec_name']
        self.assertEqual(updated_subscription.sec_name, 'new_sec_name')
        self.assertEqual(updated_subscription.topic_name, topic_name)
        self.assertEqual(updated_subscription.sub_key, 'preserved_sub_key')
        self.assertEqual(updated_subscription.creation_time, 'preserved_creation_time')

# ################################################################################################################################

    def test_on_broker_msg_SECURITY_BASIC_AUTH_EDIT_empty_subscription_dict(self):

        # Setup topic with empty subscription dict
        topic_name = 'test.topic'
        self.backend.subs_by_topic[topic_name] = {}

        # Create the broker message
        msg = {
            'cid': 'test-cid-empty',
            'has_sec_name_changed': True,
            'has_username_changed': False,
            'old_sec_name': 'nonexistent_sec_name',
            'new_sec_name': 'new_sec_name',
            'old_username': 'username',
            'new_username': 'username'
        }

        # Call the method under test
        self.backend.on_broker_msg_SECURITY_BASIC_AUTH_EDIT(msg)

        # Assert subscription dict remains empty
        self.assertEqual(self.backend.subs_by_topic[topic_name], {})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
