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

class ACKPreservesVersionTestCase(TestCase):
    """ Test 4.9 - verify the auto-generated ACK preserves the HL7 version
    from the original message's MSH-12.
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

    def test_ack_uses_original_version(self) -> 'None':

        for version in [b'2.3', b'2.4', b'2.5', b'2.5.1', b'2.7']:

            control_id = b'VER_' + version.replace(b'.', b'')
            payload = build_adt_a01(control_id=control_id, version=version)
            response_raw = tcp_send(self.host, self.port, frame(payload))

            ack = parse_ack(unframe(response_raw))
            self.assertEqual(ack['ack_code'], b'AA')

            # MSH-12 is at index 11 in the fields list ..
            msh = ack['msh_fields']
            self.assertEqual(msh[11], version, f'Version mismatch for {version!r}')

# ################################################################################################################################
# ################################################################################################################################
