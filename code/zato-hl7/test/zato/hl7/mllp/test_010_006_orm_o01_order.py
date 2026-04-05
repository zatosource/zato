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

class ORMO01OrderTestCase(TestCase):
    """ Test 10.6 - ORM^O01 (pharmacy/lab order) with MSH, PID, ORC, OBR.
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

    def test_orm_o01(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'OrderSystem', b'Hospital',
            b'ZatoApp', b'ZatoFac',
            b'20240316120000', b'',
            b'ORM^O01', b'ORD_001',
            b'P', b'2.5',
        ])
        pid = sep.join([
            b'PID', b'1', b'', b'P12345^^^Hospital^PI', b'',
            b'SMITH^JOHN', b'', b'19650214', b'M',
        ])
        orc = sep.join([b'ORC', b'NW', b'ORD001', b'', b'', b'', b'', b'^once', b'', b'20240316120000', b'', b'DR100^JONES^ALICE'])
        obr = sep.join([b'OBR', b'1', b'ORD001', b'', b'BMP^Basic Metabolic Panel^L'])

        payload = cr.join([msh, pid, orc, obr]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'ORD_001')

        self.assertEqual(len(self.received_messages), 1)
        self.assertIn(b'ORM^O01', self.received_messages[0])
        self.assertIn(b'BMP^Basic Metabolic Panel^L', self.received_messages[0])

# ################################################################################################################################
# ################################################################################################################################
