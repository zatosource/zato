# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Test helpers
from conftest import (
    build_adt_a01,
    frame,
    ini_path_from_test_file,
    start_server,
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class CallbackReturnsCustomTestCase(TestCase):
    """ Test 4.3 - callback returns custom response bytes.
    The server must forward these bytes as-is (framed in MLLP).
    """

    custom_response = b'MSH|^~\\&|ZatoApp|ZatoFac|TestApp|TestFac|20240101120000||ACK|CUSTOM_ACK|P|2.5\x0dMSA|AA|CUSTOM_001\x0d'

    @classmethod
    def setUpClass(cls) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'bytes':
            return cls.custom_response

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_custom_response_forwarded(self) -> 'None':

        payload = build_adt_a01(control_id=b'CUSTOM_001')
        response_raw = tcp_send(self.host, self.port, frame(payload))

        response_payload = unframe(response_raw)
        self.assertEqual(response_payload, self.custom_response)

# ################################################################################################################################
# ################################################################################################################################
