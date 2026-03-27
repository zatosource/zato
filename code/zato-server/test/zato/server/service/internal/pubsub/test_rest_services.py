# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from http.client import BAD_REQUEST, UNAUTHORIZED
from unittest.mock import MagicMock, patch

# ################################################################################################################################
# ################################################################################################################################

class MockChannel:
    def __init__(self, username:'str'=None) -> 'None':
        self.security = MagicMock()
        self.security.username = username

# ################################################################################################################################
# ################################################################################################################################

class MockPermissionResult:
    def __init__(self, is_ok:'bool'=True, reason:'str'='') -> 'None':
        self.is_ok = is_ok
        self.reason = reason

# ################################################################################################################################
# ################################################################################################################################

class TestPublishService(unittest.TestCase):

    def setUp(self) -> 'None':
        self.server_mock = MagicMock()
        self.server_mock.pubsub_redis = MagicMock()
        self.server_mock.pubsub_pattern_matcher = MagicMock()
        self.server_mock.pubsub_pattern_matcher.evaluate.return_value = MockPermissionResult(is_ok=True)

# ################################################################################################################################

    def _get_service(self, username:'str'='testuser') -> 'MagicMock':
        from zato.server.service.internal.pubsub.rest import Publish

        service = Publish()
        service.cid = 'test-cid'
        service.channel = MockChannel(username)
        service.server = self.server_mock
        service.request = MagicMock()
        service.response = MagicMock()
        service.response.payload = MagicMock()

        return service

# ################################################################################################################################

    def test_publish_returns_msg_id(self) -> 'None':
        """ Test that publishing returns a message ID.
        """
        service = self._get_service()
        service.request.input.topic_name = 'test.topic'
        service.request.input.data = 'test data'
        service.request.input.priority = None
        service.request.input.expiration = None
        service.request.input.correl_id = None
        service.request.input.in_reply_to = None
        service.request.input.ext_client_id = None

        self.server_mock.pubsub_redis.publish.return_value = 'msg123'

        service.handle()

        self.assertTrue(service.response.payload.is_ok)
        self.assertEqual(service.response.payload.msg_id, 'msg123')

# ################################################################################################################################

    def test_publish_validates_topic_name(self) -> 'None':
        """ Test that invalid topic names are rejected.
        """
        service = self._get_service()
        service.request.input.topic_name = 'invalid#topic'  # Contains #
        service.request.input.data = 'test data'

        service.handle()

        self.assertFalse(service.response.payload.is_ok)
        self.assertEqual(service.response.payload.status, BAD_REQUEST)

# ################################################################################################################################

    def test_publish_checks_permissions(self) -> 'None':
        """ Test that permissions are checked before publishing.
        """
        service = self._get_service()
        service.request.input.topic_name = 'test.topic'
        service.request.input.data = 'test data'

        self.server_mock.pubsub_pattern_matcher.evaluate.return_value = MockPermissionResult(is_ok=False)

        service.handle()

        self.assertFalse(service.response.payload.is_ok)
        self.assertEqual(service.response.payload.status, UNAUTHORIZED)

# ################################################################################################################################

    def test_publish_rejects_missing_data(self) -> 'None':
        """ Test that missing data is rejected.
        """
        service = self._get_service()
        service.request.input.topic_name = 'test.topic'
        service.request.input.data = None

        service.handle()

        self.assertFalse(service.response.payload.is_ok)
        self.assertEqual(service.response.payload.status, BAD_REQUEST)

# ################################################################################################################################

    def test_publish_requires_authentication(self) -> 'None':
        """ Test that unauthenticated requests are rejected.
        """
        service = self._get_service(username=None)
        service.request.input.topic_name = 'test.topic'
        service.request.input.data = 'test data'

        service.handle()

        self.assertFalse(service.response.payload.is_ok)
        self.assertEqual(service.response.payload.status, UNAUTHORIZED)

# ################################################################################################################################
# ################################################################################################################################

class TestGetMessagesService(unittest.TestCase):

    def setUp(self) -> 'None':
        self.server_mock = MagicMock()
        self.server_mock.pubsub_redis = MagicMock()
        self.server_mock.pubsub_subscriptions = MagicMock()

# ################################################################################################################################

    def _get_service(self, username:'str'='testuser') -> 'MagicMock':
        from zato.server.service.internal.pubsub.rest import GetMessages

        service = GetMessages()
        service.cid = 'test-cid'
        service.channel = MockChannel(username)
        service.server = self.server_mock
        service.request = MagicMock()
        service.response = MagicMock()
        service.response.payload = MagicMock()

        return service

# ################################################################################################################################

    def test_get_messages_returns_subscribed_messages(self) -> 'None':
        """ Test that messages are returned for subscribed topics.
        """
        service = self._get_service()
        service.request.input.max_messages = None
        service.request.input.max_len = None

        self.server_mock.pubsub_subscriptions.get_sub_key_by_username.return_value = 'zpsk.test123'
        self.server_mock.pubsub_redis.fetch_messages.return_value = [
            {'msg_id': 'msg1', 'data': 'test1'},
            {'msg_id': 'msg2', 'data': 'test2'},
        ]

        service.handle()

        self.assertTrue(service.response.payload.is_ok)
        self.assertEqual(service.response.payload.message_count, 2)

# ################################################################################################################################

    def test_get_messages_respects_max_messages(self) -> 'None':
        """ Test that max_messages parameter is passed to backend.
        """
        service = self._get_service()
        service.request.input.max_messages = 10
        service.request.input.max_len = None

        self.server_mock.pubsub_subscriptions.get_sub_key_by_username.return_value = 'zpsk.test123'
        self.server_mock.pubsub_redis.fetch_messages.return_value = []

        service.handle()

        self.server_mock.pubsub_redis.fetch_messages.assert_called_once()
        call_kwargs = self.server_mock.pubsub_redis.fetch_messages.call_args[1]
        self.assertEqual(call_kwargs['max_messages'], 10)

# ################################################################################################################################

    def test_get_messages_respects_max_len(self) -> 'None':
        """ Test that max_len parameter is passed to backend.
        """
        service = self._get_service()
        service.request.input.max_messages = None
        service.request.input.max_len = 1000

        self.server_mock.pubsub_subscriptions.get_sub_key_by_username.return_value = 'zpsk.test123'
        self.server_mock.pubsub_redis.fetch_messages.return_value = []

        service.handle()

        call_kwargs = self.server_mock.pubsub_redis.fetch_messages.call_args[1]
        self.assertEqual(call_kwargs['max_len'], 1000)

# ################################################################################################################################

    def test_get_messages_returns_empty_when_no_subscription(self) -> 'None':
        """ Test that empty list is returned when user has no subscriptions.
        """
        service = self._get_service()
        service.request.input.max_messages = None
        service.request.input.max_len = None

        self.server_mock.pubsub_subscriptions.get_sub_key_by_username.return_value = None

        service.handle()

        self.assertTrue(service.response.payload.is_ok)
        self.assertEqual(service.response.payload.message_count, 0)
        self.server_mock.pubsub_redis.fetch_messages.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class TestSubscribeService(unittest.TestCase):

    def setUp(self) -> 'None':
        self.server_mock = MagicMock()
        self.server_mock.pubsub_redis = MagicMock()
        self.server_mock.pubsub_pattern_matcher = MagicMock()
        self.server_mock.pubsub_pattern_matcher.evaluate.return_value = MockPermissionResult(is_ok=True)
        self.server_mock.pubsub_subscriptions = MagicMock()

# ################################################################################################################################

    def _get_service(self, username:'str'='testuser') -> 'MagicMock':
        from zato.server.service.internal.pubsub.rest import Subscribe

        service = Subscribe()
        service.cid = 'test-cid'
        service.channel = MockChannel(username)
        service.server = self.server_mock
        service.request = MagicMock()
        service.response = MagicMock()
        service.response.payload = MagicMock()
        service.invoke = MagicMock()

        return service

# ################################################################################################################################

    def test_subscribe_creates_subscription(self) -> 'None':
        """ Test that subscribing creates a subscription in Redis.
        """
        service = self._get_service()
        service.request.input.topic_name = 'test.topic'

        self.server_mock.pubsub_subscriptions.get_or_create_sub_key.return_value = 'zpsk.test123'
        self.server_mock.pubsub_subscriptions.get_sec_name_by_username.return_value = 'test_sec'

        service.handle()

        self.assertTrue(service.response.payload.is_ok)
        self.server_mock.pubsub_redis.subscribe.assert_called_once_with('zpsk.test123', 'test.topic')

# ################################################################################################################################

    def test_subscribe_idempotent(self) -> 'None':
        """ Test that subscribing multiple times is safe.
        """
        service = self._get_service()
        service.request.input.topic_name = 'test.topic'

        self.server_mock.pubsub_subscriptions.get_or_create_sub_key.return_value = 'zpsk.test123'
        self.server_mock.pubsub_subscriptions.get_sec_name_by_username.return_value = 'test_sec'

        # Call twice
        service.handle()
        service.handle()

        # Both should succeed
        self.assertTrue(service.response.payload.is_ok)

# ################################################################################################################################

    def test_subscribe_checks_permissions(self) -> 'None':
        """ Test that permissions are checked before subscribing.
        """
        service = self._get_service()
        service.request.input.topic_name = 'test.topic'

        self.server_mock.pubsub_pattern_matcher.evaluate.return_value = MockPermissionResult(is_ok=False)

        service.handle()

        self.assertFalse(service.response.payload.is_ok)
        self.assertEqual(service.response.payload.status, UNAUTHORIZED)
        self.server_mock.pubsub_redis.subscribe.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

class TestUnsubscribeService(unittest.TestCase):

    def setUp(self) -> 'None':
        self.server_mock = MagicMock()
        self.server_mock.pubsub_redis = MagicMock()
        self.server_mock.pubsub_subscriptions = MagicMock()

# ################################################################################################################################

    def _get_service(self, username:'str'='testuser') -> 'MagicMock':
        from zato.server.service.internal.pubsub.rest import Unsubscribe

        service = Unsubscribe()
        service.cid = 'test-cid'
        service.channel = MockChannel(username)
        service.server = self.server_mock
        service.request = MagicMock()
        service.response = MagicMock()
        service.response.payload = MagicMock()
        service.invoke = MagicMock()

        return service

# ################################################################################################################################

    def test_unsubscribe_removes_subscription(self) -> 'None':
        """ Test that unsubscribing removes the subscription from Redis.
        """
        service = self._get_service()
        service.request.input.topic_name = 'test.topic'

        self.server_mock.pubsub_subscriptions.get_sub_key_by_username.return_value = 'zpsk.test123'
        self.server_mock.pubsub_subscriptions.get_sec_name_by_username.return_value = 'test_sec'

        service.handle()

        self.assertTrue(service.response.payload.is_ok)
        self.server_mock.pubsub_redis.unsubscribe.assert_called_once_with('zpsk.test123', 'test.topic')

# ################################################################################################################################

    def test_unsubscribe_idempotent(self) -> 'None':
        """ Test that unsubscribing when not subscribed is safe.
        """
        service = self._get_service()
        service.request.input.topic_name = 'test.topic'

        # User has no subscriptions
        self.server_mock.pubsub_subscriptions.get_sub_key_by_username.return_value = None

        service.handle()

        # Should succeed without calling unsubscribe
        self.assertTrue(service.response.payload.is_ok)
        self.server_mock.pubsub_redis.unsubscribe.assert_not_called()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
