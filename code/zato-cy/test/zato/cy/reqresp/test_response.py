# -*- coding: utf-8 -*-

"""
Copyright (C) 2020, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from http.client import OK

# Zato
from zato.common import DATA_FORMAT, ZATO_OK
from zato.server.service import Service

# Zato - Cython
from test.zato.cy.simpleio_ import BaseTestCase
from zato.cy.reqresp.payload import SimpleIOPayload
from zato.cy.reqresp.response import Response
from zato.simpleio import CySimpleIO

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

    def test_len(self):
        response = Response()
        response._payload = 'abcdef'

        self.assertEqual(len(response), 6)

# ################################################################################################################################

    def test_content_type(self):
        response = Response()
        response.content_type = 'abc'

        self.assertTrue(response.content_type_changed)
        self.assertEqual(response.content_type, 'abc')

# ################################################################################################################################

    def test_init_no_sio(self):
        response = Response()
        response.init('abc', DATA_FORMAT.CSV)

        self.assertEqual(response.cid, 'abc')
        self.assertEqual(response.data_format, DATA_FORMAT.CSV)
        self.assertEqual(response.payload, '')

# ################################################################################################################################

    def test_init_with_sio(self):

        class MyService(Service):
            class SimpleIO:
                input = 'aaa', 'bbb', 'ccc', '-ddd', '-eee'
                output = 'qqq', 'www', '-eee', '-fff'

        CySimpleIO.attach_sio(self.get_server_config(), MyService)

        response = Response()
        response.sio_config = MyService._sio.definition
        response.init('abc', DATA_FORMAT.CSV)

        self.assertIsInstance(response.payload, SimpleIOPayload)

# ################################################################################################################################
# ################################################################################################################################
