# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase
from unittest.mock import MagicMock

# Zato
from zato.server.reqresp.payload import IOPayload

# ################################################################################################################################
# ################################################################################################################################

class TestIOPayloadGetValue(TestCase):

    def test_getvalue_returns_bare_list(self):
        """ Verify that getvalue() returns a plain list without any _meta wrapping.
        """
        io = MagicMock()
        payload = IOPayload(io, ['name', 'id'], 'test-cid', 'json')

        payload.append({'name': 'item1', 'id': 1})
        payload.append({'name': 'item2', 'id': 2})

        result = payload.getvalue()

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'item1')
        self.assertEqual(result[1]['name'], 'item2')

    def test_getvalue_returns_bare_dict(self):
        """ Verify that getvalue() returns a plain dict for non-repeated output.
        """
        io = MagicMock()
        payload = IOPayload(io, ['name', 'id'], 'test-cid', 'json')

        # .. set a dict-style attribute ..
        object.__setattr__(payload, 'user_attrs_dict', {'name': 'test', 'id': 42})

        result = payload.getvalue()

        self.assertIsInstance(result, dict)
        self.assertEqual(result['name'], 'test')
        self.assertEqual(result['id'], 42)
        self.assertNotIn('_meta', result)
        self.assertNotIn('response', result)

# ################################################################################################################################
# ################################################################################################################################
