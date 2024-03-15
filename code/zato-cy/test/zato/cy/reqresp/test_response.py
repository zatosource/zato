# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from http.client import OK
from unittest import main as unittest_main

# Zato
from zato.common.api import DATA_FORMAT, ZATO_OK
from zato.common.test import BaseSIOTestCase
from zato.server.service import Service

# Zato - Cython
from zato.cy.reqresp.payload import SimpleIOPayload
from zato.cy.reqresp.response import Response
from zato.simpleio import CySimpleIO

# ################################################################################################################################
# ################################################################################################################################

class MyBaseService(Service):
    class SimpleIO:
        input = 'aaa', 'bbb', 'ccc', '-ddd', '-eee'
        output = 'qqq', 'www', '-eee', '-fff'

# ################################################################################################################################
# ################################################################################################################################

class ResponseTestCase(BaseSIOTestCase):

    def test_defaults(self):
        response = Response()

        self.assertIsNone(response.cid)
        self.assertIsNone(response.content_encoding)
        self.assertEqual(response.content_type, 'text/plain')
        self.assertFalse(response.content_type_changed)
        self.assertIsNone(response.data_format)
        self.assertDictEqual(response.headers, {})
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
        response.init('abc', None, DATA_FORMAT.CSV)

        self.assertEqual(response.cid, 'abc')
        self.assertEqual(response.data_format, DATA_FORMAT.CSV)
        self.assertEqual(response.payload, '')

# ################################################################################################################################

    def test_init_has_sio(self):

        MyService = deepcopy(MyBaseService)
        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        response = Response()
        response.init('abc', MyService._sio, DATA_FORMAT.CSV)

        self.assertIsInstance(response.payload, SimpleIOPayload)

# ################################################################################################################################

    def test_setslice(self):

        MyService = deepcopy(MyBaseService)
        CySimpleIO.attach_sio(None, self.get_server_config(), MyService)

        response = Response()
        response.init('abc', MyService._sio, DATA_FORMAT.CSV)

        data = [{'a':'aa', 'b':'bb'}, {'a':'aa2', 'b':'bb2'}]
        response.payload[:] = data

        for idx, _ignored_elem in enumerate(data):
            self.assertDictEqual(data[idx], response.payload.user_attrs_list[idx])

# ################################################################################################################################

    def test_set_payload_dict_no_sio_case_1b(self):

        response = Response()
        response.init('abc', None, DATA_FORMAT.CSV)

        data = {'a':'aa', 'b':'bb'}
        response.payload = data

        self.assertDictEqual(response.payload, data)

# ################################################################################################################################

    def test_set_payload_direct_payload_case_2a(self):
        # basestring, dict, list, tuple, bool, Number + (EtreeElement, ObjectifiedElement)

        data_01 = b'abc'
        data_02 = u'def'
        data_03 = [1, 2, 3]
        data_04 = (5, 6, 7)
        data_05 = True
        data_06 = False
        data_07 = 1
        data_08 = 2.0

        elems = [data_01, data_02, data_03, data_04, data_05, data_06, data_07, data_08]

        response = Response()
        response.init('abc', None, DATA_FORMAT.CSV)

        for elem in elems:
            response.payload = elem
            self.assertIs(response.payload, elem)

# ################################################################################################################################

    def test_set_payload_not_direct_payload_no_sio_case_2b2(self):

        class MyCustomPayloadType:
            def __repr__(self):
                return '<MyCustomPayloadType>'

        response = Response()
        response.init('abc', None, DATA_FORMAT.CSV)

        try:
            response.payload = MyCustomPayloadType()
        except Exception as e:
            self.assertEqual(e.args[0], 'Cannot serialise value without SimpleIO ouput declaration (<MyCustomPayloadType>)')
        else:
            self.fail('Expected for an exception to be raised')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest_main()

# ################################################################################################################################
# ################################################################################################################################
