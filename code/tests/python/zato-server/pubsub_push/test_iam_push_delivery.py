# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
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

_delivery_poll_timeout  = 10
_delivery_poll_interval = 0.5

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

    def _wait_for_delivery(self, topic_name:'str', expected_count:'int'=1) -> 'list[anydict]':
        """ Waits until the webhook receiver has received the expected number of messages.
        """
        endpoint_config = TestConfig.endpoints[topic_name]
        receiver = endpoint_config.receiver
        start_time = time.monotonic()
        deadline = start_time + _delivery_poll_timeout

        while time.monotonic() < deadline:
            count = receiver.delivered_count()
            if count >= expected_count:
                messages = receiver.get_delivered_messages()
                logger.info('_wait_for_delivery -> topic:%s, count:%d', topic_name, len(messages))
                return messages

            time.sleep(_delivery_poll_interval)

        messages = receiver.get_delivered_messages()
        logger.info('_wait_for_delivery timeout -> topic:%s, count:%d', topic_name, len(messages))
        return messages

# ################################################################################################################################

    def test_publish_to_iam_user_created(self) -> 'None':
        """ Publish to iam.user.created, verify receiver got 1 message with correct data.
        """

        topic_name = 'iam.user.created'
        publish_data:'anydict' = {'user_id': 'u001', 'action': 'created'}

        # Publish ..
        _ = self.publisher.publish(topic_name, publish_data)

        # .. wait for push delivery ..
        messages = self._wait_for_delivery(topic_name)
        logger.info('Delivered messages -> %s', messages)

        # .. verify exactly 1 message arrived ..
        self.assertEqual(len(messages), 1)

        # .. and the data round-tripped correctly.
        message = messages[0]
        received_data = message['data']
        self.assertEqual(received_data['user_id'], 'u001')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
