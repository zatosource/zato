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

class RepeatingFieldsTestCase(TestCase):
    """ Test 10.9 - PID with multiple patient addresses (XAD repeats using ~ separator).
    Verify the repetition separator is preserved through MLLP framing.
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

    def test_repeating_addresses(self) -> 'None':

        cr = b'\x0d'
        sep = b'|'

        msh = sep.join([
            b'MSH', b'^~\\&',
            b'ADMSystem', b'Hospital',
            b'ZatoApp', b'ZatoFac',
            b'20240316150000', b'',
            b'ADT^A08', b'REP_001',
            b'P', b'2.5',
        ])
        evn = sep.join([b'EVN', b'A08', b'20240316150000'])

        # PID-11 with two addresses separated by the ~ repetition separator ..
        addr1 = b'123 Main St^^Springfield^IL^62701^US'
        addr2 = b'456 Oak Ave^^Chicago^IL^60601^US'
        repeating_addr = addr1 + b'~' + addr2

        pid = sep.join([
            b'PID', b'1', b'', b'P12345^^^Hospital^PI', b'',
            b'SMITH^JOHN', b'', b'19650214', b'M', b'', b'',
            repeating_addr,
        ])
        pv1 = sep.join([b'PV1', b'1', b'I', b'MED^201^A^Hospital'])

        payload = cr.join([msh, evn, pid, pv1]) + cr
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')
        self.assertEqual(ack['control_id'], b'REP_001')

        self.assertEqual(len(self.received_messages), 1)
        msg = self.received_messages[0]

        # Both addresses and the ~ separator must be preserved ..
        self.assertIn(addr1 + b'~' + addr2, msg)

# ################################################################################################################################
# ################################################################################################################################
