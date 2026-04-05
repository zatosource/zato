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
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class AcceptAndImmediateDisconnectTestCase(TestCase):
    """ Test 1.1 - client connects then closes without sending anything.
    Server logs the disconnection, does not crash, keeps accepting new connections.
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

    def test_immediate_disconnect_then_normal_message(self) -> 'None':

        # Connect and immediately close ..
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.close()

        # Give the server a moment to process the disconnect ..
        sleep(0.2)

        # Now send a real message on a new connection to prove the server is still alive ..
        control_id = b'AFTERDC1'
        payload = build_adt_a01(control_id=control_id)
        framed = frame(payload)

        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2.settimeout(5.0)
        sock2.connect((self.host, self.port))
        sock2.sendall(framed)
        response_raw = sock2.recv(65536)
        sock2.close()

        # Verify the server processed the message ..
        response_payload = unframe(response_raw)
        ack = parse_ack(response_payload)

        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], control_id)

        # The callback must have been invoked exactly once (not for the disconnect) ..
        self.assertEqual(len(self.received_messages), 1)

# ################################################################################################################################
# ################################################################################################################################
