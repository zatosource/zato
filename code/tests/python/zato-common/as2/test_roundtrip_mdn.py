# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import ACCEPTED, NO_CONTENT, OK

# pytest
import pytest

# Zato
from .wire import do_send, new_exchange, Payload as _payload
from zato.common.as2.common import AS2Error, MDNMode
from zato.common.as2.mdn import normalize_message_id, parse_mdn

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestMDNModes:
    """ Synchronous, asynchronous and no MDN at all.
    """

    def test_no_mdn_requested(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_mode = MDNMode.Not_Requested

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn is None
        assert result.http_status == NO_CONTENT

        request = exchange.requests[0]
        assert 'disposition-notification-to' not in request.headers

        # The payload was still delivered.
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

# ################################################################################################################################

    def test_unsigned_sync_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_signed = False

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn
        assert result.mdn.is_signed is False

# ################################################################################################################################

    def test_signed_sync_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn
        assert result.mdn.is_signed is True
        assert result.mdn.original_message_id == result.message_id

        # The MDN's MIC is the one the receiver computed, matching the sender's.
        digest, _, algorithm = result.mic.partition(', ')
        assert result.mdn.mic == digest
        assert result.mdn.mic_algorithm == algorithm

# ################################################################################################################################

    def test_async_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_mode = MDNMode.Async
        exchange.sender_partnership.async_mdn_url = 'https://zatoretail.example.com/zato/as2/mdn'

        result = do_send(exchange)

        # The inbound POST is merely accepted - the MDN travels separately.
        assert result.is_ok
        assert result.mdn is None
        assert result.http_status == ACCEPTED

        request = exchange.requests[0]
        assert request.headers['receipt-delivery-option'] == 'https://zatoretail.example.com/zato/as2/mdn'

        # The receiver prepared the MDN for asynchronous delivery ..
        inbound = exchange.results[0]
        pending = inbound.pending_async_mdn

        assert pending
        assert pending.url == 'https://zatoretail.example.com/zato/as2/mdn'

        # .. and once delivered, it reconciles against the message that was sent.
        content_type = pending.headers['Content-Type']
        mdn = parse_mdn(pending.body, content_type, exchange.sender_keystore)

        assert mdn.is_signed
        assert normalize_message_id(mdn.original_message_id) == normalize_message_id(result.message_id)

        digest, _, algorithm = result.mic.partition(', ')
        assert mdn.mic == digest
        assert mdn.mic_algorithm == algorithm

# ################################################################################################################################

    def test_async_mdn_for_an_unknown_message_id_does_not_match(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_mode = MDNMode.Async
        exchange.sender_partnership.async_mdn_url = 'https://zatoretail.example.com/zato/as2/mdn'

        result = do_send(exchange)

        pending = exchange.results[0].pending_async_mdn

        content_type = pending.headers['Content-Type']
        mdn = parse_mdn(pending.body, content_type, exchange.sender_keystore)

        # An MDN answering some other message must never reconcile against this one.
        unknown_id = '<already-reconciled-or-unknown@partnercorp.example.com>'

        assert normalize_message_id(mdn.original_message_id) == normalize_message_id(result.message_id)
        assert normalize_message_id(mdn.original_message_id) != normalize_message_id(unknown_id)

# ################################################################################################################################

    def test_the_async_destination_carries_the_partnerships_transport_settings(
        self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.mdn_mode = MDNMode.Async
        exchange.sender_partnership.async_mdn_url = 'https://zatoretail.example.com/zato/as2/mdn'

        receiver_partnership = exchange.receiver_partnerships[0]
        receiver_partnership.verify_tls = False
        receiver_partnership.http_timeout_seconds = 17

        _ = do_send(exchange)

        # The transport settings travel with the pending delivery, so the caller making the
        # outgoing request does not have to reach back for the partnership.
        pending = exchange.results[0].pending_async_mdn

        assert pending.verify_tls is False
        assert pending.timeout_seconds == 17

# ################################################################################################################################
# ################################################################################################################################

class TestAsyncMDNDestination:
    """ The asynchronous MDN destination arrives in the sender's own Receipt-Delivery-Option
    header, so an unchecked one would let a caller choose where the server makes an outgoing
    request to - and the header is read on the error paths too, before the message has proven
    to come from the partner at all.
    """

    def _send_with_destination(self, exchange:'any_', destination:'any_') -> 'any_':
        exchange.sender_partnership.mdn_mode = MDNMode.Async
        exchange.sender_partnership.async_mdn_url = destination

        out = do_send(exchange)
        return out

# ################################################################################################################################

    def test_the_partners_own_endpoint_host_is_accepted(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = self._send_with_destination(exchange, 'https://zatoretail.example.com/zato/as2/mdn')

        pending = exchange.results[0].pending_async_mdn

        assert pending
        assert pending.url == 'https://zatoretail.example.com/zato/as2/mdn'

# ################################################################################################################################

    def test_another_host_is_refused_and_the_mdn_rides_on_the_response(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = self._send_with_destination(exchange, 'https://attacker.example.net/collect')

        inbound = exchange.results[0]

        # No outgoing request was prepared at all, and the receipt came back on the response
        # instead, which still gets it to whoever made the request.
        assert inbound.pending_async_mdn is None
        assert inbound.status_code == OK
        assert inbound.body

        # The receipt on the response is a real MDN for the message that arrived.
        mdn = parse_mdn(inbound.body, inbound.content_type, exchange.sender_keystore)

        assert mdn.disposition == 'processed'
        assert normalize_message_id(mdn.original_message_id) == inbound.message_id

# ################################################################################################################################

    def test_another_port_on_the_same_host_is_refused(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # A different port is a different service, so the host matching alone is not enough.
        _ = self._send_with_destination(exchange, 'https://zatoretail.example.com:9443/collect')

        assert exchange.results[0].pending_async_mdn is None

# ################################################################################################################################

    @pytest.mark.parametrize('destination', [
        'file:///etc/passwd',
        'gopher://zatoretail.example.com/1',
        'ftp://zatoretail.example.com/receipts',
    ])
    def test_only_http_and_https_are_accepted(self, parties:'TestParties', destination:'any_') -> 'None':
        exchange = new_exchange(parties)

        _ = self._send_with_destination(exchange, destination)

        assert exchange.results[0].pending_async_mdn is None

# ################################################################################################################################

    def test_an_unknown_partner_may_not_name_a_destination(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # No partnership matched, so there is nothing to hold the destination against and the
        # caller is a stranger - this is the path an unauthenticated request takes.
        exchange.receiver_partnerships.clear()

        _ = self._send_with_destination(exchange, 'https://attacker.example.net/collect')

        inbound = exchange.results[0]

        assert inbound.partnership is None
        assert inbound.pending_async_mdn is None
        assert inbound.error_modifier == AS2Error.Unknown_Trading_Relationship

# ################################################################################################################################

    def test_a_rejected_message_may_not_name_a_destination_either(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The message fails the partnership's security policy, which is an error path that
        # still builds an MDN - and it must not become an outgoing request of the peer's choosing.
        exchange.sender_partnership.sign = False
        exchange.sender_partnership.encrypt = False

        _ = self._send_with_destination(exchange, 'https://attacker.example.net/collect')

        inbound = exchange.results[0]

        assert inbound.is_error
        assert inbound.pending_async_mdn is None

# ################################################################################################################################

    def test_a_partnership_without_an_endpoint_accepts_no_destination(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # A receive-only partnership names no endpoint, so no host can be established
        # as the partner's own.
        exchange.receiver_partnerships[0].endpoint_url = ''

        _ = self._send_with_destination(exchange, 'https://zatoretail.example.com/zato/as2/mdn')

        assert exchange.results[0].pending_async_mdn is None

# ################################################################################################################################
# ################################################################################################################################
