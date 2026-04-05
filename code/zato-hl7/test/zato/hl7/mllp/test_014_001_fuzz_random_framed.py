# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Hypothesis
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import binary

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

class FuzzRandomFramedTestCase(TestCase):
    """ Test 14.1 - generate arbitrary byte sequences, wrap in valid MLLP framing, send to server.
    The server must not crash. The callback must receive the exact bytes.
    An MLLP-framed response must be returned.
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

    @given(payload=binary(min_size=1, max_size=65536))
    @settings(max_examples=50, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_random_framed_payload(self, payload:'bytes') -> 'None':

        # Filter out payloads containing the end sequence to avoid premature message splitting ..
        if EB_CR in payload:
            return

        idx_before = len(self.received_messages)

        framed = SB + payload + EB_CR

        with tcp_session(self.host, self.port, timeout=5.0) as sock:
            sock.sendall(framed)

            resp = b''
            while b'\x1c\x0d' not in resp:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                resp += chunk

        # Server must have returned a framed response ..
        self.assertTrue(resp.startswith(SB))
        self.assertTrue(resp.endswith(EB_CR))

        # The callback must have received the exact payload ..
        self.assertEqual(len(self.received_messages), idx_before + 1)
        self.assertEqual(self.received_messages[-1], payload)

# ################################################################################################################################
# ################################################################################################################################
