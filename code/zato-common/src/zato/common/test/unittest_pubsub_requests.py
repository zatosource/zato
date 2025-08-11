# -*- coding: utf-8 -*-

"""
Copyright (C) 2025 Dariusz Suchojad <dsuch at zato.io>

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import http.client as http_client
import json
import logging
import os
from unittest import TestCase

# PyYAML
from yaml import load as yaml_load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

# Requests
import requests
from requests.auth import HTTPBasicAuth

# Zato
from zato.common.pubsub.util import cleanup_broker_impl, get_broker_config

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerBaseTestCase(TestCase):
    """ Base test case for pub/sub REST server tests with common setup and diagnostics.
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
            cls.config = yaml_load(f, Loader=Loader)

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

        # Set up HTTP client patching
        cls._setup_http_patching()

    @classmethod
    def _setup_http_patching(cls):
        """ Set up HTTP client patching for detailed logging.
        """
        # Disable default HTTP traffic logging to avoid duplicates
        http_client.HTTPConnection.debuglevel = 0

        def patched_send(self, data):
            logger = logging.getLogger('http.client')
            if isinstance(data, bytes):
                logger.debug(f'send: {data.decode("utf-8", errors="replace")}')
            else:
                logger.debug(f'send: {data}')
            return cls._original_send(self, data)

        def patched_getresponse(self):
            response = cls._original_getresponse(self)
            logger = logging.getLogger('http.client')
            version = f'HTTP/{response.version // 10}.{response.version % 10}'
            logger.debug(f'reply: \'{version} {response.status} {response.reason}\\r\\n\'')
            for header, value in response.getheaders():
                logger.debug(f'header: {header}: {value}')
            return response

        def patched_read(self, amt=None):
            data = cls._original_read(self, amt)
            if data:
                logger = logging.getLogger('http.client.response')
                try:
                    decoded = data.decode("utf-8")
                    logger.debug(f'Response body: {decoded}')
                except UnicodeDecodeError:
                    logger.debug(f'Response body (binary): {len(data)} bytes')
            return data

        # Store original methods
        cls._original_send = http_client.HTTPConnection.send
        cls._original_getresponse = http_client.HTTPConnection.getresponse
        cls._original_read = http_client.HTTPResponse.read

        # Apply patches
        http_client.HTTPConnection.send = patched_send
        http_client.HTTPConnection.getresponse = patched_getresponse
        http_client.HTTPResponse.read = patched_read

    def setUp(self):
        """ Skip tests if no config available.
        """
        if self.skip_tests:
            self.skipTest('Zato_PubSub_YAML_Config environment variable not set')

    def _call_diagnostics(self):
        """ Call diagnostics endpoint and log the response.
        """
        try:
            diagnostics_url = f'{self.base_url}/pubsub/admin/diagnostics'
            response = requests.get(diagnostics_url, auth=self.auth)
            if response.status_code == 200:
                data = response.json()
                pretty_json = json.dumps(data, indent=2)
                logger.info(f'Diagnostics response:\n{pretty_json}')
            else:
                logger.warning(f'Diagnostics failed with status {response.status_code}: {response.text}')
        except Exception as e:
            logger.error(f'Error calling diagnostics: {e}')

    def tearDown(self):
        """ Clean up after tests.
        """
        if self.skip_tests:
            return

        # Clean up broker
        broker_config = get_broker_config()
        _ = cleanup_broker_impl(broker_config, 15672)

        # Unsubscribe from all topics to clear any existing subscriptions
        for topic_name in self.test_topics:
            try:
                unsubscribe_url = f'{self.base_url}/pubsub/unsubscribe/topic/{topic_name}'
                _ = requests.post(unsubscribe_url, auth=self.auth)
                self._call_diagnostics()
            except:
                pass

# ################################################################################################################################
# ################################################################################################################################
