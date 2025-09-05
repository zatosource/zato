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
from zato.common.api import PubSub
from zato.common.pubsub.backend.rest_backend import RESTBackend
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

class RESTValidateGetParamsTestCase(TestCase):

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

    def test_validate_get_params_with_default_values(self):
        """ _validate_get_params returns default values when no params provided.
        """
        data = {}
        max_len, max_messages, wrap_in_list = self.rest_server._validate_get_params(data)

        self.assertEqual(max_len, PubSub.Message.Default_Max_Len)
        self.assertEqual(max_messages, PubSub.Message.Default_Max_Messages)

# ################################################################################################################################

    def test_validate_get_params_with_custom_values(self):
        """ _validate_get_params returns custom values when provided.
        """
        data = {
            'max_len': 1000,
            'max_messages': 5
        }
        max_len, max_messages, wrap_in_list = self.rest_server._validate_get_params(data)

        self.assertEqual(max_len, 1000)
        self.assertEqual(max_messages, 5)

# ################################################################################################################################

    def test_validate_get_params_enforces_max_len_limit(self):
        """ _validate_get_params enforces maximum length limit.
        """
        data = {
            'max_len': 10_000_000,  # Above limit
            'max_messages': 5
        }
        max_len, max_messages, wrap_in_list = self.rest_server._validate_get_params(data)

        self.assertEqual(max_len, 5_000_000)  # Capped to PubSub.Message.Default_Max_Len
        self.assertEqual(max_messages, 5)

# ################################################################################################################################

    def test_validate_get_params_enforces_max_messages_limit(self):
        """ _validate_get_params enforces maximum messages limit.
        """
        data = {
            'max_len': 1000,
            'max_messages': 2000    # Above limit
        }
        max_len, max_messages, wrap_in_list = self.rest_server._validate_get_params(data)

        self.assertEqual(max_len, 1000)
        self.assertEqual(max_messages, 1000)  # Capped to limit

# ################################################################################################################################

    def test_validate_get_params_enforces_both_limits(self):
        """ _validate_get_params enforces both limits simultaneously.
        """
        data = {
            'max_len': 10_000_000,  # Above limit
            'max_messages': 2000    # Above limit
        }
        max_len, max_messages, wrap_in_list = self.rest_server._validate_get_params(data)

        self.assertEqual(max_len, 5_000_000)  # Capped to PubSub.Message.Default_Max_Len
        self.assertEqual(max_messages, 1000)  # Capped to limit

# ################################################################################################################################

    def test_validate_get_params_with_zero_values(self):
        """ _validate_get_params handles zero values correctly.
        """
        data = {
            'max_len': 0,
            'max_messages': 0
        }
        max_len, max_messages, wrap_in_list = self.rest_server._validate_get_params(data)

        self.assertEqual(max_len, 0)
        self.assertEqual(max_messages, 0)

# ################################################################################################################################

    def test_validate_get_params_with_negative_values(self):
        """ _validate_get_params handles negative values correctly.
        """
        data = {
            'max_len': -100,
            'max_messages': -5
        }
        max_len, max_messages, wrap_in_list = self.rest_server._validate_get_params(data)

        self.assertEqual(max_len, -100)
        self.assertEqual(max_messages, -5)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
