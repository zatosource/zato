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
)

# ################################################################################################################################
# ################################################################################################################################

class CRLFAndLFBothEnabledTestCase(TestCase):
    """ Test 15.5 - CRLF and LF normalization both enabled: mixed input becomes all CR.
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

    def test_mixed_crlf_and_lf_become_all_cr(self) -> 'None':
        base = build_adt_a01(control_id=b'CTRL015005')
        parts = base.rstrip(b'\x0d').split(b'\x0d')
        payload = parts[0] + b'\x0d\x0a' + parts[1] + b'\x0a' + parts[2] + b'\x0d\x0a' + parts[3] + b'\x0d'

        tcp_send(self.host, self.port, frame(payload))

        self.assertEqual(len(self.received_payloads), 1)
        got = self.received_payloads[0]
        self.assertNotIn(b'\x0a', got)

# ################################################################################################################################
# ################################################################################################################################
