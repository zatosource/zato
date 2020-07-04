# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import OK

# Zato
from zato.common import ZATO_OK

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase
from zato.cy.reqresp.response import Response

# ################################################################################################################################
# ################################################################################################################################

class ResponseTestCase(BaseTestCase):

    def test_defaults(self):
        response = Response()

        self.assertIsNone(response.cid)
        self.assertIsNone(response.content_encoding)
        self.assertEqual(response.content_type, 'text/plain')
        self.assertFalse(response.content_type_changed)
        self.assertIsNone(response.data_format)
        self.assertIsNone(response.headers)
        self.assertEqual(response.payload, '')
        self.assertEqual(response.result, ZATO_OK)
        self.assertEqual(response.result_details, '')
        self.assertEqual(response.status_code, OK)
        self.assertEqual(response.status_message, 'OK')

# ################################################################################################################################
# ################################################################################################################################
