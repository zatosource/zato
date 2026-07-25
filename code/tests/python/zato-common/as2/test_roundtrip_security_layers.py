# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# pytest
import pytest

# Zato
from .wire import do_send, new_exchange, Payload as _payload, set_security
from zato.common.as2.common import DigestAlgorithm, EncryptionAlgorithm

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestRoundtrip:
    """ The sender's send against the receiver's handle, over a mock wire.
    """

    def test_signed_encrypted_compressed(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.compress = True

        result = do_send(exchange)

        assert result.is_ok
        assert result.message_id
        assert result.mic
        assert result.http_status == OK

        # The receiver delivered exactly one document, byte for byte.
        inbound = exchange.results[0]

        assert not inbound.is_error
        assert not inbound.is_duplicate
        assert len(inbound.payloads) == 1
        assert inbound.payloads[0].data == _payload
        assert inbound.payloads[0].content_type == 'application/edi-x12'

        # Both sides computed the same MIC.
        assert inbound.mic == result.mic

# ################################################################################################################################

    def test_sha1_signed_3des_encrypted(self, parties:'TestParties') -> 'None':

        # The exact wire combination the SHA-1 and 3DES partnership preset produces -
        # an in-house SHA-1 SignedData inside an in-house 3DES envelope,
        # with a signed SHA-1 MDN MIC.
        exchange = new_exchange(parties)
        exchange.sender_partnership.sign_algorithm = DigestAlgorithm.SHA1
        exchange.sender_partnership.encryption_algorithm = EncryptionAlgorithm.DES_EDE3_CBC
        exchange.sender_partnership.mdn_mic_algorithms = [DigestAlgorithm.SHA1]

        result = do_send(exchange)

        assert result.is_ok
        assert result.message_id
        assert result.mic
        assert result.http_status == OK

        # The receiver delivered exactly one document, byte for byte.
        inbound = exchange.results[0]

        assert not inbound.is_error
        assert not inbound.is_duplicate
        assert len(inbound.payloads) == 1
        assert inbound.payloads[0].data == _payload

        # Both sides computed the same SHA-1 MIC.
        assert inbound.mic == result.mic
        assert result.mic.endswith('sha-1')

# ################################################################################################################################

    def test_signed_only(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, True, False)

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

# ################################################################################################################################

    def test_encrypted_only(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, False, True)

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

# ################################################################################################################################

    def test_plain(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, False, False)

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

        # Nothing wrapped the payload, so it went over the wire as it is.
        assert exchange.bodies[0] == _payload

# ################################################################################################################################

    @pytest.mark.parametrize('compress_before_signing', [True, False])
    def test_compression_in_both_orders(self, parties:'TestParties', compress_before_signing:'any_') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.compress = True
        exchange.sender_partnership.compress_before_signing = compress_before_signing

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload
        assert exchange.results[0].mic == result.mic

# ################################################################################################################################

    def test_force_base64(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        exchange.sender_partnership.force_base64 = True

        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

        # The outermost entity actually travelled base64-encoded.
        request = exchange.requests[0]
        assert request.headers['content-transfer-encoding'] == 'base64'

# ################################################################################################################################
# ################################################################################################################################
