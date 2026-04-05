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
    tcp_session,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class MultipleMessagesOneConnectionTestCase(TestCase):
    """ Test 1.3 - send three framed messages sequentially on the same TCP socket.
    Verify three separate ACK responses, each with the correct MSA-2 matching the respective MSH-10.
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

    def test_three_messages_on_same_connection(self) -> 'None':

        control_ids = [b'MSG_A_001', b'MSG_A_002', b'MSG_A_003']

        with tcp_session(self.host, self.port) as sock:
            for control_id in control_ids:
                payload = build_adt_a01(control_id=control_id)
                sock.sendall(frame(payload))
                response_raw = sock.recv(65536)

                ack = parse_ack(unframe(response_raw))
                self.assertEqual(ack['ack_code'], b'AA')
                self.assertEqual(ack['control_id'], control_id)

        self.assertEqual(len(self.received_messages), 3)

# ################################################################################################################################
# ################################################################################################################################
