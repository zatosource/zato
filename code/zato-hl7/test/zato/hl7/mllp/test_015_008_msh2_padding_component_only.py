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
)

# ################################################################################################################################
# ################################################################################################################################

class MSH2PaddingComponentOnlyTestCase(TestCase):
    """ Test 15.8 - MSH-2 padding: only component separator (^).
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

    def test_single_char_msh2_padded_to_standard(self) -> 'None':
        payload = (
            b'MSH|^|SendApp|SendFac|RecvApp|RecvFac|20240101120000||ADT^A01|CTRL008|P|2.5\x0d'
            b'EVN||20240101120000\x0d'
            b'PID|||12345^^^Hospital^PI||DOE^JOHN||19800101|M\x0d'
        )
        expected_msh2 = b'^~\\&'

        tcp_send(self.host, self.port, frame(payload))

        self.assertEqual(len(self.received_payloads), 1)
        got = self.received_payloads[0]
        cr_idx = got.find(b'\x0d')
        msh_segment = got[:cr_idx]
        field_sep = msh_segment[3:4]
        fields = msh_segment.split(field_sep)
        self.assertEqual(fields[1], expected_msh2)

# ################################################################################################################################
# ################################################################################################################################
