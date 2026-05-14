# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyPI
import pytest # type: ignore[reportMissingImports]

# local
from base import BasePushTestCase
from config import is_endpoint_active

# ################################################################################################################################
# ################################################################################################################################

_skip_customer_registered = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('customer.registered'),
    reason='customer.registered not in active endpoint set',
)

_skip_customer_updated = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('customer.updated'),
    reason='customer.updated not in active endpoint set',
)

_skip_customer_deactivated = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('customer.deactivated'),
    reason='customer.deactivated not in active endpoint set',
)

_skip_order_placed = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('order.placed'),
    reason='order.placed not in active endpoint set',
)

_skip_order_shipped = pytest.mark.skipif( # type: ignore[reportUntypedFunctionDecorator]
    not is_endpoint_active('order.shipped'),
    reason='order.shipped not in active endpoint set',
)

# ################################################################################################################################
# ################################################################################################################################

class TestCustomerPushDelivery(BasePushTestCase):
    """ Push delivery tests for customer and order domain events.
    """

    @_skip_customer_registered # type: ignore[reportUntypedFunctionDecorator]
    def test_customer_registered_pushed(self) -> 'None':
        """ A message published to customer.registered must be pushed to its HTTP receiver.
        """
        topic_name = 'customer.registered'
        data = {'customer_id': 'cust-001', 'name': 'Jane Smith', 'email': 'jane@example.com'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['customer_id'], 'cust-001')

# ################################################################################################################################

    @_skip_customer_updated # type: ignore[reportUntypedFunctionDecorator]
    def test_customer_updated_pushed(self) -> 'None':
        """ A message published to customer.updated must be pushed to its HTTP receiver.
        """
        topic_name = 'customer.updated'
        data = {'customer_id': 'cust-002', 'field': 'address', 'new_value': '123 Main St'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['customer_id'], 'cust-002')

# ################################################################################################################################

    @_skip_customer_deactivated # type: ignore[reportUntypedFunctionDecorator]
    def test_customer_deactivated_pushed(self) -> 'None':
        """ A message published to customer.deactivated must be pushed to its HTTP receiver.
        """
        topic_name = 'customer.deactivated'
        data = {'customer_id': 'cust-003', 'reason': 'inactivity', 'deactivated_by': 'system'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['customer_id'], 'cust-003')

# ################################################################################################################################

    @_skip_order_placed # type: ignore[reportUntypedFunctionDecorator]
    def test_order_placed_pushed(self) -> 'None':
        """ A message published to order.placed must be pushed to its HTTP receiver.
        """
        topic_name = 'order.placed'
        data = {'order_id': 'ord-001', 'customer_id': 'cust-100', 'total': 299.99}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['order_id'], 'ord-001')

# ################################################################################################################################

    @_skip_order_shipped # type: ignore[reportUntypedFunctionDecorator]
    def test_order_shipped_pushed(self) -> 'None':
        """ A message published to order.shipped must be pushed to its HTTP receiver.
        """
        topic_name = 'order.shipped'
        data = {'order_id': 'ord-002', 'tracking_number': 'TRK-98765', 'carrier': 'express'}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['order_id'], 'ord-002')

# ################################################################################################################################

    @_skip_order_placed # type: ignore[reportUntypedFunctionDecorator]
    def test_burst_of_orders_pushed(self) -> 'None':
        """ Publishing 20 messages to order.placed must deliver all 20 to the HTTP receiver.
        """
        topic_name = 'order.placed'

        for order_index in range(20):
            order_id = f'burst-ord-{order_index:03d}'
            data = {'order_id': order_id, 'item_count': order_index + 1}
            result = self.publish(topic_name, data)
            self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=20, timeout=60)

        message_count = len(messages)
        self.assertEqual(message_count, 20)

# ################################################################################################################################

    @_skip_order_placed # type: ignore[reportUntypedFunctionDecorator]
    def test_burst_ordering_preserved(self) -> 'None':
        """ Publishing 10 messages with sequential indices must deliver them
        in the same order they were published.
        """
        topic_name = 'order.placed'

        for message_index in range(10):
            data = {'order_id': f'seq-{message_index:03d}', 'sequence': message_index}
            result = self.publish(topic_name, data)
            self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=10, timeout=30)

        message_count = len(messages)
        self.assertEqual(message_count, 10)

        # Extract the sequence index from each delivered message and verify
        # they arrive in monotonically increasing order ..
        delivered_indices = []

        for message in messages:
            received_data = self.extract_push_data(message)
            delivered_indices.append(received_data['sequence'])

        index_count = len(delivered_indices)

        for position in range(1, index_count):
            previous = delivered_indices[position - 1]
            current = delivered_indices[position]
            self.assertLess(previous, current, f'Out-of-order delivery at position {position}')

# ################################################################################################################################

    @_skip_customer_registered # type: ignore[reportUntypedFunctionDecorator]
    def test_large_customer_payload_pushed(self) -> 'None':
        """ A 100 KB JSON payload published to customer.registered must be delivered in full.
        """
        topic_name = 'customer.registered'

        large_field = 'x' * 100_000
        data = {'customer_id': 'cust-large-001', 'profile_data': large_field}

        result = self.publish(topic_name, data)
        self.assertTrue(result['is_ok'])

        messages = self.poll_for_messages(topic_name, expected_count=1, timeout=30)

        message_count = len(messages)
        self.assertEqual(message_count, 1)

        received_data = self.extract_push_data(messages[0])
        self.assertEqual(received_data['customer_id'], 'cust-large-001')
        self.assertEqual(len(received_data['profile_data']), 100_000)

# ################################################################################################################################
# ################################################################################################################################
