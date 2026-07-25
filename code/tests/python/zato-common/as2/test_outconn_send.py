# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.mdn import normalize_message_id

# Zato
from .outconn_helpers import make_connection, Payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestConnection:

    def test_send_reconciles_the_sync_mdn(self, parties:'TestParties') -> 'None':

        connection, _, requests, results = make_connection(parties)

        result = connection.send('cid-1', Payload)

        # The delivery went out signed and encrypted and came back confirmed ..
        assert result.is_ok
        assert result.message_id
        assert result.mic

        # .. the MDN answers the message that was sent ..
        assert result.mdn

        answered_message_id = normalize_message_id(result.mdn.original_message_id)
        sent_message_id = normalize_message_id(result.message_id)

        assert answered_message_id == sent_message_id

        # .. and the receiver's real pipeline accepted the payload.
        assert len(requests) == 1

        first_result = results[0]
        assert not first_result.is_error

        first_payload = first_result.payloads[0]
        assert first_payload.data == Payload

# ################################################################################################################################

    def test_send_accepts_a_string_payload(self, parties:'TestParties') -> 'None':

        connection, _, _, results = make_connection(parties)

        payload = Payload.decode('ascii')
        result = connection.send('cid-1', payload)

        assert result.is_ok

        first_result = results[0]
        first_payload = first_result.payloads[0]

        assert first_payload.data == Payload

# ################################################################################################################################

    def test_send_reports_an_unconfirmed_delivery(self, parties:'TestParties') -> 'None':

        # The receiver does not know this sender, so its MDN reports an error disposition.
        connection, _, _, results = make_connection(parties, as2_from='UnknownSender')

        result = connection.send('cid-1', Payload)

        assert not result.is_ok

        first_result = results[0]
        assert first_result.is_error

# ################################################################################################################################
# ################################################################################################################################
