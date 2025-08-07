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

class RESTBuildRabbitMQRequestTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServer('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

        # Test data constants
        self.test_sub_key = 'test_sub_key_123'

# ################################################################################################################################

    def test_build_rabbitmq_request_creates_correct_url_and_payload(self):
        """ _build_rabbitmq_request builds correct API URL and payload.
        """
        max_messages = 10
        max_len = 2000

        api_url, payload = self.rest_server._build_rabbitmq_request(
            self.test_sub_key, max_messages, max_len
        )

        expected_url = f'{self.rest_server._broker_api_base_url}/queues/{self.rest_server._broker_config.vhost}/{self.test_sub_key}/get'
        expected_payload = {
            'count': max_messages,
            'ackmode': 'ack_requeue_false',
            'encoding': 'auto',
            'truncate': max_len
        }

        self.assertEqual(api_url, expected_url)
        self.assertEqual(payload, expected_payload)

# ################################################################################################################################

    def test_build_rabbitmq_request_with_single_message(self):
        """ _build_rabbitmq_request handles single message request.
        """
        max_messages = 1
        max_len = 1000

        _, payload = self.rest_server._build_rabbitmq_request(
            self.test_sub_key, max_messages, max_len
        )

        expected_payload = {
            'count': 1,
            'ackmode': 'ack_requeue_false',
            'encoding': 'auto',
            'truncate': 1000
        }

        self.assertEqual(payload, expected_payload)

# ################################################################################################################################

    def test_build_rabbitmq_request_with_large_limits(self):
        """ _build_rabbitmq_request handles large limit values.
        """
        max_messages = 1000
        max_len = 5_000_000

        _, payload = self.rest_server._build_rabbitmq_request(
            self.test_sub_key, max_messages, max_len
        )

        expected_payload = {
            'count': 1000,
            'ackmode': 'ack_requeue_false',
            'encoding': 'auto',
            'truncate': 5_000_000
        }

        self.assertEqual(payload, expected_payload)

# ################################################################################################################################

    def test_build_rabbitmq_request_with_zero_values(self):
        """ _build_rabbitmq_request handles zero values.
        """
        max_messages = 0
        max_len = 0

        _, payload = self.rest_server._build_rabbitmq_request(
            self.test_sub_key, max_messages, max_len
        )

        expected_payload = {
            'count': 0,
            'ackmode': 'ack_requeue_false',
            'encoding': 'auto',
            'truncate': 0
        }

        self.assertEqual(payload, expected_payload)

# ################################################################################################################################

    def test_build_rabbitmq_request_url_contains_sub_key(self):
        """ _build_rabbitmq_request URL contains the subscription key.
        """
        different_sub_key = 'different_key_789'

        api_url, _ = self.rest_server._build_rabbitmq_request(
            different_sub_key, 5, 1000
        )

        self.assertIn(different_sub_key, api_url)
        self.assertTrue(api_url.endswith(f'{different_sub_key}/get'))

# ################################################################################################################################

    def test_build_rabbitmq_request_payload_structure(self):
        """ _build_rabbitmq_request payload has correct structure.
        """
        _, payload = self.rest_server._build_rabbitmq_request(
            self.test_sub_key, 5, 1000
        )

        # Check all required keys are present
        required_keys = {'count', 'ackmode', 'encoding', 'truncate'}
        self.assertEqual(set(payload.keys()), required_keys)

        # Check specific values
        self.assertEqual(payload['ackmode'], 'ack_requeue_false')
        self.assertEqual(payload['encoding'], 'auto')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
