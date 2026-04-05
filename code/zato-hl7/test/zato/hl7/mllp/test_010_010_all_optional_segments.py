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

class AllOptionalSegmentsTestCase(TestCase):
    """ Test 10.10 - ADT^A01 with every optional segment filled in
    (NK1, AL1, DG1, GT1, IN1, etc.). Verify complete delivery.
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

    def test_all_optional(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'ADMSystem', b'Hospital',
            b'ZatoApp', b'ZatoFac',
            b'20240316160000', b'',
            b'ADT^A01', b'FULL_001',
            b'P', b'2.5',
        ])
        evn = sep.join([b'EVN', b'A01', b'20240316160000'])
        pid = sep.join([
            b'PID', b'1', b'', b'P12345^^^Hospital^PI', b'',
            b'SMITH^JOHN^Q', b'', b'19650214', b'M', b'', b'',
            b'123 Main St^^Springfield^IL^62701', b'', b'(217)555-1234',
            b'', b'', b'M', b'', b'', b'SSN123456789',
        ])
        nk1 = sep.join([b'NK1', b'1', b'SMITH^MARY', b'SPO^Spouse', b'456 Main St^^Springfield^IL^62701', b'(217)555-5678'])
        pv1 = sep.join([b'PV1', b'1', b'I', b'MED^201^A^Hospital', b'', b'', b'DR100^JONES^ALICE'])
        al1 = sep.join([b'AL1', b'1', b'DA', b'PENICILLIN^Penicillin', b'SV', b'Anaphylaxis'])
        dg1 = sep.join([b'DG1', b'1', b'', b'J18.9^Pneumonia, unspecified^ICD10', b'', b'20240316', b'A'])
        gt1 = sep.join([b'GT1', b'1', b'', b'SMITH^JOHN^Q', b'', b'123 Main St^^Springfield^IL^62701', b'(217)555-1234', b'', b'19650214', b'M', b'', b'SE'])
        in1 = sep.join([b'IN1', b'1', b'BC001^BlueCross^L', b'BlueCross BlueShield', b'PO Box 1000^^Chicago^IL^60601', b'', b'', b'GRP12345', b'', b'', b'', b'20240101', b'20241231'])

        payload = cr.join([msh, evn, pid, nk1, pv1, al1, dg1, gt1, in1]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'FULL_001')

        self.assertEqual(len(self.received_messages), 1)
        msg = self.received_messages[0]

        for segment_id in [b'MSH', b'EVN', b'PID', b'NK1', b'PV1', b'AL1', b'DG1', b'GT1', b'IN1']:
            self.assertIn(segment_id + sep, msg)

# ################################################################################################################################
# ################################################################################################################################
