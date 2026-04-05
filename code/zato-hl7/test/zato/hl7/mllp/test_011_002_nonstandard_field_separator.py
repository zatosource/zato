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

class NonstandardFieldSeparatorTestCase(TestCase):
    """ Test 11.2 - build a raw MSH using # instead of | as the field separator.
    The server is encoding-agnostic at the MLLP layer, it just delivers bytes.
    The ACK builder reads the field separator from the MSH so it should use # too.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_messages = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_messages.append(data)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_hash_field_separator(self) -> 'None':

        sep = b'#'
        msh = sep.join([
            b'MSH', b'^~\\&',
            b'App', b'Fac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', b'HASH_001',
            b'P', b'2.5',
        ])
        pid = sep.join([b'PID', b'', b'', b'12345^^^Hosp^PI', b'', b'DOE^JOHN'])

        payload = msh + b'\x0d' + pid + b'\x0d'
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack_raw = unframe(response_raw)

        # The ACK should also use # as the field separator ..
        self.assertIn(b'MSH#', ack_raw)
        self.assertIn(b'MSA#', ack_raw)

        # Parse it with the # separator ..
        segments = ack_raw.split(b'\x0d')
        for seg in segments:
            if seg.startswith(b'MSA'):
                fields = seg.split(b'#')
                self.assertEqual(fields[1], b'AA')
                self.assertEqual(fields[2], b'HASH_001')
                break

        self.assertEqual(len(self.received_messages), 1)

# ################################################################################################################################
# ################################################################################################################################
