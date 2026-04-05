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

class UTF8EncodingTestCase(TestCase):
    """ Test 3.1 - build a message with MSH-18 = UNICODE UTF-8 and a PID patient name
    containing multi-byte UTF-8 characters (German umlauts). Verify callback receives
    correctly decoded data and ACK is returned.
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

    def test_utf8_with_german_umlauts(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'TestApp', b'TestFac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', b'UTF8_001',
            b'P', b'2.5',
            b'', b'', b'', b'', b'',
            b'UNICODE UTF-8',
        ])

        # German umlauts in UTF-8 ..
        name = 'Müller^Jürgen^Ö'.encode('utf-8')
        pid = sep.join([b'PID', b'', b'', b'12345^^^Hosp^PI', b'', name, b'', b'19800101', b'M'])
        pv1 = sep.join([b'PV1', b'', b'I', b'W^100^1^Hosp'])

        payload = cr.join([msh, pid, pv1]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'UTF8_001')

        # Verify the callback got the full payload with the UTF-8 bytes ..
        self.assertEqual(len(self.received_messages), 1)
        self.assertIn('Müller'.encode('utf-8'), self.received_messages[0])
        self.assertIn('Jürgen'.encode('utf-8'), self.received_messages[0])

        # Verify detected encoding is utf-8 ..
        channel_item = self.received_ctx[0]['zato.channel_item']
        self.assertEqual(channel_item['data_encoding'], 'utf-8')

# ################################################################################################################################
# ################################################################################################################################
