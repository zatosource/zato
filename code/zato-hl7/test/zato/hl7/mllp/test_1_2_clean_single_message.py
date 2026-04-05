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

class CleanSingleMessageTestCase(TestCase):
    """ Test 1.2 - send one framed ADT^A01, receive a framed ACK, verify:
    - MSA-1 is AA
    - MSA-2 echoes the original MSH-10 (message control id)
    - sender/receiver are swapped in the ACK MSH
    """

    @classmethod
    def setUpClass(cls):
        cls.received_messages = []
        cls.received_ctx = []

        def callback(service_name, data, data_format=None, zato_ctx=None):
            cls.received_messages.append(data)
            cls.received_ctx.append(zato_ctx)
            return None

        ini = ini_path_from_test_file(__file__)
        cls.server, cls.host, cls.port = start_server(ini, callback)

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_single_message_exchange(self):

        control_id = b'MSG00001'
        sending_app = b'SenderApp'
        sending_fac = b'SenderFac'
        receiving_app = b'RecvApp'
        receiving_fac = b'RecvFac'

        payload = build_adt_a01(
            control_id=control_id,
            sending_app=sending_app,
            sending_fac=sending_fac,
            receiving_app=receiving_app,
            receiving_fac=receiving_fac,
        )

        framed = frame(payload)
        response_raw = tcp_send(self.host, self.port, framed)

        # Unframe the response ..
        response_payload = unframe(response_raw)

        # Parse the ACK ..
        ack = parse_ack(response_payload)

        # MSA-1 must be AA ..
        self.assertEqual(ack['ack_code'], b'AA')

        # MSA-2 must echo the original MSH-10 ..
        self.assertEqual(ack['control_id'], control_id)

        # Sender/receiver must be swapped in the ACK MSH ..
        msh_fields = ack['msh_fields']
        ack_sending_app = msh_fields[2]
        ack_sending_fac = msh_fields[3]
        ack_receiving_app = msh_fields[4]
        ack_receiving_fac = msh_fields[5]

        self.assertEqual(ack_sending_app, receiving_app)
        self.assertEqual(ack_sending_fac, receiving_fac)
        self.assertEqual(ack_receiving_app, sending_app)
        self.assertEqual(ack_receiving_fac, sending_fac)

        # Verify the callback received the payload ..
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0], payload)

        # Verify the callback received the correct encoding ..
        channel_item = self.received_ctx[0]['zato.channel_item']
        self.assertEqual(channel_item['data_encoding'], 'iso-8859-1')

# ################################################################################################################################
# ################################################################################################################################
