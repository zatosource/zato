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

class ACKSenderReceiverSwapTestCase(TestCase):
    """ Test 4.8 - verify the auto-generated ACK swaps sending/receiving application
    and facility fields from the original message's MSH.
    """

    @classmethod
    def setUpClass(cls) -> 'None':

        def callback(service_name:'str', data:'bytes', data_format:'str'=None, zato_ctx:'dict'=None) -> 'None':
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls) -> 'None':
        cls.server.stop()

    def test_sender_receiver_swapped_in_ack(self) -> 'None':

        payload = build_adt_a01(
            control_id=b'SWAP_001',
            sending_app=b'SenderApp',
            sending_fac=b'SenderFac',
            receiving_app=b'RecvApp',
            receiving_fac=b'RecvFac',
        )
        response_raw = tcp_send(self.host, self.port, frame(payload))

        ack = parse_ack(unframe(response_raw))
        self.assertEqual(ack['ack_code'], b'AA')

        # The ACK's MSH fields should have sender/receiver swapped ..
        msh = ack['msh_fields']

        # msh[0] = 'MSH', msh[1] = encoding chars
        # msh[2] = sending_app (was RecvApp in original)
        # msh[3] = sending_fac (was RecvFac in original)
        # msh[4] = receiving_app (was SenderApp in original)
        # msh[5] = receiving_fac (was SenderFac in original)
        self.assertEqual(msh[2], b'RecvApp')
        self.assertEqual(msh[3], b'RecvFac')
        self.assertEqual(msh[4], b'SenderApp')
        self.assertEqual(msh[5], b'SenderFac')

# ################################################################################################################################
# ################################################################################################################################
