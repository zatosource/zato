# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Test helpers
from conftest import (
    SB,
    EB_CR,
    build_adt_a01,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class DuplicateHeaderAsPayloadTestCase(TestCase):
    """ Test 8.2 - send 0x0B + payload + 0x0B + more data + 0x1C 0x0D.
    The server consumes the first 0x0B as the start sequence and treats the second 0x0B
    as part of the payload. The message is processed, not rejected.
    Verify the callback receives payload that includes the embedded 0x0B byte.
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

    def test_duplicate_header_treated_as_payload(self) -> 'None':

        payload = build_adt_a01(control_id=b'DUP_001')

        # 0x0B + payload + 0x0B + extra data + 0x1C 0x0D ..
        raw = SB + payload + SB + b'extra_data' + EB_CR

        with tcp_session(self.host, self.port, timeout=3.0) as sock:
            sock.sendall(raw)

            resp = b''
            while b'\x1c\x0d' not in resp:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp += chunk

        ack = parse_ack(unframe(resp))
        self.assertEqual(ack['ack_code'], b'AA')

        # The callback receives everything between the first 0x0B and the 0x1C 0x0D,
        # including the embedded second 0x0B ..
        self.assertEqual(len(self.received_messages), 1)
        self.assertIn(SB, self.received_messages[0])
        self.assertIn(b'extra_data', self.received_messages[0])

# ################################################################################################################################
# ################################################################################################################################
