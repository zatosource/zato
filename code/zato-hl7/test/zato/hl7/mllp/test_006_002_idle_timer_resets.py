# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# gevent
from gevent import sleep as gsleep

# Test helpers
from conftest import (
    build_adt_a01,
    frame,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class IdleTimerResetsTestCase(TestCase):
    """ Test 6.2 - configure idle_timeout = 3, recv_timeout = 1.
    Connect, send a message at t=0, sleep 2 seconds, send another message.
    Verify the connection is still alive after the second message (timer reset).
    """

    @classmethod
    def setUpClass(cls) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_idle_timer_resets_after_message(self) -> 'None':

        msg1 = build_adt_a01(control_id=b'IDLE_001')
        msg2 = build_adt_a01(control_id=b'IDLE_002')

        with tcp_session(self.host, self.port, timeout=10.0) as sock:

            # First message at t=0 ..
            sock.sendall(frame(msg1))
            resp1 = b''
            while b'\x1c\x0d' not in resp1:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp1 += chunk

            ack1 = parse_ack(unframe(resp1))
            self.assertEqual(ack1['ack_code'], b'AA')

            # Sleep 2 seconds (within the 3s idle timeout) ..
            gsleep(2.0)

            # Second message - if the timer reset, connection is still alive ..
            sock.sendall(frame(msg2))
            resp2 = b''
            while b'\x1c\x0d' not in resp2:
                chunk = sock.recv(4096)
                if not chunk:
                    self.fail('Connection closed before second ACK was received')
                resp2 += chunk

            ack2 = parse_ack(unframe(resp2))
            self.assertEqual(ack2['ack_code'], b'AA')
            self.assertEqual(ack2['control_id'], b'IDLE_002')

# ################################################################################################################################
# ################################################################################################################################
