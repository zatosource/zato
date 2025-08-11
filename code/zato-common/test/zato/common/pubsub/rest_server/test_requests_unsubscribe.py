# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import http.client as http_client
import logging
import os
import time
from unittest import main, TestCase

# requests
import requests
from requests.auth import HTTPBasicAuth

# PyYAML
from yaml import safe_load as yaml_load

# Zato
from zato.common.pubsub.util import get_broker_config, cleanup_broker_impl

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Enable HTTP traffic logging
http_client.HTTPConnection.debuglevel = 1

# Patch HTTPConnection methods to log with proper format
original_send = http_client.HTTPConnection.send
original_getresponse = http_client.HTTPConnection.getresponse

def patched_send(self, data):
    logger = logging.getLogger('http.client')
    if isinstance(data, bytes):
        logger.debug(f'send: {data.decode("utf-8", errors="replace")}')
    else:
        logger.debug(f'send: {data}')
    return original_send(self, data)

def patched_getresponse(self):
    response = original_getresponse(self)
    logger = logging.getLogger('http.client')
    logger.debug(f'reply: {response.version} {response.status} {response.reason}')
    for header, value in response.getheaders():
        logger.debug(f'header: {header}: {value}')
    return response

http_client.HTTPConnection.send = patched_send
http_client.HTTPConnection.getresponse = patched_getresponse

# Patch HTTPResponse to log response body
original_read = http_client.HTTPResponse.read

def patched_read(self, amt=None):
    data = original_read(self, amt)
    if data:
        logger = logging.getLogger('http.client.response')
        try:
            decoded = data.decode("utf-8")
            logger.debug(f'Response body: {decoded}')
        except UnicodeDecodeError:
            logger.debug(f'Response body (binary): {len(data)} bytes')
    return data

http_client.HTTPResponse.read = patched_read

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerUnsubscribeTestCase(TestCase):
    """ Test cases for the pub/sub REST server unsubscribe functionality.
    """

    @classmethod
    def setUpClass(cls):
        """ Set up test configuration.
        """
        # Check if config environment variable exists
        config_path = os.environ.get('Zato_PubSub_YAML_Config_File')
        if not config_path:
            cls.skip_tests = True
            return

        cls.skip_tests = False

        # Load configuration
        with open(config_path, 'r') as f:
            cls.config = yaml_load(f)

        # Extract demo user credentials
        cls.username = 'demo'
        cls.password = cls.config['security'][0]['password']
        cls.auth = HTTPBasicAuth(cls.username, cls.password)

        # Server configuration
        cls.base_url = 'http://127.0.0.1:44556'

        # Test topics from config
        cls.test_topics = [
            cls.config['pubsub_topic'][0]['name'],
            cls.config['pubsub_topic'][1]['name'],
            cls.config['pubsub_topic'][2]['name']
        ]

# ################################################################################################################################

    def setUp(self):
        """ Skip tests if no config available.
        """
        if self.skip_tests:
            self.skipTest('Zato_PubSub_YAML_Config environment variable not set')

# ################################################################################################################################

    def tearDown(self):
        """ Clean up after tests.
        """
        if self.skip_tests:
            return

        # Clean up broker
        broker_config = get_broker_config()
        _ = cleanup_broker_impl(broker_config, 15672)

        # Unsubscribe from all topics to clear any existing subscriptions
        for topic in self.test_topics:
            try:
                _ = requests.post(
                    f'{self.base_url}/pubsub/unsubscribe/topic/{topic}',
                    auth=self.auth
                )
            except Exception:
                pass

# ################################################################################################################################

    def test_subscribe_then_unsubscribe(self):
        """ Test subscribing to a topic and then unsubscribing.
        """
        topic = self.test_topics[0]  # demo.1

        # Subscribe to topic
        response = requests.post(
            f'{self.base_url}/pubsub/subscribe/topic/{topic}',
            auth=self.auth
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_ok'])

        # Wait 0.1 second
        time.sleep(0.1)

        # Unsubscribe from topic
        response = requests.post(
            f'{self.base_url}/pubsub/unsubscribe/topic/{topic}',
            auth=self.auth
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['is_ok'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
