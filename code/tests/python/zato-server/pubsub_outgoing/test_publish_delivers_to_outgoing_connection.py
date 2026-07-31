# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
import unittest
from json import loads

# Zato
from zato.common.test.config_pubsub_outgoing import TestConfig

# local
from _helpers import get_client, publish, publish_through_facade

# ################################################################################################################################
# ################################################################################################################################

# How long to keep watching after the expected messages arrived, to see whether any more of them do.
_quiet_period_seconds = 5

# ################################################################################################################################
# ################################################################################################################################

class PublishDeliversToOutgoingConnectionTestCase(unittest.TestCase):
    """ What a service publishes to an outgoing connection reaches that connection.
    """

    @classmethod
    def setUpClass(class_) -> 'None': # pyright: ignore[reportSelfClsParameterName]
        class_.client = get_client()

# ################################################################################################################################

    def test_publish_reaches_the_connection(self) -> 'None':

        payload = {'order_id': 'order-1234', 'customer': 'Maria Kowalska'}

        _ = publish(self.client, TestConfig.orders_connection, payload)

        receiver = TestConfig.orders_receiver
        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        request = requests[0]

        self.assertEqual(request.method, 'POST')
        self.assertEqual(request.path, '/api/orders')
        self.assertEqual(loads(request.body), payload)

# ################################################################################################################################

    def test_publish_returns_the_id_of_the_queued_message(self) -> 'None':

        payload = {'order_id': 'order-2345', 'customer': 'Maria Kowalska'}

        msg_id = publish(self.client, TestConfig.orders_connection, payload)

        self.assertTrue(msg_id, msg_id)

        receiver = TestConfig.orders_receiver
        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

# ################################################################################################################################

    def test_publish_through_the_facade_reaches_the_same_connection(self) -> 'None':
        """ self.rest['Name'].publish and self.out.rest['Name'].publish are the same publication.
        """
        payload = {'order_id': 'order-3456', 'customer': 'Maria Kowalska'}

        _ = publish_through_facade(self.client, TestConfig.orders_connection, payload)

        receiver = TestConfig.orders_receiver
        requests = receiver.wait_for_requests(1)

        self.assertEqual(len(requests), 1, requests)

        request = requests[0]

        self.assertEqual(request.path, '/api/orders')
        self.assertEqual(loads(request.body), payload)

# ################################################################################################################################

    def test_every_message_arrives_once(self) -> 'None':

        expected = []

        for index in range(3):
            payload = {'order_id': f'order-{index}', 'customer': 'Maria Kowalska'}
            expected.append(payload)
            _ = publish(self.client, TestConfig.orders_connection, payload)

        receiver = TestConfig.orders_receiver
        requests = receiver.wait_for_requests(3)

        self.assertEqual(len(requests), 3, requests)

        received = []

        for request in requests:
            received.append(loads(request.body))

        self.assertEqual(received, expected)

        # .. nothing arrives twice, so the count stands after everything has had time to be repeated.
        time.sleep(_quiet_period_seconds)

        self.assertEqual(len(receiver.requests), 3, receiver.requests)

# ################################################################################################################################

    def test_publishing_to_one_connection_leaves_the_other_alone(self) -> 'None':

        payload = {'order_id': 'order-4567', 'customer': 'Maria Kowalska'}

        _ = publish(self.client, TestConfig.orders_connection, payload)

        orders_receiver = TestConfig.orders_receiver
        _ = orders_receiver.wait_for_requests(1)

        inventory_receiver = TestConfig.inventory_receiver

        self.assertEqual(inventory_receiver.requests, [], inventory_receiver.requests)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
