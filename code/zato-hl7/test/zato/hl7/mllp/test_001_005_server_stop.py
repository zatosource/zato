# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from time import sleep
from unittest import TestCase

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

class ServerStopTestCase(TestCase):
    """ Test 1.5 - connect, send a message, then call server.stop().
    Verify the response arrives before the server shuts down.
    Verify a subsequent connection attempt is refused.
    """

    def test_stop_after_message(self) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            return None

        ini = ini_path_from_test_file(__file__)
        server, host, port = start_server(ini, callback)

        # .. send a message and get a response while server is running ..
        control_id = b'STOP_001'
        response_raw = tcp_send(host, port, frame(build_adt_a01(control_id=control_id)))
        ack = parse_ack(unframe(response_raw))

        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], control_id)

        # .. stop the server ..
        server.stop()
        sleep(0.3)

        # .. verify new connections are refused ..
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)

        with self.assertRaises((ConnectionRefusedError, OSError)):
            sock.connect((host, port))

        sock.close()

# ################################################################################################################################
# ################################################################################################################################
