# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from unittest import main

# Requests
import requests

# Zato
from zato.common.test.unittest_pubsub_requests import PubSubRESTServerBaseTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTServerTestCase(PubSubRESTServerBaseTestCase):
    """ Test cases for the pub/sub REST server.
    """

# ################################################################################################################################

    def _wait_for_objects_in_diagnostics(self) -> 'any_':
        """ Wait for all test objects to appear in diagnostics response.
        """
        max_attempts = 100_000_000
        attempt = 0
        data = None

        while attempt < max_attempts:
            attempt += 1
            logger.info(f'Checking diagnostics for objects (attempt {attempt}/{max_attempts})')

            data = self._call_diagnostics()
            if not data:
                logger.info('No diagnostics data received')
                time.sleep(0.5)
                continue

            diagnostics_data = data.get('data', {})
            if not diagnostics_data:
                logger.info('No data section in diagnostics response')
                time.sleep(0.5)
                continue

            missing_objects = []

            # Check topics
            if 'pubsub_topic' in self.config:
                topics_data = diagnostics_data.get('topics', {})
                for topic_config in self.config['pubsub_topic']:
                    topic_name = topic_config['name']
                    if topic_name not in topics_data:
                        missing_objects.append(f'topic:{topic_name}')

            # Check users
            if 'security' in self.config:
                users_data = diagnostics_data.get('users', {})
                for security_config in self.config['security']:
                    username = security_config['username']
                    if username not in users_data:
                        missing_objects.append(f'user:{username}')

            # Check permissions - pattern_matcher clients use usernames
            if 'pubsub_permission' in self.config:
                pattern_matcher_data = diagnostics_data.get('pattern_matcher', {})
                clients_data = pattern_matcher_data.get('clients', {})
                for permission_config in self.config['pubsub_permission']:
                    security_name = permission_config['security']
                    # Find the username that has this security definition
                    username = None
                    for user_config in self.config.get('security', []):
                        if user_config.get('name') == security_name:
                            username = user_config.get('username')
                            break
                    if username and username not in clients_data:
                        missing_objects.append(f'permission:{username}')

            # Check subscriptions
            if 'pubsub_subscription' in self.config:
                subscriptions_data = diagnostics_data.get('subscriptions', {})
                for subscription_config in self.config['pubsub_subscription']:
                    for topic_name in subscription_config['topic_list']:
                        if topic_name not in subscriptions_data:
                            missing_objects.append(f'subscription:{topic_name}')

            if not missing_objects:
                logger.info('All config objects found in diagnostics')
                return data
            else:
                logger.info(f'Missing objects: {missing_objects}, retrying in 0.5s')
                time.sleep(0.5)

        logger.error(f'Timeout waiting for objects to appear in diagnostics after {max_attempts} attempts')
        return data

# ################################################################################################################################

    def _publish_message(self, topic_name:'str', message_data:'any_') -> 'any_':
        """ Publish a message to a topic.
        """
        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'
        publish_payload = {'data': message_data}
        return requests.post(publish_url, json=publish_payload, auth=self.auth)

# ################################################################################################################################

    def _get_messages(self, max_messages:'int'=10, max_len:'int'=1000) -> 'any_':
        """ Get messages from user's queue.
        """
        get_messages_url = f'{self.base_url}/pubsub/messages/get'
        get_payload = {'max_messages': max_messages, 'max_len': max_len}
        return requests.post(get_messages_url, json=get_payload, auth=self.auth)

# ################################################################################################################################

    def _unsubscribe_from_topic(self, topic_name:'str') -> 'any_':
        """ Unsubscribe from a topic.
        """
        unsubscribe_url = f'{self.base_url}/pubsub/unsubscribe/topic/{topic_name}'
        return requests.post(unsubscribe_url, auth=self.auth)

    def _extract_publish_data(self, response:'any_') -> 'any_':
        """ Extract data from publish response.
        """
        return response.json()

# ################################################################################################################################

    def _extract_get_messages_data(self, response:'any_') -> 'any_':
        """ Extract data from get messages response.
        """
        return response.json()

# ################################################################################################################################

    def _extract_unsubscribe_data(self, response:'any_') -> 'any_':
        """ Extract data from unsubscribe response.
        """
        return response.json()

    def _assert_publish_success(self, response:'any_', data:'any_') -> 'None':
        """ Assert that publish response is successful.
        """
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['is_ok'])
        self.assertIn('msg_id', data)

# ################################################################################################################################

    def _assert_get_messages_success(self, response:'any_', data:'any_') -> 'None':
        """ Assert that get messages response is successful.
        """
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['is_ok'])

# ################################################################################################################################

    def _assert_unsubscribe_success(self, response:'any_', data:'any_') -> 'None':
        """ Assert that unsubscribe response is successful.
        """
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['is_ok'])

# ################################################################################################################################

    def _assert_message_content(self, messages:'any_', expected_message:'any_', expected_msg_id:'str') -> 'None':
        """ Assert message content matches expectations.
        """
        self.assertEqual(len(messages), 1)
        received_message = messages[0]
        self.assertEqual(received_message['data'], expected_message)
        self.assertEqual(received_message['msg_id'], expected_msg_id)

# ################################################################################################################################

    def _assert_user_not_subscribed_to_topic(self, topic_name:'str') -> 'None':
        """ Assert that the user is not subscribed to the given topic by checking diagnostics.
        """
        diagnostics_data = self._call_diagnostics()
        self.assertIsNotNone(diagnostics_data)

        data_section = diagnostics_data.get('data', {})
        subscriptions = data_section.get('subscriptions', {})

        # Check if topic exists in subscriptions
        if topic_name in subscriptions:
            topic_subscriptions = subscriptions[topic_name]
            # Check if our user's security definition is not in the topic subscriptions
            security_config = self.config['security']
            first_security = security_config[0]
            user_sec_name = first_security['name']
            self.assertNotIn(user_sec_name, topic_subscriptions, f'User should not be subscribed to topic {topic_name}')

# ################################################################################################################################

    def _run_complete_topic_scenario(self, topic_name:'str', test_message:'any_') -> 'None':
        """ Run complete scenario for a topic: publish, get, unsubscribe, verify.
        """
        # .. publish message to topic and verify it was successful ..
        publish_response = self._publish_message(topic_name, test_message)
        publish_data = self._extract_publish_data(publish_response)
        self._assert_publish_success(publish_response, publish_data)

        # .. retrieve message from the user's queue and verify it was received ..
        get_response = self._get_messages()
        get_data = self._extract_get_messages_data(get_response)
        self._assert_get_messages_success(get_response, get_data)
        self._assert_message_content(get_data['messages'], test_message, publish_data['msg_id'])

        # .. unsubscribe from topic ..
        unsubscribe_response = self._unsubscribe_from_topic(topic_name)
        unsubscribe_data = self._extract_unsubscribe_data(unsubscribe_response)
        self._assert_unsubscribe_success(unsubscribe_response, unsubscribe_data)

        # .. verify that the user is no longer subscribed to topic.
        self._assert_user_not_subscribed_to_topic(topic_name)

# ################################################################################################################################

    def test_full_path(self) -> 'None':
        """ Test full path with enmasse configuration.
        """
        # Skip auto-unsubscribe for this test since we want to control cleanup manually ..
        self.skip_auto_unsubscribe = True

        # .. wait for all configuration objects to appear in diagnostics ..
        self._wait_for_objects_in_diagnostics()

        # .. prepare test data ..
        topic_name_1 = 'demo.1'
        topic_name_2 = 'demo.2'
        topic_name_3 = 'demo.3'

        test_message_1 = {'first': 'message1', 'id': 1, 'timestamp': '2025-01-01T10:00:00Z'}
        test_message_2 = {'second': 'message2', 'id': 2, 'timestamp': '2025-01-02T11:00:00Z'}
        test_message_3 = {'third': 'message3', 'id': 3, 'timestamp': '2025-01-03T11:00:00Z'}

        # .. run complete scenario for demo.1 ..
        self._run_complete_topic_scenario(topic_name_1, test_message_1)

        # .. run complete scenario for demo.2 ..
        self._run_complete_topic_scenario(topic_name_2, test_message_2)

        # .. run complete scenario for demo.3 ..
        self._run_complete_topic_scenario(topic_name_3, test_message_3)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
