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

class ISO8859EncodingTestCase(TestCase):
    """ Test 3.2 - build a message with MSH-18 = 8859/1 and a PID patient name
    containing a French accented character (e-acute). Verify correct delivery.
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

    def test_iso8859_with_french_accents(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'TestApp', b'TestFac',
            b'ZatoApp', b'ZatoFac',
            b'20240101120000', b'',
            b'ADT^A01', b'LAT1_001',
            b'P', b'2.5',
            b'', b'', b'', b'', b'',
            b'8859/1',
        ])

        # French name with e-acute (0xe9) and e-grave (0xe8) in ISO-8859-1 ..
        name = 'Bénédicte^Hélène'.encode('iso-8859-1')
        pid = sep.join([b'PID', b'', b'', b'67890^^^Hosp^PI', b'', name, b'', b'19750315', b'F'])
        pv1 = sep.join([b'PV1', b'', b'I', b'W^200^1^Hosp'])

        payload = cr.join([msh, pid, pv1]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'LAT1_001')

        # Verify the callback got the ISO-8859-1 bytes ..
        self.assertEqual(len(self.received_messages), 1)
        self.assertIn(b'\xe9', self.received_messages[0])
        self.assertIn(b'\xe8', self.received_messages[0])

        # Verify detected encoding ..
        channel_item = self.received_ctx[0]['zato.channel_item']
        self.assertEqual(channel_item['data_encoding'], 'iso-8859-1')

# ################################################################################################################################
# ################################################################################################################################
