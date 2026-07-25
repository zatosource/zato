# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from .wire import do_send, new_exchange, Payload as _payload, Receiver_Identifier as _receiver_identifier, \
    Sender_Identifier as _sender_identifier, set_security
from zato.common.as2.common import Default, TransferMode
from zato.common.as2.inbound import handle
from zato.common.as2.outbound import build_message
from zato.common.as2.partnership import HTTPAuth

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestWireShape:
    """ Wire-level assertions - what actually left the sender, not what the APIs report.
    """

    def test_ciphertext_on_the_wire(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = do_send(exchange)

        request = exchange.requests[0]
        body = exchange.bodies[0]

        # The wire carries an encrypted entity and none of the plaintext.
        assert request.headers['content-type'].startswith('application/pkcs7-mime; smime-type=enveloped-data')
        assert b'ISA*00' not in body
        assert b'4523891' not in body

# ################################################################################################################################

    def test_compression_on_the_wire(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, False, False)
        exchange.sender_partnership.compress = True

        result = do_send(exchange)

        request = exchange.requests[0]
        body = exchange.bodies[0]

        # The wire carries a compressed entity and none of the plaintext.
        assert request.headers['content-type'].startswith('application/pkcs7-mime; smime-type=compressed-data')
        assert b'ISA*00' not in body

        assert result.is_ok

# ################################################################################################################################

    def test_as2_headers(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)

        request = exchange.requests[0]

        assert request.headers['as2-version'] == '1.2'
        assert request.headers['as2-from'] == _sender_identifier
        assert request.headers['as2-to'] == _receiver_identifier
        assert request.headers['message-id'] == result.message_id
        assert request.headers['subject'] == Default.Subject
        assert request.headers['mime-version'] == '1.0'
        assert request.headers['ediint-features'] == 'multiple-attachments, AS2-Reliability'

        # A signed synchronous MDN was requested.
        assert request.headers['disposition-notification-to'] == _sender_identifier
        assert request.headers['disposition-notification-options'] == \
            'signed-receipt-protocol=required, pkcs7-signature; signed-receipt-micalg=required, sha-256'
        assert 'receipt-delivery-option' not in request.headers

# ################################################################################################################################

    def test_version_pinning(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.as2_version = '1.1'

        result = do_send(exchange)

        assert result.is_ok
        assert exchange.requests[0].headers['as2-version'] == '1.1'

# ################################################################################################################################

    def test_inbound_accepts_an_absent_version(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # An AS2 1.0 peer sends no AS2-Version header at all - inbound never rejects on version.
        body, headers, _, _ = build_message(exchange.sender_partnership, exchange.sender_keystore, _payload)
        del headers['AS2-Version']

        result = handle(body, headers, exchange.receiver_partnerships, exchange.receiver_keystore)

        assert not result.is_error
        assert result.payloads[0].data == _payload

# ################################################################################################################################

    def test_quoted_identifiers(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.as2_from = 'Zato Retail'
        exchange.sender_partnership.as2_to = 'Partner:Corp'

        receiver_partnership = exchange.receiver_partnerships[0]
        receiver_partnership.as2_from = 'Partner:Corp'
        receiver_partnership.as2_to = 'Zato Retail'

        result = do_send(exchange)

        # Identifiers with a space or a colon travel as quoted-strings ..
        request = exchange.requests[0]
        assert request.headers['as2-from'] == '"Zato Retail"'
        assert request.headers['as2-to'] == '"Partner:Corp"'

        # .. and the receiver unquoted them back before matching the partnership.
        inbound = exchange.results[0]
        assert inbound.as2_from == 'Zato Retail'
        assert inbound.as2_to == 'Partner:Corp'
        assert not inbound.is_error

        assert result.is_ok

# ################################################################################################################################

    def test_ediint_features_are_surfaced(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        _ = do_send(exchange)

        inbound = exchange.results[0]
        assert inbound.ediint_features == 'multiple-attachments, AS2-Reliability'

# ################################################################################################################################
# ################################################################################################################################

class TestTransferModes:
    """ Content-Length is the default framing, chunked is per partner, threshold switches on size.
    """

    def test_content_length_by_default(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)

        request = exchange.requests[0]
        assert 'content-length' in request.headers
        assert 'transfer-encoding' not in request.headers

        assert result.is_ok

# ################################################################################################################################

    def test_chunked(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.http_transfer_mode = TransferMode.Chunked

        result = do_send(exchange)

        request = exchange.requests[0]
        assert request.headers['transfer-encoding'] == 'chunked'
        assert 'content-length' not in request.headers

        assert result.is_ok

# ################################################################################################################################

    def test_threshold_switches_to_chunked(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.http_transfer_mode = TransferMode.Threshold
        exchange.sender_partnership.chunked_threshold_bytes = 16

        result = do_send(exchange)

        request = exchange.requests[0]
        assert request.headers['transfer-encoding'] == 'chunked'

        assert result.is_ok

# ################################################################################################################################

    def test_threshold_keeps_content_length_below_it(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.http_transfer_mode = TransferMode.Threshold
        exchange.sender_partnership.chunked_threshold_bytes = 100 * 1024 * 1024

        result = do_send(exchange)

        request = exchange.requests[0]
        assert 'content-length' in request.headers
        assert 'transfer-encoding' not in request.headers

        assert result.is_ok

# ################################################################################################################################

    def test_basic_auth(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        auth = HTTPAuth()
        auth.username = 'zato.retail'
        auth.password = 'Test password'

        exchange.sender_partnership.http_auth = auth

        result = do_send(exchange)

        request = exchange.requests[0]
        assert request.headers['authorization'].startswith('Basic ')

        assert result.is_ok

# ################################################################################################################################
# ################################################################################################################################
