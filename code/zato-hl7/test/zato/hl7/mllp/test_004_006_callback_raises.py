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
    parse_ack,
    start_server,
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class CallbackRaisesTestCase(TestCase):
    """ Test 4.6 - callback raises an exception.
    The server must return an AE (Application Error) NAK and keep the connection alive.
    """

    @classmethod
    def setUpClass(cls) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            raise ValueError('Simulated callback failure')

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_exception_produces_ae_nak(self) -> 'None':

        payload = build_adt_a01(control_id=b'ERR_001')
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AE')
        self.assertEqual(ack['control_id'], b'ERR_001')

        # ERR segment should contain an error description ..
        self.assertIn(b'Callback error', ack['err_text'])

# ################################################################################################################################
# ################################################################################################################################
