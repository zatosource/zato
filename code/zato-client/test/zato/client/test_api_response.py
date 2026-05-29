# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from unittest import TestCase
from unittest.mock import MagicMock

# Zato
from zato.client import _APIResponse

# ################################################################################################################################
# ################################################################################################################################

class TestAPIResponsePaginationMeta(TestCase):

    def _make_inner(self, status_code, text, headers):
        inner = MagicMock()
        inner.status_code = status_code
        inner.text = text
        inner.headers = headers
        return inner

    def test_meta_populated_from_pagination_headers(self):
        """ Verify that self.meta is populated from X-Zato-Page-* response headers.
        """
        headers = {
            'X-Zato-Page-Current': '3',
            'X-Zato-Page-Size': '25',
            'X-Zato-Page-Total': '10',
            'X-Zato-Page-Previous': '2',
            'X-Zato-Page-Next': '4',
            'X-Zato-Page-Has-Previous': 'True',
            'X-Zato-Page-Has-Next': 'True',
            'X-Zato-Result-Total': '245',
            'x-zato-cid': 'abc123',
        }

        inner = self._make_inner(OK, '[]', headers)
        response = _APIResponse(inner)

        self.assertEqual(response.meta['cur_page'], '3')
        self.assertEqual(response.meta['page_size'], '25')
        self.assertEqual(response.meta['num_pages'], '10')
        self.assertEqual(response.meta['prev_page'], '2')
        self.assertEqual(response.meta['next_page'], '4')
        self.assertEqual(response.meta['has_prev_page'], 'True')
        self.assertEqual(response.meta['has_next_page'], 'True')
        self.assertEqual(response.meta['total'], '245')

    def test_meta_empty_when_no_pagination_headers(self):
        """ Verify that self.meta is empty when no pagination headers are present.
        """
        headers = {
            'x-zato-cid': 'abc123',
            'Content-Type': 'application/json',
        }

        inner = self._make_inner(OK, '[]', headers)
        response = _APIResponse(inner)

        self.assertEqual(response.meta, {})

    def test_data_is_bare_list(self):
        """ Verify that response.data is the bare list from the body.
        """
        headers = {
            'X-Zato-Page-Current': '1',
            'X-Zato-Page-Total': '1',
            'x-zato-cid': 'abc123',
        }

        inner = self._make_inner(OK, '[{"id": 1, "name": "test"}]', headers)
        response = _APIResponse(inner)

        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'test')

# ################################################################################################################################
# ################################################################################################################################
