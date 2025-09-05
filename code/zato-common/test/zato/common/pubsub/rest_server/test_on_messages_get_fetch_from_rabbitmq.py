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
from zato.common.pubsub.server.rest_publish import PubSubRESTServerPublish

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

class RESTServerHelper(PubSubRESTServerPublish):
    """ Test REST server that overrides HTTP requests to RabbitMQ.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_rabbitmq_response = []
        self.test_rabbitmq_status_code = 200
        self.captured_api_urls = []
        self.captured_payloads = []

    def _fetch_from_rabbitmq(self, cid, api_url, payload):
        """ Override to capture requests and return test data.
        """
        self.captured_api_urls.append(api_url)
        self.captured_payloads.append(payload)

        if self.test_rabbitmq_status_code != 200:
            return None

        return self.test_rabbitmq_response

# ################################################################################################################################
# ################################################################################################################################

class RESTFetchFromRabbitMQTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = RESTServerHelper('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

        # Test data constants
        self.test_cid = 'test-cid-123'
        self.test_api_url = 'http://test.rabbitmq.api/queues/vhost/queue/get'
        self.test_payload = {'count': 5, 'ackmode': 'ack_requeue_false'}

# ################################################################################################################################

    def test_fetch_from_rabbitmq_returns_data_on_success(self):
        """ _fetch_from_rabbitmq returns data when RabbitMQ responds successfully.
        """
        test_data = [{'message': 'test message 1'}, {'message': 'test message 2'}]
        self.rest_server.test_rabbitmq_response = test_data
        self.rest_server.test_rabbitmq_status_code = 200

        result = self.rest_server._fetch_from_rabbitmq(
            self.test_cid, self.test_api_url, self.test_payload
        )

        self.assertEqual(result, test_data)
        self.assertEqual(len(self.rest_server.captured_api_urls), 1)
        self.assertEqual(self.rest_server.captured_api_urls[0], self.test_api_url)
        self.assertEqual(len(self.rest_server.captured_payloads), 1)
        self.assertEqual(self.rest_server.captured_payloads[0], self.test_payload)

# ################################################################################################################################

    def test_fetch_from_rabbitmq_returns_none_on_error(self):
        """ _fetch_from_rabbitmq returns None when RabbitMQ responds with error.
        """
        self.rest_server.test_rabbitmq_status_code = 500

        result = self.rest_server._fetch_from_rabbitmq(
            self.test_cid, self.test_api_url, self.test_payload
        )

        self.assertIsNone(result)

# ################################################################################################################################

    def test_fetch_from_rabbitmq_returns_none_on_404(self):
        """ _fetch_from_rabbitmq returns None when queue not found.
        """
        self.rest_server.test_rabbitmq_status_code = 404

        result = self.rest_server._fetch_from_rabbitmq(
            self.test_cid, self.test_api_url, self.test_payload
        )

        self.assertIsNone(result)

# ################################################################################################################################

    def test_fetch_from_rabbitmq_returns_none_on_401(self):
        """ _fetch_from_rabbitmq returns None when authentication fails.
        """
        self.rest_server.test_rabbitmq_status_code = 401

        result = self.rest_server._fetch_from_rabbitmq(
            self.test_cid, self.test_api_url, self.test_payload
        )

        self.assertIsNone(result)

# ################################################################################################################################

    def test_fetch_from_rabbitmq_captures_multiple_requests(self):
        """ _fetch_from_rabbitmq captures multiple requests correctly.
        """
        test_data = [{'message': 'test'}]
        self.rest_server.test_rabbitmq_response = test_data
        self.rest_server.test_rabbitmq_status_code = 200

        # Make first request
        result1 = self.rest_server._fetch_from_rabbitmq(
            self.test_cid, 'http://api1.url', {'payload': 1}
        )

        # Make second request
        result2 = self.rest_server._fetch_from_rabbitmq(
            self.test_cid, 'http://api2.url', {'payload': 2}
        )

        self.assertEqual(result1, test_data)
        self.assertEqual(result2, test_data)
        self.assertEqual(len(self.rest_server.captured_api_urls), 2)
        self.assertEqual(self.rest_server.captured_api_urls[0], 'http://api1.url')
        self.assertEqual(self.rest_server.captured_api_urls[1], 'http://api2.url')
        self.assertEqual(len(self.rest_server.captured_payloads), 2)
        self.assertEqual(self.rest_server.captured_payloads[0], {'payload': 1})
        self.assertEqual(self.rest_server.captured_payloads[1], {'payload': 2})

# ################################################################################################################################

    def test_fetch_from_rabbitmq_returns_empty_list(self):
        """ _fetch_from_rabbitmq returns empty list when no messages available.
        """
        self.rest_server.test_rabbitmq_response = []
        self.rest_server.test_rabbitmq_status_code = 200

        result = self.rest_server._fetch_from_rabbitmq(
            self.test_cid, self.test_api_url, self.test_payload
        )

        self.assertEqual(result, [])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
