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

class ThreePipelinedTestCase(TestCase):
    """ Test 2.8 - concatenate three framed messages into a single send().
    Verify three ACKs are returned, each with the correct control id.
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

    def test_three_messages_in_one_send(self) -> 'None':

        control_ids = [b'TRI_001', b'TRI_002', b'TRI_003']
        combined = b''
        for control_id in control_ids:
            combined += frame(build_adt_a01(control_id=control_id))

        with tcp_session(self.host, self.port) as sock:
            sock.sendall(combined)

            # Read all three ACK responses ..
            all_data = b''
            for _ in range(30):
                chunk = sock.recv(65536)
                if not chunk:
                    break
                all_data += chunk
                if all_data.count(b'\x1c\x0d') >= 3:
                    break

        # Split the framed responses ..
        responses = [resp for resp in all_data.split(b'\x1c\x0d') if resp]

        self.assertEqual(len(responses), 3)

        for idx, control_id in enumerate(control_ids):
            ack = parse_ack(unframe(responses[idx] + b'\x1c\x0d'))
            self.assertEqual(ack['ack_code'], b'AA')
            self.assertEqual(ack['control_id'], control_id)

        self.assertEqual(len(self.received_messages), 3)

# ################################################################################################################################
# ################################################################################################################################
