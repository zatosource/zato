# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Hypothesis
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import integers

# Test helpers
from conftest import (
    SB,
    EB_CR,
    ini_path_from_test_file,
    start_server,
    tcp_session,
)

# ################################################################################################################################
# ################################################################################################################################

class FuzzRandomSizeTestCase(TestCase):
    """ Test 14.5 - generate valid MLLP frames with payload sizes from 0 bytes to 256 KB.
    The server must handle all sizes without crashing.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_messages = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_messages.append(len(data))
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    @given(size=integers(min_value=0, max_value=262144))
    @settings(max_examples=20, deadline=30000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_random_payload_size(self, size:'int') -> 'None':

        # Use 'A' bytes to avoid accidental end sequences ..
        payload = b'A' * size

        idx_before = len(self.received_messages)
        framed = SB + payload + EB_CR

        with tcp_session(self.host, self.port, timeout=15.0) as sock:
            sock.sendall(framed)

            resp = b''
            while EB_CR not in resp:
                chunk = sock.recv(262144)
                if not chunk:
                    break
                resp += chunk

        self.assertTrue(resp.startswith(SB))
        self.assertTrue(resp.endswith(EB_CR))

        self.assertEqual(len(self.received_messages), idx_before + 1)
        self.assertEqual(self.received_messages[-1], size)

# ################################################################################################################################
# ################################################################################################################################
