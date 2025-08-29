# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
import subprocess
from http.client import BAD_REQUEST, OK
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

    def _wait_for_objects_in_diagnostics(self) -> 'any_':
        """ Wait for all test objects to appear in diagnostics response.
        """
        max_attempts = 100_000_000
        attempt = 0
        data = None
        sleep_time = 0.1

        while attempt < max_attempts:
            attempt += 1
            logger.debug(f'Checking diagnostics for objects (attempt {attempt}/{max_attempts})')

            data = self._call_diagnostics()
            if not data:
                logger.debug('No diagnostics data received')
                time.sleep(sleep_time)
                continue

            diagnostics_data = data.get('data', {})
            if not diagnostics_data:
                logger.debug('No data section in diagnostics response')
                time.sleep(sleep_time)
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
                logger.debug('All config objects found in diagnostics')
                return data
            else:
                logger.debug(f'Missing objects: {missing_objects}, retrying in {sleep_time}s')
                time.sleep(sleep_time)

        logger.error(f'Timeout waiting for objects to appear in diagnostics after {max_attempts} attempts')
        return data

# ################################################################################################################################

    def _publish_message(self, topic_name:'str', message_data:'any_') -> 'any_':
        """ Publish a message to a topic.
        """
        publish_url = f'{self.base_url}/pubsub/topic/{topic_name}'
        publish_payload = {'data': message_data}

        publish_response = requests.post(publish_url, json=publish_payload, auth=self.auth)

        # Only wait for messages if the publish was successful
        if publish_response.status_code == OK:
            logger.info('Message published to %s', topic_name)
            # First check RabbitMQ to ensure there's at least one message in the queue ..
            self._wait_for_messages_in_queue()

        # .. and now return the publication response ..
        return publish_response

# ################################################################################################################################

    def _get_messages(self, max_messages:'int'=10, max_len:'int'=1000) -> 'any_':
        """ Get messages from user's queue.
        """
        get_messages_url = f'{self.base_url}/pubsub/messages/get'
        get_payload = {'max_messages': max_messages, 'max_len': max_len}
        return requests.post(get_messages_url, json=get_payload, auth=self.auth)

# ################################################################################################################################

    def _wait_for_messages_in_queue(self, timeout:'int'=300_000_000) -> 'None':
        """ Wait for at least one message to appear in the user's queue via rabbitmqctl.
        """
        logger.info('Checking stats')

        # Find the user's queue name by checking subscriptions
        user_queue_name = None
        diagnostics_data = self._call_diagnostics()
        if diagnostics_data and 'data' in diagnostics_data:
            subscriptions = diagnostics_data['data'].get('subscriptions', {})
            for subs in subscriptions.values():
                user_sec_name = self.config['security'][0]['name']
                if user_sec_name in subs:
                    subscription = subs[user_sec_name]
                    user_queue_name = subscription.get('sub_key')
                    break

        if not user_queue_name:
            logger.error('Could not find user queue name, cannot proceed')
            raise Exception('User queue name not found in diagnostics')

        logger.info(f'Looking for queue: {user_queue_name}')

        # Use the Zato internal vhost
        vhost_name = 'zato.internal'

        # First, list all queues to find the full queue name
        try:
            result = subprocess.run(
                ['sudo', 'rabbitmqctl', 'list_queues', '-p', vhost_name, 'name'],
                capture_output=True,
                text=True,
                check=True
            )

            # Parse output to find matching queue
            matching_queue = None
            for line in result.stdout.strip().split('\n'):
                if line and not line.startswith('Timeout:') and not line.startswith('Listing'):
                    if user_queue_name in line:
                        matching_queue = line.strip()
                        break

            if matching_queue:
                user_queue_name = matching_queue
                logger.info(f'Found matching queue: {user_queue_name}')
            else:
                logger.error(f'No queue found containing {user_queue_name}')
                raise Exception(f'Queue not found: {user_queue_name}')
        except subprocess.CalledProcessError as e:
            logger.error(f'Error listing queues: {e}')
            raise

        # Check for messages in the queue
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    ['sudo', 'rabbitmqctl', 'list_queues', '-p', vhost_name, 'name', 'messages'],
                    capture_output=True,
                    text=True,
                    check=True
                )

                # Parse output to find our queue and its message count
                for line in result.stdout.strip().split('\n'):
                    if user_queue_name in line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            message_count = int(parts[1])
                            if message_count > 0:
                                message_word = 'message' if message_count == 1 else 'messages'
                                logger.info(f'Found {message_count} {message_word} in queue {user_queue_name}')
                                return
                            else:
                                logger.info(f'Stats found no messages in queue {user_queue_name}, waiting...')
                        break
            except (subprocess.CalledProcessError, ValueError) as e:
                logger.warning(f'Error checking queue status: {e}')

            time.sleep(0.5)

        logger.warning(f'Timeout waiting for messages in queue {user_queue_name}')

# ################################################################################################################################

    def _subscribe_to_topic(self, topic_name:'str') -> 'any_':
        """ Subscribe to a topic.
        """
        subscribe_url = f'{self.base_url}/pubsub/subscribe/topic/{topic_name}'
        return requests.post(subscribe_url, auth=self.auth)

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
        logger.info('Before publish to %s', topic_name)

        # Publish message to topic and verify it was successful ..
        publish_response = self._publish_message(topic_name, test_message)

        publish_data = self._extract_publish_data(publish_response)
        self._assert_publish_success(publish_response, publish_data)

        # .. retrieve message from the user's queue and verify it was received ..
        get_response = self._get_messages()
        logger.info('Message received')

        get_data = self._extract_get_messages_data(get_response)
        self._assert_get_messages_success(get_response, get_data)
        self._assert_message_content(get_data['messages'], test_message, publish_data['msg_id'])

        # .. unsubscribe from topic ..
        unsubscribe_response = self._unsubscribe_from_topic(topic_name)
        unsubscribe_data = self._extract_unsubscribe_data(unsubscribe_response)
        self._assert_unsubscribe_success(unsubscribe_response, unsubscribe_data)

        # .. verify that the user is no longer subscribed to topic.
        self._assert_user_not_subscribed_to_topic(topic_name)

    def _test_topic_validation(self) -> 'None':
        """ Test topic name validation for publish, subscribe, and unsubscribe operations.
        """
        class InvalidTopic:
            def __init__(self, name, expected_error):
                self.name = name
                self.expected_error = expected_error

        long_topic = InvalidTopic('a' * 201, 'Invalid request data')
        hash_topic = InvalidTopic('test%23topic', 'Invalid request data')
        unicode_topic = InvalidTopic('test.Ω', 'Invalid request data')

        # Test long topic name - publish
        publish_response = self._publish_message(long_topic.name, {'test': 'data'})
        self.assertEqual(publish_response.status_code, BAD_REQUEST)
        self.assertIn(long_topic.expected_error, publish_response.text)

        # Test long topic name - subscribe
        subscribe_response = self._subscribe_to_topic(long_topic.name)
        self.assertEqual(subscribe_response.status_code, BAD_REQUEST)
        self.assertIn(long_topic.expected_error, subscribe_response.text)

        # Test long topic name - unsubscribe
        unsubscribe_response = self._unsubscribe_from_topic(long_topic.name)
        self.assertEqual(unsubscribe_response.status_code, BAD_REQUEST)
        self.assertIn(long_topic.expected_error, unsubscribe_response.text)

        # Test hash character topic - publish
        publish_response = self._publish_message(hash_topic.name, {'test': 'data'})
        self.assertEqual(publish_response.status_code, BAD_REQUEST)
        self.assertIn(hash_topic.expected_error, publish_response.text)

        # Test hash character topic - subscribe
        subscribe_response = self._subscribe_to_topic(hash_topic.name)
        self.assertEqual(subscribe_response.status_code, BAD_REQUEST)
        self.assertIn(hash_topic.expected_error, subscribe_response.text)

        # Test hash character topic - unsubscribe
        unsubscribe_response = self._unsubscribe_from_topic(hash_topic.name)
        self.assertEqual(unsubscribe_response.status_code, BAD_REQUEST)
        self.assertIn(hash_topic.expected_error, unsubscribe_response.text)

        # Test unicode character topic - publish
        publish_response = self._publish_message(unicode_topic.name, {'test': 'data'})
        self.assertEqual(publish_response.status_code, BAD_REQUEST)
        self.assertIn(unicode_topic.expected_error, publish_response.text)

        # Test unicode character topic - subscribe
        subscribe_response = self._subscribe_to_topic(unicode_topic.name)
        self.assertEqual(subscribe_response.status_code, BAD_REQUEST)
        self.assertIn(unicode_topic.expected_error, subscribe_response.text)

        # Test unicode character topic - unsubscribe
        unsubscribe_response = self._unsubscribe_from_topic(unicode_topic.name)
        self.assertEqual(unsubscribe_response.status_code, BAD_REQUEST)
        self.assertIn(unicode_topic.expected_error, unsubscribe_response.text)

# ################################################################################################################################

    def test_full_path(self) -> 'None':
        """ Test full path with enmasse configuration.
        """
        # Local variables
        max_loops = 1

        # Skip auto-unsubscribe for this test since we want to control cleanup manually ..
        self.skip_auto_unsubscribe = True

        # .. first test topic validation ..
        self._test_topic_validation()

        # .. wait for all configuration objects to appear in diagnostics ..
        self._wait_for_objects_in_diagnostics()

        # .. prepare test data ..
        topic_name_1 = 'demo.1'
        topic_name_2 = 'demo.2'
        topic_name_3 = 'demo.3'

        test_message_1 = {'first': 'message1', 'id': 1, 'timestamp': '2025-01-01T10:00:00Z'}
        test_message_2 = {'second': 'message2', 'id': 2, 'timestamp': '2025-01-02T11:00:00Z'}
        test_message_3 = {'third': 'message3', 'id': 3, 'timestamp': '2025-01-03T11:00:00Z'}

        # .. run complete scenarios in a loop ..
        for idx in range(1, max_loops+1):

            # .. log progress ..
            logger.info('Loop %s/%s', idx, max_loops)

            # .. if this is not the first iteration, we need to subscribe our client to all the topics ..
            # .. because in the first iteration we have unbuscribed from them all ..
            if idx > 1:
                self._subscribe_to_topic(topic_name_1)
                self._subscribe_to_topic(topic_name_2)
                self._subscribe_to_topic(topic_name_3)

            # .. run complete scenario for demo.1 ..
            self._run_complete_topic_scenario(topic_name_1, test_message_1)

            # .. run complete scenario for demo.2 ..
            self._run_complete_topic_scenario(topic_name_2, test_message_2)

            # .. run complete scenario for demo.3 ..
            self._run_complete_topic_scenario(topic_name_3, test_message_3)

            # .. run the full cycle with one topic only now ..
            for sub_idx in range(max_loops):

                logger.info('Sub-loop %s/%s/%s', idx, max_loops, sub_idx)

                # .. subscribe the user to topic demo.1 again ..
                self._subscribe_to_topic(topic_name_1)

                # .. run complete scenario for demo.1 again ..
                self._run_complete_topic_scenario(topic_name_1, test_message_1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
