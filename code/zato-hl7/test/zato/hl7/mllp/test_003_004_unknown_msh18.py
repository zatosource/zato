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
    start_server,
    tcp_send,
)

# ################################################################################################################################
# ################################################################################################################################

class UnknownMSH18TestCase(TestCase):
    """ Test 3.4 - build a message with MSH-18 = BOGUS_ENCODING.
    Verify the server falls back to the default codec (ISO-8859-1).
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_ctx = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_ctx.append(zato_ctx)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_unknown_msh18_defaults_to_iso8859(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'TestApp', b'TestFac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', b'BOGUS_001',
            b'P', b'2.5',
            b'', b'', b'', b'', b'',
            b'BOGUS_ENCODING',
        ])
        pid = sep.join([b'PID', b'', b'', b'11111^^^Hosp^PI', b'', b'Doe^John', b'', b'19900101', b'M'])

        payload = cr.join([msh, pid]) + cr
        _ = tcp_send(self.host, self.port, frame(payload))

        self.assertEqual(len(self.received_ctx), 1)
        channel_item = self.received_ctx[0]['zato.channel_item']
        self.assertEqual(channel_item['data_encoding'], 'iso-8859-1')

# ################################################################################################################################
# ################################################################################################################################
