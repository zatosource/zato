# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Hypothesis
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import lists, integers

# Test helpers
from conftest import (
    EB_CR,
    SB,
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

class FuzzRandomChunksTestCase(TestCase):
    """ Test 14.6 - take a valid framed message and send it in random-sized chunks (1 to 500 bytes).
    The server must reassemble correctly and return an ACK.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_messages = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_messages.append(data)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)
        cls.payload = build_adt_a01(control_id=b'CHUNK_001')
        cls.framed = frame(cls.payload)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    @given(chunk_sizes=lists(integers(min_value=1, max_value=500), min_size=1, max_size=200))
    @settings(max_examples=30, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_random_chunk_send(self, chunk_sizes:'list') -> 'None':

        idx_before = len(self.received_messages)
        data = self.framed
        offset = 0

        with tcp_session(self.host, self.port, timeout=5.0) as sock:

            for cs in chunk_sizes:
                if offset >= len(data):
                    break
                end = min(offset + cs, len(data))
                sock.sendall(data[offset:end])
                offset = end

            # Send any remaining bytes ..
            if offset < len(data):
                sock.sendall(data[offset:])

            resp = b''
            while EB_CR not in resp:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                resp += chunk

        ack = parse_ack(unframe(resp))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'CHUNK_001')

        self.assertEqual(len(self.received_messages), idx_before + 1)
        self.assertEqual(self.received_messages[-1], self.payload)

# ################################################################################################################################
# ################################################################################################################################
