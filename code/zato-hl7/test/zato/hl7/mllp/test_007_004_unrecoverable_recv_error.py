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
    SB,
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

class UnrecoverableRecvErrorTestCase(TestCase):
    """ Test 7.4 - after a connection is established, the client sends the start byte
    then shuts down both sides of its socket externally. The server's recv raises an OSError
    which is caught by the generic exception handler. The server must remain operational.
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

    def test_recv_oserror(self) -> 'None':

        # Send a start byte to get the connection into the recv loop,
        # then forcibly shut down the socket ..
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((self.host, self.port))
        sock.sendall(SB)

        gsleep(0.2)

        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()

        # Give the server time to detect the error ..
        gsleep(0.5)

        # The server should still be alive ..
        msg = build_adt_a01(control_id=b'OSERR_001')
        response_raw = tcp_send(self.host, self.port, frame(msg))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'OSERR_001')

# ################################################################################################################################
# ################################################################################################################################
