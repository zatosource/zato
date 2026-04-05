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
    parse_ack,
    start_server,
    tcp_send,
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class CallbackRaisesThenSucceedsTestCase(TestCase):
    """ Test 4.7 - callback raises on the first call, succeeds on the second.
    Verify the connection stays alive and the second message gets an AA ACK.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.call_count = 0

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.call_count += 1
            if cls.call_count == 1:
                raise RuntimeError('First call fails')
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_first_fails_second_succeeds(self) -> 'None':

        msg1 = build_adt_a01(control_id=b'FAIL_001')
        msg2 = build_adt_a01(control_id=b'OK_002')

        with tcp_session(self.host, self.port) as sock:

            # First message - should get AE NAK ..
            sock.sendall(frame(msg1))
            resp1 = b''
            while b'\x1c\x0d' not in resp1:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp1 += chunk

            ack1 = parse_ack(unframe(resp1))
            self.assertEqual(ack1['ack_code'], b'AE')
            self.assertEqual(ack1['control_id'], b'FAIL_001')

            # Second message on the same connection - should get AA ACK ..
            sock.sendall(frame(msg2))
            resp2 = b''
            while b'\x1c\x0d' not in resp2:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp2 += chunk

            ack2 = parse_ack(unframe(resp2))
            self.assertEqual(ack2['ack_code'], b'AA')
            self.assertEqual(ack2['control_id'], b'OK_002')

# ################################################################################################################################
# ################################################################################################################################
