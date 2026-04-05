# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
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

class BinaryPayloadTestCase(TestCase):
    """ Test 11.5 - send 0x0B + 256 random bytes + 0x1C 0x0D.
    Verify the callback receives those exact 256 random bytes unmodified (byte-for-byte comparison).
    The server is a transport layer, not a parser - it never validates whether the payload is actual HL7.
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

    def test_binary_payload_byte_for_byte(self) -> 'None':

        # Generate 256 random bytes, filtering out 0x1C followed by 0x0D
        # to avoid an accidental end sequence ..
        random_bytes = bytearray()
        while len(random_bytes) < 256:
            chunk = os.urandom(512)
            for i, b in enumerate(chunk):
                if len(random_bytes) >= 256:
                    break
                # Skip 0x0D if the previous byte was 0x1C (avoid end sequence) ..
                if b == 0x0D and random_bytes and random_bytes[-1] == 0x1C:
                    continue
                random_bytes.append(b)

        random_bytes = bytes(random_bytes)
        framed = SB + random_bytes + EB_CR

        with tcp_session(self.host, self.port, timeout=3.0) as sock:
            sock.sendall(framed)

            resp = b''
            while b'\x1c\x0d' not in resp:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp += chunk

        # The callback must have received the exact same bytes ..
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0], random_bytes)

# ################################################################################################################################
# ################################################################################################################################
