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

class MSH18RepetitionTestCase(TestCase):
    """ Test 3.5 - build a message with MSH-18 containing a repetition separator,
    e.g. "UNICODE UTF-8~8859/1". The server should use the first value only (utf-8).
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

    def test_msh18_repetition_uses_first(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'TestApp', b'TestFac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', b'REP_001',
            b'P', b'2.5',
            b'', b'', b'', b'', b'',
            b'UNICODE UTF-8~8859/1',
        ])
        pid = sep.join([b'PID', b'', b'', b'22222^^^Hosp^PI', b'', b'Smith^Jane', b'', b'19850505', b'F'])

        payload = cr.join([msh, pid]) + cr
        _ = tcp_send(self.host, self.port, frame(payload))

        self.assertEqual(len(self.received_ctx), 1)
        channel_item = self.received_ctx[0]['zato.channel_item']
        self.assertEqual(channel_item['data_encoding'], 'utf-8')

# ################################################################################################################################
# ################################################################################################################################
