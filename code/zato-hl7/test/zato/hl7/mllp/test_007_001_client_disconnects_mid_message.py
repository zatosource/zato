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
    SB,
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

class ClientDisconnectsMidMessageTestCase(TestCase):
    """ Test 7.1 - send 0x0B + half of a message payload, then close the socket.
    Server must detect the disconnect and log it without crashing.
    A subsequent connection and message exchange must still work.
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

    def test_mid_message_disconnect(self) -> 'None':

        payload = build_adt_a01(control_id=b'MID_001')
        half = payload[:len(payload) // 2]

        # Send start byte + half payload, then close ..
        with tcp_session(self.host, self.port) as sock:
            sock.sendall(SB + half)

        # Give the server time to detect the disconnect ..
        gsleep(0.5)

        # A new connection should work fine ..
        full_msg = build_adt_a01(control_id=b'MID_002')
        response_raw = tcp_send(self.host, self.port, frame(full_msg))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'MID_002')

# ################################################################################################################################
# ################################################################################################################################
