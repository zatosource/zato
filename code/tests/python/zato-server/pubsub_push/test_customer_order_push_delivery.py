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

logger = logging.getLogger('zato.test.pubsub_push.customer_order_push_delivery')

# ################################################################################################################################
# ################################################################################################################################

class TestCustomerOrderPushDelivery(unittest.TestCase):
    """ Tests for push delivery to customer and order topic webhook receivers.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.publisher = PublishClient(
            TestConfig.base_url, TestConfig.publisher_username, TestConfig.publisher_password)

# ################################################################################################################################

    def test_publish_to_all_customer_order_topics(self) -> 'None':
        """ Publish to all 5 customer/order topics, verify each receiver got exactly 1 message
        and the data round-tripped correctly.
        """

        # Define each topic with its payload and the field to verify ..
        topics_to_test:'list[tuple[str, anydict, str, str]]' = [
            ('customer.registered',  {'customer_id': 'cust1', 'email': 'cust1@example.com'}, 'customer_id', 'cust1'),
            ('customer.updated',     {'customer_id': 'cust2', 'field': 'address'},           'customer_id', 'cust2'),
            ('customer.deactivated', {'customer_id': 'cust3', 'reason': 'inactive'},         'reason',      'inactive'),
            ('order.placed',         {'order_id': 'ord1', 'total': '99.99'},                 'order_id',    'ord1'),
            ('order.shipped',        {'order_id': 'ord2', 'carrier': 'dhl'},                 'carrier',     'dhl'),
        ]

        # Publish to all 5 topics ..
        for topic_name, publish_data, _, _ in topics_to_test:
            _ = self.publisher.publish(topic_name, publish_data)
            logger.info('Published to %s -> %s', topic_name, publish_data)

        # .. wait for delivery on each and verify.
        for topic_name, _, expected_field, expected_value in topics_to_test:

            receiver = TestConfig.endpoints[topic_name].receiver
            messages = receiver.wait_for_delivery(expected_count=1)
            logger.info('Delivered to %s -> %s', topic_name, messages)

            # .. verify exactly 1 message arrived ..
            self.assertEqual(len(messages), 1)

            # .. extract and deserialize the data ..
            message = messages[0]
            received_data = message['data']

            if isinstance(received_data, str):
                received_data = json.loads(received_data)

            # .. and confirm the expected field value.
            logger.info('received_data for %s -> %s', topic_name, received_data)
            self.assertEqual(received_data[expected_field], expected_value)

# ################################################################################################################################

    def test_burst_twenty_messages(self) -> 'None':
        """ Publish a burst of messages to one topic, verify all arrive at the receiver.
        """

        topic_name = 'customer.registered'
        receiver = TestConfig.endpoints[topic_name].receiver
        burst_count = 20

        # Publish all messages ..
        for idx in range(burst_count):
            publish_data:'anydict' = {'customer_id': f'burst_{idx}', 'sequence': idx}
            _ = self.publisher.publish(topic_name, publish_data)

        logger.info('Published %d messages to %s', burst_count, topic_name)

        # .. wait for all to be delivered ..
        messages = receiver.wait_for_delivery(expected_count=burst_count)
        logger.info('Delivered %s messages to %s', messages, topic_name)

        # .. and verify the count.
        self.assertEqual(len(messages), burst_count)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
