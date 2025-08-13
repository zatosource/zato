# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from unittest import main

# requests
import requests

# Zato
from zato.common.test.unittest_pubsub_requests import PubSubRESTServerBaseTestCase

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerTestCase(PubSubRESTServerBaseTestCase):
    """ Test cases for the pub/sub REST server.
    """

    def xtest_subscribe_publish_get_unsubscribe_flow(self):
        """ Test complete pub/sub flow: subscribe -> publish -> get messages -> unsubscribe.
        """
        topic_name = self.test_topics[0]  # demo.1

        # Step 1: Subscribe to topic
        subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        response = requests.post(subscribe_url, auth=self.auth)
        self.assertEqual(response.status_code, 200)

        subscribe_data = response.json()
        self.assertTrue(subscribe_data['is_ok'])

        # Check diagnostics after subscribe - should show subscription
        diagnostics_after_subscribe = self._call_diagnostics()
        self.assertIsNotNone(diagnostics_after_subscribe)
        self.assertTrue(diagnostics_after_subscribe['is_ok'])
        self.assertIn('data', diagnostics_after_subscribe)

        # Verify subscription exists
        subscriptions = diagnostics_after_subscribe['data']['subscriptions']
        self.assertIn(topic_name, subscriptions)
        self.assertIn('demo_sec_def', subscriptions[topic_name])
        self.assertIn('sub_key', subscriptions[topic_name]['demo_sec_def'])

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

        # Check diagnostics after publish - subscription should still exist
        diagnostics_after_publish = self._call_diagnostics()
        self.assertIsNotNone(diagnostics_after_publish)
        self.assertTrue(diagnostics_after_publish['is_ok'])
        self.assertIn('data', diagnostics_after_publish)

        # Verify subscription still exists
        subscriptions = diagnostics_after_publish['data']['subscriptions']
        self.assertIn(topic_name, subscriptions)
        self.assertIn('demo_sec_def', subscriptions[topic_name])

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

        # Check diagnostics after getting messages - subscription should still exist
        diagnostics_after_get = self._call_diagnostics()
        self.assertIsNotNone(diagnostics_after_get)
        self.assertTrue(diagnostics_after_get['is_ok'])
        self.assertIn('data', diagnostics_after_get)

        # Verify subscription still exists
        subscriptions = diagnostics_after_get['data']['subscriptions']
        self.assertIn(topic_name, subscriptions)
        self.assertIn('demo_sec_def', subscriptions[topic_name])

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

        # Check diagnostics after unsubscribe - subscription should be removed
        diagnostics_after_unsubscribe = self._call_diagnostics()
        self.assertIsNotNone(diagnostics_after_unsubscribe)
        self.assertTrue(diagnostics_after_unsubscribe['is_ok'])
        self.assertIn('data', diagnostics_after_unsubscribe)

        # Verify subscription no longer exists for this topic
        subscriptions = diagnostics_after_unsubscribe['data']['subscriptions']
        self.assertNotIn(topic_name, subscriptions)

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

        # Check diagnostics after publish without subscription - should still have no subscriptions
        diagnostics_after_publish_no_sub = self._call_diagnostics()
        self.assertIsNotNone(diagnostics_after_publish_no_sub)
        self.assertTrue(diagnostics_after_publish_no_sub['is_ok'])
        self.assertIn('data', diagnostics_after_publish_no_sub)

        # Verify no subscription exists for this topic
        subscriptions = diagnostics_after_publish_no_sub['data']['subscriptions']
        self.assertNotIn(topic_name, subscriptions)

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

    def xtest_multiple_topics_subscription(self):
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

            # Check diagnostics after subscribe - should show subscription for this topic
            diagnostics_after_subscribe = self._call_diagnostics()
            self.assertIsNotNone(diagnostics_after_subscribe)
            self.assertTrue(diagnostics_after_subscribe['is_ok'])
            self.assertIn('data', diagnostics_after_subscribe)

            # Verify subscription exists for this topic
            subscriptions = diagnostics_after_subscribe['data']['subscriptions']
            self.assertIn(topic_name, subscriptions)
            self.assertIn('demo_sec_def', subscriptions[topic_name])
            self.assertIn('sub_key', subscriptions[topic_name]['demo_sec_def'])

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

            # Check diagnostics after publish - subscriptions should still exist
            diagnostics_after_publish = self._call_diagnostics()
            self.assertIsNotNone(diagnostics_after_publish)
            self.assertTrue(diagnostics_after_publish['is_ok'])
            self.assertIn('data', diagnostics_after_publish)

            # Verify subscriptions exist for both topics
            subscriptions = diagnostics_after_publish['data']['subscriptions']
            self.assertIn(topic1, subscriptions)
            self.assertIn(topic2, subscriptions)
            self.assertIn('demo_sec_def', subscriptions[topic1])
            self.assertIn('demo_sec_def', subscriptions[topic2])

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

        # Check diagnostics after getting messages - subscriptions should still exist
        diagnostics_after_get = self._call_diagnostics()
        self.assertIsNotNone(diagnostics_after_get)
        self.assertTrue(diagnostics_after_get['is_ok'])
        self.assertIn('data', diagnostics_after_get)

        # Verify subscriptions exist for both topics
        subscriptions = diagnostics_after_get['data']['subscriptions']
        self.assertIn(topic1, subscriptions)
        self.assertIn(topic2, subscriptions)
        self.assertIn('demo_sec_def', subscriptions[topic1])
        self.assertIn('demo_sec_def', subscriptions[topic2])

        # Verify we got messages from both topics
        received_topics = {msg['topic_name'] for msg in messages_data['data']}
        self.assertIn(topic1, received_topics)
        self.assertIn(topic2, received_topics)

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
