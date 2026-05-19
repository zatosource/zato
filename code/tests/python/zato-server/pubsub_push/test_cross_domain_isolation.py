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

logger = logging.getLogger('zato.test.pubsub_push.cross_domain_isolation')

# ################################################################################################################################
# ################################################################################################################################

class TestCrossDomainIsolation(unittest.TestCase):
    """ Tests for cross-domain isolation - messages go only to their subscribed endpoints.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(
            TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

# ################################################################################################################################

    def test_publish_to_topic_a_delivers_nothing_to_endpoint_b(self) -> 'None':
        """ Publish a message to one topic, wait generously, verify that a different
        topic's receiver got zero deliveries.
        """

        source_topic = 'iam.user.created'
        unrelated_topic = 'order.shipped'

        source_receiver = TestConfig.endpoints[source_topic].receiver
        unrelated_receiver = TestConfig.endpoints[unrelated_topic].receiver

        # Publish a message to the source topic ..
        publish_data:'anydict' = {'user_id': 'isolation_test', 'source': 'test_cross_domain'}
        _ = self.publisher.publish(source_topic, publish_data)
        logger.info('Published to %s', source_topic)

        # .. wait for the source receiver to get its message ..
        delivery_timeout = 30.0
        source_messages = source_receiver.wait_for_delivery(expected_count=1, timeout=delivery_timeout)
        source_count = len(source_messages)
        logger.info('Source receiver (%s) delivered %d message(s) -> %s', source_topic, source_count, source_messages)

        # .. verify the source got it ..
        self.assertEqual(source_count, 1)

        # .. now wait generously and check the unrelated receiver ..
        isolation_wait = 10.0
        time.sleep(isolation_wait)

        unrelated_messages = unrelated_receiver.get_delivered_messages()
        unrelated_count = len(unrelated_messages)
        logger.info('Unrelated receiver (%s) delivered %d message(s) -> %s', unrelated_topic, unrelated_count, unrelated_messages)

        # .. verify the unrelated endpoint got nothing.
        self.assertEqual(unrelated_count, 0)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
