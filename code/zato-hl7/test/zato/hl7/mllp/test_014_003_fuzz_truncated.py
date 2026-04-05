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
from hypothesis.strategies import integers

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

class FuzzTruncatedTestCase(TestCase):
    """ Test 14.3 - generate a valid framed message, truncate at a random position, close the socket.
    The server must not crash. A subsequent clean connection must still work.
    """

    @classmethod
    def setUpClass(cls) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)
        cls.full_frame = frame(build_adt_a01(control_id=b'TRUNC_001'))

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    @given(cut_at=integers(min_value=1, max_value=200))
    @settings(max_examples=30, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_truncated_frame(self, cut_at:'int') -> 'None':

        # Clamp to the actual frame length ..
        cut_at = min(cut_at, len(self.full_frame) - 1)

        truncated = self.full_frame[:cut_at]

        with tcp_session(self.host, self.port, timeout=2.0) as sock:
            try:
                sock.sendall(truncated)
            except Exception:
                pass

        gsleep(0.2)

        # Server must still be alive ..
        msg = build_adt_a01(control_id=b'TRUNC_OK')
        resp = tcp_send(self.host, self.port, frame(msg))
        ack = parse_ack(unframe(resp))
        self.assertEqual(ack['ack_code'], b'AA')

# ################################################################################################################################
# ################################################################################################################################
