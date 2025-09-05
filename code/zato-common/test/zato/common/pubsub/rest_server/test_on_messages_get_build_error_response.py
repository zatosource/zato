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
from zato.common.pubsub.models import BadRequestResponse
from zato.common.pubsub.server.rest_pull import PubSubRESTServerPull

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

class RESTBuildErrorResponseTestCase(TestCase):

    def setUp(self):

        # Suppress ResourceWarnings from gevent
        warnings.filterwarnings('ignore', category=ResourceWarning)

        # Create a test broker client that captures publish calls
        self.broker_client = BrokerClientHelper()
        self.rest_server = PubSubRESTServerPull('localhost', 8080, should_init_broker_client=False)
        self.rest_server.backend = RESTBackend(self.rest_server, self.broker_client) # type: ignore

        # Test data constants
        self.test_cid = 'test-cid-123'

# ################################################################################################################################

    def test_build_error_response_creates_bad_request_response(self):
        """ _build_error_response creates proper BadRequestResponse with details.
        """
        error_details = 'Test error occurred'

        response = self.rest_server._build_error_response(self.test_cid, error_details)

        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, error_details)

# ################################################################################################################################

    def test_build_error_response_with_empty_details(self):
        """ _build_error_response handles empty error details.
        """
        error_details = ''

        response = self.rest_server._build_error_response(self.test_cid, error_details)

        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, '')

# ################################################################################################################################

    def test_build_error_response_with_long_details(self):
        """ _build_error_response handles long error details.
        """
        error_details = 'This is a very long error message that contains detailed information about what went wrong during the processing of the request and includes technical details that might be useful for debugging purposes.'

        response = self.rest_server._build_error_response(self.test_cid, error_details)

        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, error_details)

# ################################################################################################################################

    def test_build_error_response_with_special_characters(self):
        """ _build_error_response handles special characters in error details.
        """
        error_details = 'Error with special chars: ñáéíóú 🚀 @#$%^&*()[]{}|\\:";\'<>?,./'

        response = self.rest_server._build_error_response(self.test_cid, error_details)

        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, error_details)

# ################################################################################################################################

    def test_build_error_response_with_multiline_details(self):
        """ _build_error_response handles multiline error details.
        """
        error_details = 'First line of error\nSecond line of error\nThird line with more details'

        response = self.rest_server._build_error_response(self.test_cid, error_details)

        self.assertIsInstance(response, BadRequestResponse)
        self.assertEqual(response.cid, self.test_cid)
        self.assertEqual(response.details, error_details)

# ################################################################################################################################

    def test_build_error_response_different_cids(self):
        """ _build_error_response handles different CIDs correctly.
        """
        error_details = 'Common error message'

        cid1 = 'error-cid-111'
        cid2 = 'error-cid-222'

        response1 = self.rest_server._build_error_response(cid1, error_details)
        response2 = self.rest_server._build_error_response(cid2, error_details)

        self.assertEqual(response1.cid, cid1)
        self.assertEqual(response2.cid, cid2)
        self.assertEqual(response1.details, error_details)
        self.assertEqual(response2.details, error_details)

# ################################################################################################################################

    def test_build_error_response_common_error_messages(self):
        """ _build_error_response handles common error message patterns.
        """
        common_errors = [
            'No subscription found for user',
            'Failed to retrieve messages from queue',
            'Internal error retrieving messages',
            'Authentication failed',
            'Invalid request format',
            'Queue not found',
            'Connection timeout',
            'Permission denied'
        ]

        for error_msg in common_errors:
            response = self.rest_server._build_error_response(self.test_cid, error_msg)

            self.assertIsInstance(response, BadRequestResponse)
            self.assertEqual(response.cid, self.test_cid)
            self.assertEqual(response.details, error_msg)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
