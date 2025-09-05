#!/usr/bin/env python

"""
Tests for wrap_in_list behavior in PubSub REST server message retrieval.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import unittest
import warnings
from unittest.mock import Mock

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.models import APIResponse
from zato.common.pubsub.server.rest_publish import PubSubRESTServer

# ################################################################################################################################
# ################################################################################################################################

class BrokerClientHelper:
    """ Test broker client that captures publish calls without mocking.
    """

    def __init__(self):
        self.published_messages = []
        self.published_exchanges = []
        self.published_routing_keys = []

    def publish(self, message, exchange, routing_key):
        """ Capture publish parameters for verification.
        """
        self.published_messages.append(message)
        self.published_exchanges.append(exchange)
        self.published_routing_keys.append(routing_key)

# ################################################################################################################################
# ################################################################################################################################

class RESTWrapInListTestCase(unittest.TestCase):
    """ Tests for wrap_in_list behavior in _build_success_response.
    """

    def setUp(self):
        """ Set up test fixtures.
        """
        warnings.filterwarnings('ignore', category=ResourceWarning)

        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore
        self.rest_server.logger = Mock()
        self.test_cid = 'test-cid-123'

    def test_single_message_wrap_in_list_false(self):
        """ Single message with wrap_in_list=False returns message at root level.
        """
        test_messages = [
            {
                'meta': {
                    'msg_id': 'msg_1',
                    'topic_name': 'test.topic',
                    'size': 100,
                    'priority': 5,
                    'expiration': 3600,
                    'correl_id': 'corr_1',
                    'pub_time_iso': '2023-01-01T00:00:00+00:00',
                    'recv_time_iso': '2023-01-01T00:00:01+00:00',
                    'expiration_time_iso': '2023-01-01T01:00:00+00:00',
                    'time_since_pub': 1.0,
                    'time_since_recv': 0.5
                },
                'data': 'test message content'
            }
        ]

        response = self.rest_server._build_success_response(self.test_cid, test_messages, 1, False)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.message_count, 1)
        self.assertEqual(response.data, 'test message content')
        self.assertEqual(response.meta['msg_id'], 'msg_1')
        self.assertIsNone(response.messages)

# ################################################################################################################################

    def test_single_message_wrap_in_list_true(self):
        """ Single message with wrap_in_list=True returns message in list.
        """
        test_messages = [
            {
                'meta': {
                    'msg_id': 'msg_1',
                    'topic_name': 'test.topic',
                    'size': 100,
                    'priority': 5,
                    'expiration': 3600,
                    'correl_id': 'corr_1',
                    'pub_time_iso': '2023-01-01T00:00:00+00:00',
                    'recv_time_iso': '2023-01-01T00:00:01+00:00',
                    'expiration_time_iso': '2023-01-01T01:00:00+00:00',
                    'time_since_pub': 1.0,
                    'time_since_recv': 0.5
                },
                'data': 'test message content'
            }
        ]

        response = self.rest_server._build_success_response(self.test_cid, test_messages, 1, True)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.message_count, 1)
        self.assertEqual(response.messages, test_messages)
        self.assertIsNone(response.data)
        self.assertIsNone(response.meta)

# ################################################################################################################################

    def test_multiple_messages_wrap_in_list_false(self):
        """ Multiple messages with wrap_in_list=False returns messages in list.
        """
        test_messages = [
            {
                'meta': {
                    'msg_id': 'msg_1',
                    'topic_name': 'test.topic',
                    'size': 100,
                    'priority': 5,
                    'expiration': 3600,
                    'correl_id': 'corr_1',
                    'pub_time_iso': '2023-01-01T00:00:00+00:00',
                    'recv_time_iso': '2023-01-01T00:00:01+00:00',
                    'expiration_time_iso': '2023-01-01T01:00:00+00:00',
                    'time_since_pub': 1.0,
                    'time_since_recv': 0.5
                },
                'data': 'test message 1'
            },
            {
                'meta': {
                    'msg_id': 'msg_2',
                    'topic_name': 'test.topic',
                    'size': 110,
                    'priority': 3,
                    'expiration': 3600,
                    'correl_id': 'corr_2',
                    'pub_time_iso': '2023-01-01T00:00:02+00:00',
                    'recv_time_iso': '2023-01-01T00:00:03+00:00',
                    'expiration_time_iso': '2023-01-01T01:00:02+00:00',
                    'time_since_pub': 2.0,
                    'time_since_recv': 1.5
                },
                'data': 'test message 2'
            }
        ]

        response = self.rest_server._build_success_response(self.test_cid, test_messages, 50, False)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.message_count, 2)
        self.assertEqual(response.messages, test_messages)
        self.assertIsNone(response.data)
        self.assertIsNone(response.meta)

# ################################################################################################################################

    def test_multiple_messages_wrap_in_list_true(self):
        """ Multiple messages with wrap_in_list=True returns messages in list.
        """
        test_messages = [
            {
                'meta': {
                    'msg_id': 'msg_1',
                    'topic_name': 'test.topic',
                    'size': 100,
                    'priority': 5,
                    'expiration': 3600,
                    'correl_id': 'corr_1',
                    'pub_time_iso': '2023-01-01T00:00:00+00:00',
                    'recv_time_iso': '2023-01-01T00:00:01+00:00',
                    'expiration_time_iso': '2023-01-01T01:00:00+00:00',
                    'time_since_pub': 1.0,
                    'time_since_recv': 0.5
                },
                'data': 'test message 1'
            },
            {
                'meta': {
                    'msg_id': 'msg_2',
                    'topic_name': 'test.topic',
                    'size': 110,
                    'priority': 3,
                    'expiration': 3600,
                    'correl_id': 'corr_2',
                    'pub_time_iso': '2023-01-01T00:00:02+00:00',
                    'recv_time_iso': '2023-01-01T00:00:03+00:00',
                    'expiration_time_iso': '2023-01-01T01:00:02+00:00',
                    'time_since_pub': 2.0,
                    'time_since_recv': 1.5
                },
                'data': 'test message 2'
            }
        ]

        response = self.rest_server._build_success_response(self.test_cid, test_messages, 50, True)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.message_count, 2)
        self.assertEqual(response.messages, test_messages)
        self.assertIsNone(response.data)
        self.assertIsNone(response.meta)

# ################################################################################################################################

    def test_empty_messages_wrap_in_list_false(self):
        """ Empty messages with wrap_in_list=False returns empty list.
        """
        test_messages = []

        response = self.rest_server._build_success_response(self.test_cid, test_messages, 1, False)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.message_count, 0)
        self.assertEqual(response.messages, [])
        self.assertIsNone(response.data)
        self.assertIsNone(response.meta)

# ################################################################################################################################

    def test_empty_messages_wrap_in_list_true(self):
        """ Empty messages with wrap_in_list=True returns empty list.
        """
        test_messages = []

        response = self.rest_server._build_success_response(self.test_cid, test_messages, 1, True)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.message_count, 0)
        self.assertEqual(response.messages, [])
        self.assertIsNone(response.data)
        self.assertIsNone(response.meta)

# ################################################################################################################################

    def test_max_messages_greater_than_one_wrap_in_list_false(self):
        """ max_messages > 1 with wrap_in_list=False returns messages in list.
        """
        test_messages = [
            {
                'meta': {
                    'msg_id': 'msg_1',
                    'topic_name': 'test.topic',
                    'size': 100,
                    'priority': 5,
                    'expiration': 3600,
                    'correl_id': 'corr_1',
                    'pub_time_iso': '2023-01-01T00:00:00+00:00',
                    'recv_time_iso': '2023-01-01T00:00:01+00:00',
                    'expiration_time_iso': '2023-01-01T01:00:00+00:00',
                    'time_since_pub': 1.0,
                    'time_since_recv': 0.5
                },
                'data': 'test message content'
            }
        ]

        response = self.rest_server._build_success_response(self.test_cid, test_messages, 5, False)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.message_count, 1)
        self.assertEqual(response.messages, test_messages)
        self.assertIsNone(response.data)
        self.assertIsNone(response.meta)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
