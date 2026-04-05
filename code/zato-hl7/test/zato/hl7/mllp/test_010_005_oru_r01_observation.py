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

class ORUR01ObservationTestCase(TestCase):
    """ Test 10.5 - ORU^R01 (observation result) with MSH, PID, OBR, OBX carrying a numeric lab value.
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

    def test_oru_r01(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'LabSystem', b'Hospital',
            b'ZatoApp', b'ZatoFac',
            b'20240316110000', b'',
            b'ORU^R01', b'LAB_001',
            b'P', b'2.5',
        ])
        pid = sep.join([
            b'PID', b'1', b'', b'P12345^^^Hospital^PI', b'',
            b'SMITH^JOHN', b'', b'19650214', b'M',
        ])
        obr = sep.join([b'OBR', b'1', b'ORD001', b'', b'CBC^Complete Blood Count^L'])
        obx = sep.join([
            b'OBX', b'1', b'NM', b'WBC^White Blood Cell Count^L', b'',
            b'7.5', b'10*3/uL', b'4.5-11.0', b'N', b'', b'', b'F',
        ])

        payload = cr.join([msh, pid, obr, obx]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'LAB_001')

        self.assertEqual(len(self.received_messages), 1)
        self.assertIn(b'ORU^R01', self.received_messages[0])
        self.assertIn(b'7.5', self.received_messages[0])

# ################################################################################################################################
# ################################################################################################################################
