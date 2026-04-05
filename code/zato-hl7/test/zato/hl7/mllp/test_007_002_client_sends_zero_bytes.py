# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
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
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class ClientSendsZeroBytesTestCase(TestCase):
    """ Test 7.2 - connect, then shut down the write side with shutdown(SHUT_WR).
    The server receives a zero-length read and must detect the disconnect.
    A subsequent connection must still work.
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

    def test_shutdown_wr_detected(self) -> 'None':

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((self.host, self.port))

        # Shut down the write side, server sees a zero-length recv ..
        sock.shutdown(socket.SHUT_WR)

        # Read until the server closes the connection ..
        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    break
        except (ConnectionError, socket.timeout, OSError):
            pass
        finally:
            sock.close()

        # Give the server time to clean up ..
        gsleep(0.3)

        # A new connection should work fine ..
        msg = build_adt_a01(control_id=b'ZERO_001')
        response_raw = tcp_send(self.host, self.port, frame(msg))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'ZERO_001')

# ################################################################################################################################
# ################################################################################################################################
