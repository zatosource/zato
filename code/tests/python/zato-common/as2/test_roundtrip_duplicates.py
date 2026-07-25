# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from .wire import do_send, new_exchange

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestReliability:
    """ The resend semantics - the same content travels under the same Message-ID
    because no MDN arrived for the original attempt.
    """

    def test_resend_reuses_the_message_id(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        first = do_send(exchange)

        # The resend goes out under the original Message-ID ..
        second = do_send(exchange, message_id=first.message_id)

        assert second.message_id == first.message_id

        # .. and both attempts reconcile, the second one against the stored MDN.
        assert first.is_ok
        assert second.is_ok

# ################################################################################################################################

    def test_fresh_sends_get_fresh_message_ids(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        first = do_send(exchange)
        second = do_send(exchange)

        assert first.message_id != second.message_id
        assert not exchange.results[1].is_duplicate

# ################################################################################################################################
# ################################################################################################################################

class TestDuplicateDetection:
    """ A replay of an already-processed message is answered with the stored MDN bytes,
    byte for byte, and its payload is never delivered a second time.
    """

    def test_duplicate_gets_the_stored_mdn_bytes(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        first = do_send(exchange)
        second = do_send(exchange, message_id=first.message_id)

        # The second delivery was recognized as a replay ..
        first_inbound = exchange.results[0]
        second_inbound = exchange.results[1]

        assert not first_inbound.is_duplicate
        assert second_inbound.is_duplicate

        # .. its payload was not delivered again ..
        assert len(first_inbound.payloads) == 1
        assert len(second_inbound.payloads) == 0

        # .. and the MDN bytes went out exactly as stored, never recomputed.
        assert second.response_body == first.response_body
        assert second_inbound.body == first_inbound.body

# ################################################################################################################################

    def test_different_message_ids_are_not_duplicates(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = do_send(exchange)
        _ = do_send(exchange)

        assert not exchange.results[0].is_duplicate
        assert not exchange.results[1].is_duplicate

        # Both deliveries handed their payload over.
        assert len(exchange.results[0].payloads) == 1
        assert len(exchange.results[1].payloads) == 1

# ################################################################################################################################
# ################################################################################################################################
