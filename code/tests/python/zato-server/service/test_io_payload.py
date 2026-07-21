# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.util.message import Message
from zato.server.reqresp.payload import IOPayload

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'test-cid-0001'

# ################################################################################################################################
# ################################################################################################################################

class TestIOPayloadDeclaredOutput(unittest.TestCase):
    """ A payload built from a string-based output declaration - declared names
    are the only ones that may be read or written.
    """

    def _make_payload(self, *output_names:'str') -> 'IOPayload':
        io_processor = MagicMock()
        io_processor.service_class = 'test.module.OrderDetails'

        out = IOPayload(io_processor, list(output_names), _test_cid, 'json')
        return out

# ################################################################################################################################

    def test_declared_name_accepts_a_scalar(self) -> 'None':
        payload = self._make_payload('customer_id', 'status')
        payload.customer_id = 'C-1001'
        payload.status = 'confirmed'

        self.assertEqual(payload.getvalue(), {'customer_id': 'C-1001', 'status': 'confirmed'})

# ################################################################################################################################

    def test_declared_name_vivifies_a_message_subtree(self) -> 'None':
        payload = self._make_payload('abc')
        payload.abc.hello = 123

        self.assertEqual(payload.getvalue(), {'abc': {'hello': 123}})

# ################################################################################################################################

    def test_subtree_nests_to_any_depth(self) -> 'None':
        payload = self._make_payload('abc')
        payload.abc.hello.world = 123
        payload.abc.status = 'confirmed'

        self.assertEqual(payload.getvalue(), {'abc': {'hello': {'world': 123}, 'status': 'confirmed'}})

# ################################################################################################################################

    def test_vivified_subtree_is_the_same_object_across_reads(self) -> 'None':
        payload = self._make_payload('abc')

        first = payload.abc
        second = payload.abc

        self.assertIsInstance(first, Message)
        self.assertIs(first, second)

# ################################################################################################################################

    def test_read_only_subtree_is_pruned_from_getvalue(self) -> 'None':
        payload = self._make_payload('abc', 'status')
        _ = payload.abc
        payload.status = 'confirmed'

        self.assertEqual(payload.getvalue(), {'status': 'confirmed'})

# ################################################################################################################################

    def test_undeclared_read_raises_naming_the_declared_list(self) -> 'None':
        payload = self._make_payload('customer_id', 'status')

        with self.assertRaises(KeyError) as raised:
            _ = payload.customer_name

        message = str(raised.exception)
        self.assertIn('customer_name', message)
        self.assertIn('customer_id', message)
        self.assertIn('status', message)

# ################################################################################################################################

    def test_undeclared_write_raises_naming_the_declared_list(self) -> 'None':
        payload = self._make_payload('customer_id', 'status')

        with self.assertRaises(KeyError) as raised:
            payload.customer_name = 'Test Customer'

        message = str(raised.exception)
        self.assertIn('customer_name', message)
        self.assertIn('customer_id', message)
        self.assertIn('status', message)

# ################################################################################################################################

    def test_undeclared_item_write_raises(self) -> 'None':
        payload = self._make_payload('customer_id')

        with self.assertRaises(KeyError):
            payload['customer_name'] = 'Test Customer'

# ################################################################################################################################

    def test_declared_item_write_is_accepted(self) -> 'None':
        payload = self._make_payload('customer_id')
        payload['customer_id'] = 'C-1001'

        self.assertEqual(payload.getvalue(), {'customer_id': 'C-1001'})

# ################################################################################################################################

    def test_set_payload_attrs_keeps_declared_names_only(self) -> 'None':
        payload = self._make_payload('customer_id', 'status')
        payload.set_payload_attrs({'customer_id': 'C-1001', 'status': 'confirmed', 'internal_note': 'not for the wire'})

        self.assertEqual(payload.getvalue(), {'customer_id': 'C-1001', 'status': 'confirmed'})

# ################################################################################################################################

    def test_repeated_output_through_slice_assignment(self) -> 'None':
        payload = self._make_payload('customer_id')
        payload[:] = [{'customer_id': 'C-1001'}, {'customer_id': 'C-1002'}]

        self.assertEqual(payload.getvalue(), [{'customer_id': 'C-1001'}, {'customer_id': 'C-1002'}])

# ################################################################################################################################

    def test_repeated_output_through_append(self) -> 'None':
        payload = self._make_payload('customer_id')
        payload.append({'customer_id': 'C-1001'})
        payload.append({'customer_id': 'C-1002'})

        self.assertEqual(payload.getvalue(), [{'customer_id': 'C-1001'}, {'customer_id': 'C-1002'}])

# ################################################################################################################################

    def test_getvalue_mixes_scalars_and_subtrees(self) -> 'None':
        payload = self._make_payload('customer_id', 'details')
        payload.customer_id = 'C-1001'
        payload.details.city = 'Amsterdam'
        payload.details.country = 'Netherlands'

        expected = {'customer_id': 'C-1001', 'details': {'city': 'Amsterdam', 'country': 'Netherlands'}}
        self.assertEqual(payload.getvalue(), expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
