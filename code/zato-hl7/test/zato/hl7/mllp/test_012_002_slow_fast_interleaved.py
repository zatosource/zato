# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from threading import Thread
from time import monotonic
from unittest import TestCase

# gevent
from gevent import sleep as gsleep

# Test helpers
from conftest import (
    SB,
    EB_CR,
    build_adt_a01,
    frame,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class SlowFastInterleavedTestCase(TestCase):
    """ Test 12.2 - one connection sends a message in small chunks with 100ms delays.
    Another connection sends a complete message immediately.
    Verify the fast client gets its ACK without waiting for the slow client.
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

    def test_fast_not_blocked_by_slow(self) -> 'None':

        slow_payload = build_adt_a01(control_id=b'SLOW_001')
        fast_payload = build_adt_a01(control_id=b'FAST_001')

        fast_result = [None]
        fast_time = [None]

        def slow_sender() -> 'None':
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            sock.connect((self.host, self.port))
            try:
                data = SB + slow_payload + EB_CR
                chunk_size = 50
                for i in range(0, len(data), chunk_size):
                    sock.sendall(data[i:i + chunk_size])
                    gsleep(0.1)
                resp = b''
                while b'\x1c\x0d' not in resp:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    resp += chunk
            finally:
                sock.close()

        def fast_sender() -> 'None':
            gsleep(0.3)
            t0 = monotonic()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            sock.connect((self.host, self.port))
            try:
                sock.sendall(frame(fast_payload))
                resp = b''
                while b'\x1c\x0d' not in resp:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    resp += chunk
                fast_time[0] = monotonic() - t0
                fast_result[0] = parse_ack(unframe(resp))
            finally:
                sock.close()

        slow_thread = Thread(target=slow_sender)
        fast_thread = Thread(target=fast_sender)

        slow_thread.start()
        fast_thread.start()
        slow_thread.join(timeout=15.0)
        fast_thread.join(timeout=15.0)

        self.assertIsNotNone(fast_result[0])
        self.assertEqual(fast_result[0]['ack_code'], b'AA')
        self.assertEqual(fast_result[0]['control_id'], b'FAST_001')

        # The fast client should get its response well before the slow client finishes ..
        self.assertLess(fast_time[0], 3.0)

# ################################################################################################################################
# ################################################################################################################################
