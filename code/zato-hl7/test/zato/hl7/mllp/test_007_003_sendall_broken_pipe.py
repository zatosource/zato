# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from threading import Event
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
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class SendallBrokenPipeTestCase(TestCase):
    """ Test 7.3 - the callback closes the client socket from a second thread before
    the server can send the response. The server must catch the ConnectionError on sendall.
    A subsequent connection must still work.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.client_sockets = []
        cls.close_event = Event()

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            if cls.client_sockets:
                try:
                    cls.client_sockets[0].shutdown(socket.SHUT_RDWR)
                    cls.client_sockets[0].close()
                except Exception:
                    pass
                cls.close_event.set()
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_broken_pipe_on_sendall(self) -> 'None':

        payload = build_adt_a01(control_id=b'BPIPE_001')

        # Create a raw socket so we can stash a reference for the callback to close ..
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((self.host, self.port))
        self.client_sockets.append(sock)

        sock.sendall(frame(payload))

        # Wait for the callback to close the socket ..
        self.close_event.wait(timeout=5.0)
        gsleep(0.5)

        # The server should still be alive - verify with a new connection ..
        msg = build_adt_a01(control_id=b'BPIPE_002')
        response_raw = tcp_send(self.host, self.port, frame(msg))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'BPIPE_002')

# ################################################################################################################################
# ################################################################################################################################
