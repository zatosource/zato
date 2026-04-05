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

class MessageWithNTETestCase(TestCase):
    """ Test 10.8 - ORU^R01 with NTE (notes and comments) segments containing free text.
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

    def test_nte_segments(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'LabSystem', b'Hospital',
            b'ZatoApp', b'ZatoFac',
            b'20240316140000', b'',
            b'ORU^R01', b'NTE_001',
            b'P', b'2.5',
        ])
        pid = sep.join([
            b'PID', b'1', b'', b'P12345^^^Hospital^PI', b'',
            b'SMITH^JOHN', b'', b'19650214', b'M',
        ])
        obr = sep.join([b'OBR', b'1', b'ORD001', b'', b'CBC^Complete Blood Count^L'])
        obx = sep.join([b'OBX', b'1', b'NM', b'WBC^WBC^L', b'', b'7.5', b'10*3/uL', b'4.5-11.0', b'N', b'', b'', b'F'])
        nte1 = sep.join([b'NTE', b'1', b'L', b'Patient fasting for 12 hours before collection.'])
        nte2 = sep.join([b'NTE', b'2', b'L', b'Sample slightly hemolyzed but within acceptable limits.'])

        payload = cr.join([msh, pid, obr, obx, nte1, nte2]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'NTE_001')

        self.assertEqual(len(self.received_messages), 1)
        msg = self.received_messages[0]
        self.assertIn(b'Patient fasting for 12 hours', msg)
        self.assertIn(b'Sample slightly hemolyzed', msg)

# ################################################################################################################################
# ################################################################################################################################
