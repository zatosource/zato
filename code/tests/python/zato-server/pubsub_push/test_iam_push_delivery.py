# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import unittest

# local
from _client import PublishClient
from config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.iam_push_delivery')

# ################################################################################################################################
# ################################################################################################################################

class TestIAMPushDelivery(unittest.TestCase):
    """ Tests for push delivery to IAM topic webhook receivers.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(
            TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

# ################################################################################################################################

    def test_publish_to_all_iam_topics(self) -> 'None':
        """ Publish to all 5 IAM topics, verify each receiver got exactly 1 message
        and the data round-tripped correctly.
        """

        # Define each topic with its payload and the field to verify ..
        topics_to_test:'list[tuple[str, anydict, str, str]]' = [
            ('iam.user.created',    {'user_id': 'user1', 'action': 'created'},       'user_id', 'user1'),
            ('iam.user.deleted',    {'user_id': 'user2', 'reason': 'account_closed'}, 'user_id', 'user2'),
            ('iam.role.assigned',   {'user_id': 'user3', 'role': 'admin'},            'role',    'admin'),
            ('iam.password.changed', {'user_id': 'user4'},                            'user_id', 'user4'),
            ('iam.login.failed',    {'user_id': 'user5', 'ip': '10.0.0.1'},          'ip',      '10.0.0.1'),
        ]

        # Publish to all 5 topics ..
        for topic_name, publish_data, _, _ in topics_to_test:
            _ = self.publisher.publish(topic_name, publish_data)
            logger.info('Published to %s -> %s', topic_name, publish_data)

        # .. wait for delivery on each and verify.
        for topic_name, _, expected_field, expected_value in topics_to_test:

            receiver = TestConfig.endpoints[topic_name].receiver
            messages = receiver.wait_for_delivery(expected_count=1)
            delivered_count = len(messages)
            logger.info('Delivered %d message(s) to %s -> %s', delivered_count, topic_name, messages)

            # .. verify exactly 1 message arrived ..
            self.assertEqual(delivered_count, 1)

            # .. extract and deserialize the data ..
            message = messages[0]
            received_data = message['data']

            if isinstance(received_data, str):
                received_data = json.loads(received_data)

            # .. and confirm the expected field value.
            logger.info('received_data for %s -> %s', topic_name, received_data)
            self.assertEqual(received_data[expected_field], expected_value)

# ################################################################################################################################

    def test_pushed_message_metadata(self) -> 'None':
        """ Verify the pushed message envelope contains data, msg_id, pub_time_iso, topic_name.
        """

        topic_name = 'iam.user.created'
        publish_data:'anydict' = {'user_id': 'meta_test', 'action': 'created'}

        # Publish ..
        _ = self.publisher.publish(topic_name, publish_data)

        # .. wait for push delivery ..
        receiver = TestConfig.endpoints[topic_name].receiver
        messages = receiver.wait_for_delivery(expected_count=1)
        delivered_count = len(messages)
        logger.info('Delivered %d message(s) -> %s', delivered_count, messages)

        # .. verify the envelope fields are present.
        message = messages[0]
        logger.info('Message envelope -> %s', message)

        self.assertIn('data', message)
        self.assertIn('msg_id', message)
        self.assertIn('pub_time_iso', message)
        self.assertIn('topic_name', message)

# ################################################################################################################################

    def test_publish_response_contains_msg_id(self) -> 'None':
        """ Verify the publish REST response contains a msg_id field.
        """

        topic_name = 'iam.user.created'
        publish_data:'anydict' = {'user_id': 'response_test', 'action': 'created'}

        # Publish and check the response.
        response = self.publisher.publish(topic_name, publish_data)
        logger.info('Publish response -> %s', response)

        self.assertIn('msg_id', response)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
