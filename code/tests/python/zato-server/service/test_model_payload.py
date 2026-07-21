# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from dataclasses import dataclass
from unittest.mock import MagicMock

# Zato
from zato.common.marshal_.api import Model
from zato.common.marshal_.io import DataClassIO
from zato.common.typing_ import optional
from zato.server.reqresp.response import Response
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'test-cid-0001'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Address(Model):
    city: str
    country: str

# ################################################################################################################################

@dataclass(init=False)
class OrderDetails(Model):
    customer_id: str
    status: str
    address: Address
    backup_address: 'optional[Address]' = None

# ################################################################################################################################
# ################################################################################################################################

class TestModelVivification(unittest.TestCase):
    """ Dot access on model instances - nested model fields vivify, scalars and typos raise.
    """

    def test_nested_model_field_vivifies_an_instance(self) -> 'None':
        order = OrderDetails.__new__(OrderDetails)
        order.address.city = 'Amsterdam'

        self.assertIsInstance(order.address, Address)
        self.assertEqual(order.address.city, 'Amsterdam')

# ################################################################################################################################

    def test_vivified_instance_is_the_same_object_across_reads(self) -> 'None':
        order = OrderDetails.__new__(OrderDetails)

        first = order.address
        second = order.address

        self.assertIs(first, second)

# ################################################################################################################################

    def test_unset_scalar_field_raises_naming_the_type(self) -> 'None':
        order = OrderDetails.__new__(OrderDetails)

        with self.assertRaises(AttributeError) as raised:
            _ = order.customer_id

        message = str(raised.exception)
        self.assertIn('customer_id', message)
        self.assertIn('OrderDetails', message)
        self.assertIn('not a nested model', message)

# ################################################################################################################################

    def test_undeclared_read_raises_listing_the_fields(self) -> 'None':
        order = OrderDetails.__new__(OrderDetails)

        with self.assertRaises(AttributeError) as raised:
            _ = order.customer_name

        message = str(raised.exception)
        self.assertIn('customer_name', message)
        self.assertIn('customer_id', message)
        self.assertIn('status', message)

# ################################################################################################################################

    def test_undeclared_write_raises_listing_the_fields(self) -> 'None':
        order = OrderDetails.__new__(OrderDetails)

        with self.assertRaises(AttributeError) as raised:
            order.customer_name = 'Test Customer'

        message = str(raised.exception)
        self.assertIn('customer_name', message)
        self.assertIn('customer_id', message)
        self.assertIn('status', message)

# ################################################################################################################################

    def test_declared_write_is_accepted(self) -> 'None':
        order = OrderDetails.__new__(OrderDetails)
        order.customer_id = 'C-1001'

        self.assertEqual(order.customer_id, 'C-1001')

# ################################################################################################################################

    def test_field_with_a_default_resolves_through_normal_lookup(self) -> 'None':
        order = OrderDetails.__new__(OrderDetails)

        self.assertIsNone(order.backup_address)

# ################################################################################################################################

    def test_to_dict_includes_the_vivified_subtree(self) -> 'None':
        order = OrderDetails.__new__(OrderDetails)
        order.customer_id = 'C-1001'
        order.status = 'confirmed'
        order.address.city = 'Amsterdam'
        order.address.country = 'Netherlands'

        expected = {
            'customer_id': 'C-1001',
            'status': 'confirmed',
            'address': {'city': 'Amsterdam', 'country': 'Netherlands'},
            'backup_address': None,
        }
        self.assertEqual(order.to_dict(), expected)

# ################################################################################################################################
# ################################################################################################################################

class TestResponseModelPayload(unittest.TestCase):
    """ A dataclass output declaration makes the payload getter vivify a model instance on first access.
    """

    def _make_response(self, output_model_class:'type') -> 'Response':

        class IODeclaration:
            output = output_model_class

        io = DataClassIO(MagicMock(), IODeclaration)

        out = Response()
        out.init(_test_cid, io, 'json', output_model_class)
        return out

# ################################################################################################################################

    def test_first_access_vivifies_the_output_model(self) -> 'None':
        response = self._make_response(OrderDetails)

        self.assertIsInstance(response.payload, OrderDetails)

# ################################################################################################################################

    def test_vivified_payload_is_the_same_object_across_reads(self) -> 'None':
        response = self._make_response(OrderDetails)

        first = response.payload
        second = response.payload

        self.assertIs(first, second)

# ################################################################################################################################

    def test_nested_assignment_through_the_payload(self) -> 'None':
        response = self._make_response(OrderDetails)
        response.payload.customer_id = 'C-1001'
        response.payload.address.city = 'Amsterdam'

        self.assertEqual(response.payload.customer_id, 'C-1001')
        self.assertEqual(response.payload.address.city, 'Amsterdam')

# ################################################################################################################################

    def test_whole_instance_assignment_replaces_the_payload(self) -> 'None':
        response = self._make_response(OrderDetails)

        order = OrderDetails.__new__(OrderDetails)
        order.customer_id = 'C-1001'
        order.status = 'confirmed'
        order.address.city = 'Amsterdam'
        order.address.country = 'Netherlands'

        # With the JSON data format an assigned model is stored as its dict form.
        response.payload = order

        self.assertEqual(response.payload, order.to_dict())

# ################################################################################################################################

    def test_assignment_turns_vivification_off(self) -> 'None':
        response = self._make_response(OrderDetails)
        response.payload = ''

        self.assertEqual(response.payload, '')

# ################################################################################################################################
# ################################################################################################################################

class TestSetResponseDataWithModels(unittest.TestCase):
    """ The generic serialization funnel - vivified-but-empty models normalize to an empty string.
    """

    def _make_service(self, output_model_class:'type') -> 'Service':

        class IODeclaration:
            output = output_model_class

        io = DataClassIO(MagicMock(), IODeclaration)

        out = Service.__new__(Service)
        out.response = Response()
        out.response.init(_test_cid, io, 'json', output_model_class)
        return out

# ################################################################################################################################

    def test_untouched_payload_serializes_to_an_empty_string(self) -> 'None':
        service = self._make_service(OrderDetails)

        result = service.set_response_data(service, data_format='json', transport='')

        self.assertEqual(result, '')
        self.assertEqual(service.response.payload, '')

# ################################################################################################################################

    def test_vivified_but_unpopulated_payload_serializes_to_an_empty_string(self) -> 'None':
        service = self._make_service(OrderDetails)

        # This read vivifies the model without giving it any content.
        _ = service.response.payload

        result = service.set_response_data(service, data_format='json', transport='')

        self.assertEqual(result, '')
        self.assertEqual(service.response.payload, '')

# ################################################################################################################################

    def test_populated_payload_stays_a_model(self) -> 'None':
        service = self._make_service(OrderDetails)
        service.response.payload.customer_id = 'C-1001'

        result = service.set_response_data(service, data_format='json', transport='')

        self.assertIsInstance(result, OrderDetails)
        self.assertEqual(result.customer_id, 'C-1001')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
