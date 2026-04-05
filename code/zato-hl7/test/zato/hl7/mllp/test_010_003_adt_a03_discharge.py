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

class ADTA03DischargeTestCase(TestCase):
    """ Test 10.3 - full ADT^A03 (patient discharge) with MSH, EVN, PID, PV1.
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

    def test_adt_a03(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'ADMSystem', b'Hospital',
            b'ZatoApp', b'ZatoFac',
            b'20240315140000', b'',
            b'ADT^A03', b'DIS_001',
            b'P', b'2.5',
        ])
        evn = sep.join([b'EVN', b'A03', b'20240315140000'])
        pid = sep.join([
            b'PID', b'1', b'', b'P12345^^^Hospital^PI', b'',
            b'SMITH^JOHN^Q', b'', b'19650214', b'M',
        ])
        pv1 = sep.join([b'PV1', b'1', b'I', b'MED^201^A^Hospital', b'', b'', b'DR100^JONES^ALICE', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'', b'20240315140000'])

        payload = cr.join([msh, evn, pid, pv1]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'DIS_001')

        self.assertEqual(len(self.received_messages), 1)
        self.assertIn(b'ADT^A03', self.received_messages[0])

# ################################################################################################################################
# ################################################################################################################################
