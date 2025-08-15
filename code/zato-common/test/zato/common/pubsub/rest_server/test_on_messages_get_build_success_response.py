# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
import warnings
from unittest import main, TestCase

# Zato
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.models import APIResponse
from zato.common.pubsub.server.rest import PubSubRESTServer

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

class RESTBuildSuccessResponseTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

        # Test data constants
        self.test_cid = 'test-cid-123'

# ################################################################################################################################

    def test_build_success_response_creates_api_response(self):
        """ _build_success_response creates proper APIResponse with messages.
        """
        test_messages = [
            {'msg_id': 'msg_1', 'data': 'message 1'},
            {'msg_id': 'msg_2', 'data': 'message 2'}
        ]

        response = self.rest_server._build_success_response(self.test_cid, test_messages)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.messages, test_messages)
        self.assertEqual(response.message_count, len(test_messages))

# ################################################################################################################################

    def test_build_success_response_with_empty_messages(self):
        """ _build_success_response handles empty message list.
        """
        test_messages = []

        response = self.rest_server._build_success_response(self.test_cid, test_messages)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.messages, [])
        self.assertEqual(response.message_count, 0)

# ################################################################################################################################

    def test_build_success_response_with_single_message(self):
        """ _build_success_response handles single message.
        """
        test_messages = [
            {
                'msg_id': 'single_msg_123',
                'data': 'single message content',
                'topic_name': 'test.topic',
                'priority': 5
            }
        ]

        response = self.rest_server._build_success_response(self.test_cid, test_messages)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(len(response.messages), 1)
        self.assertEqual(response.message_count, 1)
        self.assertEqual(response.messages[0]['msg_id'], 'single_msg_123')
        self.assertEqual(response.messages[0]['data'], 'single message content')

# ################################################################################################################################

    def test_build_success_response_with_complex_messages(self):
        """ _build_success_response handles complex message structures.
        """
        test_messages = [
            {
                'msg_id': 'complex_msg_1',
                'data': {'nested': {'structure': 'value'}},
                'topic_name': 'complex.topic',
                'priority': 8,
                'headers': {'custom': 'header'},
                'metadata': ['item1', 'item2']
            },
            {
                'msg_id': 'complex_msg_2',
                'data': [1, 2, 3, 4, 5],
                'topic_name': 'array.topic',
                'priority': 2
            }
        ]

        response = self.rest_server._build_success_response(self.test_cid, test_messages)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(len(response.messages), 2)
        self.assertEqual(response.message_count, 2)
        self.assertEqual(response.messages, test_messages)

# ################################################################################################################################

    def test_build_success_response_preserves_message_order(self):
        """ _build_success_response preserves message order.
        """
        test_messages = []
        for i in range(10):
            test_messages.append({
                'msg_id': f'msg_{i}',
                'data': f'message {i}',
                'sequence': i
            })

        response = self.rest_server._build_success_response(self.test_cid, test_messages)

        self.assertIsInstance(response, APIResponse)
        self.assertTrue(response.is_ok)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(len(response.messages), 10)
        self.assertEqual(response.message_count, 10)

        for i, message in enumerate(response.messages):
            self.assertEqual(message['msg_id'], f'msg_{i}')
            self.assertEqual(message['sequence'], i)

# ################################################################################################################################

    def test_build_success_response_different_cids(self):
        """ _build_success_response handles different CIDs correctly.
        """
        test_messages = [{'msg_id': 'test_msg', 'data': 'test data'}]

        cid1 = 'cid-111'
        cid2 = 'cid-222'

        response1 = self.rest_server._build_success_response(cid1, test_messages)
        response2 = self.rest_server._build_success_response(cid2, test_messages)

        self.assertEqual(response1.cid, cid1)
        self.assertEqual(response2.cid, cid2)
        self.assertTrue(response1.is_ok)
        self.assertTrue(response2.is_ok)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
