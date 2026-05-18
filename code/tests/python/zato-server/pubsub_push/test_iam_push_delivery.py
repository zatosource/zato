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

    def test_publish_to_iam_user_created(self) -> 'None':
        """ Publish to iam.user.created, verify receiver got 1 message with correct data.
        """

        topic_name = 'iam.user.created'
        publish_data:'anydict' = {'user_id': 'u001', 'action': 'created'}

        # Publish ..
        _ = self.publisher.publish(topic_name, publish_data)

        # .. wait for push delivery ..
        receiver = TestConfig.endpoints[topic_name].receiver
        messages = receiver.wait_for_delivery(expected_count=1)
        logger.info('Delivered messages -> %s', messages)

        # .. verify exactly 1 message arrived ..
        self.assertEqual(len(messages), 1)

        # .. and the data round-tripped correctly.
        message = messages[0]
        received_data = message['data']

        if isinstance(received_data, str):
            received_data = json.loads(received_data)

        self.assertEqual(received_data['user_id'], 'u001')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
