# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Test helpers
from conftest import (
    frame,
    ini_path_from_test_file,
    start_server,
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class CallbackReturnsStringTestCase(TestCase):
    """ Test 4.5 - callback returns a string (not bytes).
    The server must encode it using the detected encoding and forward it.
    """

    string_response = 'MSH|^~\\&|ZatoApp|ZatoFac|TestApp|TestFac|20240101120000||ACK|STR_ACK|P|2.5\rMSA|AA|STR_001\r'

    @classmethod
    def setUpClass(cls) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'str':
            return cls.string_response

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_string_response_encoded(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        # Use ISO-8859-1 as encoding so we can verify encoding path ..
        msh = sep.join([
            b'MSH', b'^~\\&',
            b'TestApp', b'TestFac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', b'STR_001',
            b'P', b'2.5',
            b'', b'', b'', b'', b'',
            b'8859/1',
        ])
        pid = sep.join([b'PID', b'', b'', b'44444^^^Hosp^PI', b'', b'Doe^Jane', b'', b'19900101', b'F'])
        payload = cr.join([msh, pid]) + cr

        response_raw = tcp_send(self.host, self.port, frame(payload))
        response_payload = unframe(response_raw)

        # The server encodes the string with the detected encoding (iso-8859-1) ..
        expected = self.string_response.encode('iso-8859-1')
        self.assertEqual(response_payload, expected)

# ################################################################################################################################
# ################################################################################################################################
