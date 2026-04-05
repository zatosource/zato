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
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class BackToBackConnectionsTestCase(TestCase):
    """ Test 11.6 - open a connection, send a message, close. Immediately open a new connection
    and send another message. Verify both messages are processed.
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

    def test_back_to_back(self) -> 'None':

        msg1 = build_adt_a01(control_id=b'B2B_001')
        resp1 = tcp_send(self.host, self.port, frame(msg1))
        ack1 = parse_ack(unframe(resp1))
        self.assertEqual(ack1['ack_code'], b'AA')
        self.assertEqual(ack1['control_id'], b'B2B_001')

        msg2 = build_adt_a01(control_id=b'B2B_002')
        resp2 = tcp_send(self.host, self.port, frame(msg2))
        ack2 = parse_ack(unframe(resp2))
        self.assertEqual(ack2['ack_code'], b'AA')
        self.assertEqual(ack2['control_id'], b'B2B_002')

        self.assertEqual(len(self.received_messages), 2)

# ################################################################################################################################
# ################################################################################################################################
