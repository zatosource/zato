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

class LFNormalizationMixedCRLFTestCase(TestCase):
    """ Test 15.2 - LF normalization: mixed CR and LF segment separators.
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

    def test_mixed_separators_become_all_cr(self) -> 'None':
        payload = build_adt_a01(control_id=b'CTRL015002')
        parts = payload.rstrip(b'\x0d').split(b'\x0d')
        out = parts[0]
        for i in range(len(parts) - 1):
            sep = b'\x0d' if i % 2 == 0 else b'\x0a'
            out = out + sep + parts[i + 1]
        out = out + b'\x0d'

        tcp_send(self.host, self.port, frame(out))

        self.assertEqual(len(self.received_payloads), 1)
        got = self.received_payloads[0]
        self.assertNotIn(b'\x0a', got)

# ################################################################################################################################
# ################################################################################################################################
