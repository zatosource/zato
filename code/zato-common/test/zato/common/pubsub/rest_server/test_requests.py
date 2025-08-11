# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import http.client as http_client
import logging
import time
from unittest import main

# requests
import requests

# Zato
from zato.common.test.unittest_pubsub_requests import PubSubRESTServerBaseTestCase

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerTestCase(PubSubRESTServerBaseTestCase):
    """ Test cases for the pub/sub REST server.
    """

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

# ################################################################################################################################

    def setUp(self):
        """ Skip tests if no config available.
        """
        if self.skip_tests:
            self.skipTest('Zato_PubSub_YAML_Config environment variable not set')

# ################################################################################################################################

    def _call_diagnostics(self):
        """ Call diagnostics endpoint and log the response.
        """
        try:
            diagnostics_url = f'{self.base_url}/pubsub/admin/diagnostics'
            response = requests.get(diagnostics_url, auth=self.auth)
            if response.status_code == 200:
                import json
                data = response.json()
                pretty_json = json.dumps(data, indent=4)
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
        self._call_diagnostics()
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
        self._call_diagnostics()

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
        self.assertGreater(len(messages_data['data']), 0)
        self._call_diagnostics()

        # Verify message content
        message = messages_data['data'][0]
        self.assertEqual(message['data'], 'Test message for demo.1')
        self.assertEqual(message['topic_name'], topic_name)
        self.assertEqual(message['correl_id'], 'test-correlation-id')
        self.assertEqual(message['priority'], 7)

        # Step 4: Unsubscribe from the topic we subscribed to
        unsubscribe_url = f'{self.base_url}/pubsub/unsubscribe/topic/{topic_name}'
        response = requests.post(unsubscribe_url, auth=self.auth)
        self.assertEqual(response.status_code, 200)

        unsubscribe_data = response.json()
        self.assertTrue(unsubscribe_data['is_ok'])
        self._call_diagnostics()
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
        self._call_diagnostics()

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
            self._call_diagnostics()

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
            self._call_diagnostics()

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
        self._call_diagnostics()

        # Verify we got messages from both topics
        received_topics = {msg['topic_name'] for msg in messages_data['data']}
        self.assertIn(topic1, received_topics)
        self.assertIn(topic2, received_topics)

# ################################################################################################################################

    def test_publish_without_subscription(self):
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
