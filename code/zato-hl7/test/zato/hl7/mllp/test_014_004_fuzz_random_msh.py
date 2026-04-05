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

class FuzzRandomMSHTestCase(TestCase):
    """ Test 14.4 - generate an HL7-shaped message with random bytes in MSH fields.
    Wrap in valid framing and send. The server must not crash.
    The callback must receive the payload. A response must be returned.
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

    @given(
        sending_app=binary(min_size=1, max_size=20),
        sending_fac=binary(min_size=1, max_size=20),
        control_id=binary(min_size=1, max_size=20),
        version=binary(min_size=1, max_size=10),
        charset=binary(min_size=0, max_size=20),
    )
    @settings(max_examples=50, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_random_msh_fields(self, sending_app:'bytes', sending_fac:'bytes',
                                control_id:'bytes', version:'bytes', charset:'bytes') -> 'None':

        # Filter out values containing the field separator, CR, or end sequence ..
        for val in [sending_app, sending_fac, control_id, version, charset]:
            if b'|' in val or b'\x0d' in val or b'\x1c' in val:
                return

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            sending_app, sending_fac,
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', control_id,
            b'P', version,
            b'', b'', b'', b'', b'',
            charset,
        ])
        payload = msh + cr

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

        # The callback must have been called ..
        self.assertEqual(len(self.received_messages), idx_before + 1)

# ################################################################################################################################
# ################################################################################################################################
