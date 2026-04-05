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
    tcp_session,
    unframe,
)

from test_009_001_large_message import _build_message_with_obx

# ################################################################################################################################
# ################################################################################################################################

class ManyRecvCallsTestCase(TestCase):
    """ Test 9.2 - configure read_buffer_size = 64.
    Send a 4 KB framed message. The server reassembles it across ~64 recv calls.
    Verify correct delivery.
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

    def test_4k_with_tiny_buffer(self) -> 'None':

        payload = _build_message_with_obx(b'TINY_001', 4096)

        with tcp_session(self.host, self.port, timeout=10.0) as sock:
            sock.sendall(frame(payload))

            resp = b''
            while b'\x1c\x0d' not in resp:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                resp += chunk

        ack = parse_ack(unframe(resp))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'TINY_001')

        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0], payload)

# ################################################################################################################################
# ################################################################################################################################
