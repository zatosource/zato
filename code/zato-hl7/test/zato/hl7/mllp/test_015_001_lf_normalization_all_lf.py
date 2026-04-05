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

class LFNormalizationAllLFTestCase(TestCase):
    """ Test 15.1 - LF normalization: message with LF segment separators.
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

    def test_lf_separators_normalized_to_cr(self) -> 'None':
        control_id = b'CTRL015001'
        payload = build_adt_a01(control_id=control_id)
        payload = payload.replace(b'\x0d', b'\x0a')

        response_raw = tcp_send(self.host, self.port, frame(payload))

        self.assertEqual(len(self.received_payloads), 1)
        got = self.received_payloads[0]
        self.assertNotIn(b'\x0a', got)
        self.assertGreater(got.count(b'\x0d'), 0)

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], control_id)

# ################################################################################################################################
# ################################################################################################################################
