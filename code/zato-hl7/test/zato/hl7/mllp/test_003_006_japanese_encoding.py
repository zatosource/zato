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

class JapaneseEncodingTestCase(TestCase):
    """ Test 3.6 - build a message with MSH-18 = ISO IR87 and a PID patient name
    containing Japanese characters encoded in ISO-2022-JP. Verify delivery and encoding detection.
    """

    @classmethod
    def setUpClass(cls) -> 'None':
        cls.received_messages = []
        cls.received_ctx = []

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            cls.received_messages.append(data)
            cls.received_ctx.append(zato_ctx)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_japanese_iso_ir87(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'TestApp', b'TestFac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', b'JP_001',
            b'P', b'2.5',
            b'', b'', b'', b'', b'',
            b'ISO IR87',
        ])

        # Japanese characters encoded in ISO-2022-JP ..
        jp_name = '田中^太郎'.encode('iso2022_jp')
        pid = sep.join([b'PID', b'', b'', b'33333^^^Hosp^PI', b'', jp_name, b'', b'19700101', b'M'])
        pv1 = sep.join([b'PV1', b'', b'I', b'W^300^1^Hosp'])

        payload = cr.join([msh, pid, pv1]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'JP_001')

        self.assertEqual(len(self.received_messages), 1)
        self.assertIn(jp_name, self.received_messages[0])

        channel_item = self.received_ctx[0]['zato.channel_item']
        self.assertEqual(channel_item['data_encoding'], 'iso2022_jp')

# ################################################################################################################################
# ################################################################################################################################
