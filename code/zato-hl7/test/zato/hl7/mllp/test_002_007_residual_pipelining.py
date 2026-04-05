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

class ResidualPipeliningTestCase(TestCase):
    """ Test 2.7 - send two properly framed messages concatenated in a single send().
    Server must process both messages and return two ACKs.
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

    def test_two_messages_in_one_send(self) -> 'None':

        msg1 = frame(build_adt_a01(control_id=b'PIPE_001'))
        msg2 = frame(build_adt_a01(control_id=b'PIPE_002'))

        combined = msg1 + msg2

        with tcp_session(self.host, self.port) as sock:
            sock.sendall(combined)

            # Read both ACK responses ..
            all_data = b''
            for _ in range(20):
                chunk = sock.recv(65536)
                if not chunk:
                    break
                all_data += chunk
                # We expect two framed ACK responses, each ending with 0x1C 0x0D ..
                if all_data.count(b'\x1c\x0d') >= 2:
                    break

        # Split the two framed responses ..
        responses = all_data.split(b'\x1c\x0d')
        # Last element is empty after the final split ..
        responses = [resp for resp in responses if resp]

        self.assertEqual(len(responses), 2)

        ack1 = parse_ack(unframe(responses[0] + b'\x1c\x0d'))
        ack2 = parse_ack(unframe(responses[1] + b'\x1c\x0d'))

        self.assertEqual(ack1['ack_code'], b'AA')
        self.assertEqual(ack1['control_id'], b'PIPE_001')

        self.assertEqual(ack2['ack_code'], b'AA')
        self.assertEqual(ack2['control_id'], b'PIPE_002')

        self.assertEqual(len(self.received_messages), 2)

# ################################################################################################################################
# ################################################################################################################################
