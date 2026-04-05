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

class CRLFNormalizationAllCRLFTestCase(TestCase):
    """ Test 15.4 - CRLF normalization: all segment separators are CRLF.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_payloads = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_payloads.append(data)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_crlf_collapses_to_single_cr(self) -> 'None':
        control_id = b'CTRL015004'
        payload = build_adt_a01(control_id=control_id)
        payload = payload.replace(b'\x0d', b'\x0d\x0a')

        response_raw = tcp_send(self.host, self.port, frame(payload))

        self.assertEqual(len(self.received_payloads), 1)
        got = self.received_payloads[0]
        self.assertNotIn(b'\x0a', got)

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], control_id)

# ################################################################################################################################
# ################################################################################################################################
