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

class MSH2PaddingDisabledTestCase(TestCase):
    """ Test 15.11 - MSH-2 padding disabled; short encoding chars unchanged.
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

    def test_msh2_short_encoding_unchanged(self) -> 'None':
        raw = (
            b'MSH|^&|SendApp|SendFac|RecvApp|RecvFac|20240101120000||ADT^A01|CTRL011|P|2.5\x0d'
            b'PID|||12345^^^Hospital^PI||DOE^JOHN||19800101|M\x0d'
        )

        tcp_send(self.host, self.port, frame(raw))

        self.assertEqual(len(self.received_payloads), 1)
        got = self.received_payloads[0]
        self.assertEqual(got, raw)

        cr_idx = got.find(b'\x0d')
        msh_segment = got[:cr_idx]
        field_sep = msh_segment[3:4]
        fields = msh_segment.split(field_sep)
        self.assertEqual(fields[1], b'^&')


# ################################################################################################################################
# ################################################################################################################################
