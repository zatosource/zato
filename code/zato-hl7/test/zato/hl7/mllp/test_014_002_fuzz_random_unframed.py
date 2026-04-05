# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# gevent
from gevent import sleep as gsleep

# Hypothesis
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import binary

# Test helpers
from conftest import (
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

class FuzzRandomUnframedTestCase(TestCase):
    """ Test 14.2 - generate arbitrary byte sequences and send them raw (no 0x0B prefix).
    The server must not crash. It should close the connection.
    A subsequent clean connection must still work.
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

    @given(payload=binary(min_size=1, max_size=4096))
    @settings(max_examples=30, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_random_unframed(self, payload:'bytes') -> 'None':

        # Skip payloads that happen to start with 0x0B (valid start byte) ..
        if payload[0:1] == b'\x0b':
            return

        with tcp_session(self.host, self.port, timeout=3.0) as sock:
            try:
                sock.sendall(payload)
                # Read whatever the server sends back (AR NAK or nothing) ..
                try:
                    sock.recv(65536)
                except Exception:
                    pass
            except Exception:
                pass

        gsleep(0.1)

        # Server must still be alive ..
        msg = build_adt_a01(control_id=b'FUZZ_OK')
        resp = tcp_send(self.host, self.port, frame(msg))
        ack = parse_ack(unframe(resp))
        self.assertEqual(ack['ack_code'], b'AA')

# ################################################################################################################################
# ################################################################################################################################
