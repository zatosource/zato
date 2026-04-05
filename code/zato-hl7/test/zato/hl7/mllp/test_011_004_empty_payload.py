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
    ini_path_from_test_file,
    start_server,
    tcp_session,
)

# ################################################################################################################################
# ################################################################################################################################

class EmptyPayloadTestCase(TestCase):
    """ Test 11.4 - send 0x0B 0x1C 0x0D (framing with zero-length payload).
    Verify the server handles it without crashing. The callback receives empty bytes
    and the server auto-generates an AA ACK.
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

    def test_empty_payload(self) -> 'None':

        empty_frame = SB + EB_CR

        with tcp_session(self.host, self.port, timeout=3.0) as sock:
            sock.sendall(empty_frame)

            resp = b''
            while b'\x1c\x0d' not in resp:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp += chunk

        # The server should have returned something framed ..
        self.assertTrue(len(resp) > 0)

        # The callback should have been called with empty bytes ..
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0], b'')

# ################################################################################################################################
# ################################################################################################################################
