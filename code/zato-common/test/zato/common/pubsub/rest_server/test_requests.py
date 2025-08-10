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

logging.basicConfig(level=logging.DEBUG)

# Enable HTTP traffic logging
http_client.HTTPConnection.debuglevel = 1

# Patch HTTPResponse to log response body
original_read = http_client.HTTPResponse.read

def patched_read(self, amt=None):
    data = original_read(self, amt)
    if data:
        logger = logging.getLogger('http.client.response')
        logger.debug(f'Response body: {data.decode("utf-8", errors="replace")}')
    return data

http_client.HTTPResponse.read = patched_read

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerTestCase(TestCase):
    """ Test cases for the pub/sub REST server.
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

    def setUp(self):
        """ Skip tests if no config available.
        """
        if self.skip_tests:
            self.skipTest("Zato_PubSub_YAML_Config environment variable not set")

        # Clean up broker before running tests
        broker_config = get_broker_config()
        _ = cleanup_broker_impl(broker_config, 15672)

# ################################################################################################################################

    def test_subscribe_publish_get_unsubscribe_flow(self):
        """ Test complete pub/sub flow: subscribe -> publish -> get messages -> unsubscribe.
        """
        topic_name = self.test_topics[0]  # demo.1

        # Step 1: Subscribe to topic
        subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        response = requests.post(subscribe_url, auth=self.auth)
        self.assertEqual(response.status_code, 200)

        subscribe_data = response.json()
        self.assertTrue(subscribe_data['is_ok'])
        self.assertIn('cid', subscribe_data)

        # Step 2: Publish a message
        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'
        message_data = {
            'data': 'Test message for demo.1',
            'priority': 7,
            'expiration': 3600,
            'correl_id': 'test-correlation-id'
        }

        response = requests.post(
            publish_url,
            json=message_data,
            auth=self.auth,
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)

        publish_data = response.json()
        self.assertTrue(publish_data['is_ok'])
        self.assertIn('msg_id', publish_data)
        self.assertIn('cid', publish_data)

        # Step 3: Get messages (with small delay for message delivery)
        time.sleep(0.1)

        get_messages_url = f'{self.base_url}/pubsub/messages/get'
        get_data = {
            'max_messages': 10,
            'max_len': 1000000
        }

        response = requests.post(
            get_messages_url,
            json=get_data,
            auth=self.auth,
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)

        messages_data = response.json()
        self.assertTrue(messages_data['is_ok'])
        self.assertIn('data', messages_data)
        self.assertGreater(len(messages_data['data']), 0)

        # Verify message content
        message = messages_data['data'][0]
        self.assertEqual(message['data'], 'Test message for demo.1')
        self.assertEqual(message['topic_name'], topic_name)
        self.assertEqual(message['correl_id'], 'test-correlation-id')
        self.assertEqual(message['priority'], 7)

        # Step 4: Unsubscribe from all topics
        for test_topic in self.test_topics:
            unsubscribe_url = f'{self.base_url}/pubsub/unsubscribe/topic/{test_topic}'
            response = requests.post(unsubscribe_url, auth=self.auth)
            self.assertEqual(response.status_code, 200)

            unsubscribe_data = response.json()
            self.assertTrue(unsubscribe_data['is_ok'])
            self.assertIn('cid', unsubscribe_data)

        # Step 5: Publish another message after unsubscribing
        response = requests.post(
            publish_url,
            json=message_data,
            auth=self.auth,
            headers={'Content-Type': 'application/json'}
        )

        # Publishing should still work even without subscribers
        self.assertEqual(response.status_code, 200)

        # Step 6: Try to get messages - should return 400 error for unsubscribed user
        response = requests.post(
            get_messages_url,
            json=get_data,
            auth=self.auth,
            headers={'Content-Type': 'application/json'}
        )

        self.assertEqual(response.status_code, 400)
        error_data = response.json()
        self.assertFalse(error_data['is_ok'])
        self.assertIn('No subscription found for user', error_data['details'])

# ################################################################################################################################

    def test_multiple_topics_subscription(self):
        """ Test subscribing to multiple topics and publishing to each.
        """
        topic1 = self.test_topics[1]  # demo.2
        topic2 = self.test_topics[2]  # demo.3

        # Subscribe to both topics
        for topic_name in [topic1, topic2]:
            subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
            response = requests.post(subscribe_url, auth=self.auth)
            self.assertEqual(response.status_code, 200)

            subscribe_data = response.json()
            self.assertTrue(subscribe_data['is_ok'])

        # Publish messages to both topics
        messages = {
            topic1: 'Message for demo.2 topic',
            topic2: 'Message for demo.3 topic'
        }

        for topic_name, message_text in messages.items():
            publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'
            message_data = {
                'data': message_text,
                'priority': 5,
                'correl_id': f'test-{topic_name}'
            }

            response = requests.post(
                publish_url,
                json=message_data,
                auth=self.auth,
                headers={'Content-Type': 'application/json'}
            )
            self.assertEqual(response.status_code, 200)

            publish_data = response.json()
            self.assertTrue(publish_data['is_ok'])

        # Get all messages
        get_messages_url = f'{self.base_url}/pubsub/messages/get'
        get_data = {
            'max_messages': 10,
            'max_len': 1000000
        }

        response = requests.post(
            get_messages_url,
            json=get_data,
            auth=self.auth,
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)

        messages_data = response.json()
        self.assertTrue(messages_data['is_ok'])
        self.assertGreaterEqual(len(messages_data['data']), 2)

        # Verify we got messages from both topics
        received_topics = {msg['topic_name'] for msg in messages_data['data']}
        self.assertIn(topic1, received_topics)
        self.assertIn(topic2, received_topics)

        # Unsubscribe from both topics
        for topic_name in [topic1, topic2]:
            unsubscribe_url = f'{self.base_url}/pubsub/unsubscribe/topic/{topic_name}'
            response = requests.post(unsubscribe_url, auth=self.auth)
            self.assertEqual(response.status_code, 200)

            unsubscribe_data = response.json()
            self.assertTrue(unsubscribe_data['is_ok'])

# ################################################################################################################################

    def xtest_publish_without_subscription(self):
        """ Test publishing to a topic without being subscribed.
        """
        topic_name = self.test_topics[0]  # demo.1

        # Publish message without subscription
        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'
        message_data = {
            'data': 'Message without subscription',
            'priority': 3
        }

        response = requests.post(
            publish_url,
            json=message_data,
            auth=self.auth,
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)

        publish_data = response.json()
        self.assertTrue(publish_data['is_ok'])
        self.assertIn('msg_id', publish_data)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
