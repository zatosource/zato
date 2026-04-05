# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Test helpers
from conftest import (
    frame,
    ini_path_from_test_file,
    parse_ack,
    start_server,
    tcp_send,
    unframe,
)

# ################################################################################################################################
# ################################################################################################################################

class NonstandardEncodingCharsTestCase(TestCase):
    """ Test 11.3 - build a raw MSH with @~\\! instead of ^~\\&.
    Verify the ACK echoes the encoding characters correctly.
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

    def test_custom_encoding_chars(self) -> 'None':

        sep = b'|'
        custom_enc = b'@~\\!'

        msh = sep.join([
            b'MSH', custom_enc,
            b'App', b'Fac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', b'ENC_001',
            b'P', b'2.5',
        ])
        payload = msh + b'\x0d'

        response_raw = tcp_send(self.host, self.port, frame(payload))
        ack = parse_ack(unframe(response_raw))

        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'ENC_001')

        # The ACK MSH-2 (encoding characters) should echo back the custom value ..
        msh_fields = ack['msh_fields']
        self.assertEqual(msh_fields[1], custom_enc)

# ################################################################################################################################
# ################################################################################################################################
