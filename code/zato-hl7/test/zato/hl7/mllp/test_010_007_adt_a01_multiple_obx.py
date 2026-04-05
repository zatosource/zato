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

class ADTA01MultipleOBXTestCase(TestCase):
    """ Test 10.7 - ADT^A01 with embedded observation data (multiple OBX segments).
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

    def test_adt_a01_with_obx(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'ADMSystem', b'Hospital',
            b'ZatoApp', b'ZatoFac',
            b'20240316130000', b'',
            b'ADT^A01', b'MOBX_001',
            b'P', b'2.5',
        ])
        evn = sep.join([b'EVN', b'A01', b'20240316130000'])
        pid = sep.join([
            b'PID', b'1', b'', b'P12345^^^Hospital^PI', b'',
            b'DOE^JANE', b'', b'19900101', b'F',
        ])
        pv1 = sep.join([b'PV1', b'1', b'I', b'MED^201^A^Hospital'])
        obx1 = sep.join([b'OBX', b'1', b'NM', b'HEIGHT^Height^L', b'', b'170', b'cm', b'', b'N', b'', b'', b'F'])
        obx2 = sep.join([b'OBX', b'2', b'NM', b'WEIGHT^Weight^L', b'', b'68.5', b'kg', b'', b'N', b'', b'', b'F'])
        obx3 = sep.join([b'OBX', b'3', b'NM', b'BP_SYS^BP Systolic^L', b'', b'120', b'mmHg', b'', b'N', b'', b'', b'F'])

        payload = cr.join([msh, evn, pid, pv1, obx1, obx2, obx3]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'MOBX_001')

        self.assertEqual(len(self.received_messages), 1)
        msg = self.received_messages[0]
        self.assertIn(b'HEIGHT^Height^L', msg)
        self.assertIn(b'WEIGHT^Weight^L', msg)
        self.assertIn(b'BP_SYS^BP Systolic^L', msg)

# ################################################################################################################################
# ################################################################################################################################
