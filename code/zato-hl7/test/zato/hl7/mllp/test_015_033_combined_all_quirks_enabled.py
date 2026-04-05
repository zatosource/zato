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
    parse_ack,
    start_server,
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class CombinedAllQuirksEnabledTestCase(TestCase):
    """ Test 15.33 - Combined: all quirks enabled at once.
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

    def test_malformed_message_normalized(self) -> 'None':
        raw = (
            b'MSH|^| Lab|Fac1|RecvApp|RecvFac\x0a'
            b'PID|||12345^^^Hospital^PI||DOE^JOHN||19800101|M\x0a'
        )

        response_raw = tcp_send(self.host, self.port, frame(raw))

        self.assertEqual(len(self.received_payloads), 1)
        got = self.received_payloads[0]
        self.assertNotIn(b'\x0a', got)

        cr_idx = got.find(b'\x0d')
        msh_segment = got[:cr_idx]
        field_sep = msh_segment[3:4]
        fields = msh_segment.split(field_sep)
        self.assertEqual(fields[1], b'^~\\&')
        self.assertEqual(fields[8], b'ACK')
        self.assertEqual(fields[9], b'0')
        self.assertEqual(fields[10], b'P')
        self.assertEqual(fields[11], b'2.5')

        ack = parse_ack(unframe(response_raw))
        self.assertIn('msh_fields', ack)
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['msh_fields'][4], b'Lab')


# ################################################################################################################################
# ################################################################################################################################
