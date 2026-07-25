# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK

# httpx
import httpx

# Zato
from .wire import do_send, new_exchange, Payload as _payload, set_security
from zato.common.as2.common import AS2Error
from zato.common.as2.inbound import handle
from zato.common.as2.mdn import parse_mdn
from zato.common.as2.outbound import build_message

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

def _use_tampering_wire(exchange:'any_') -> 'None':
    """ Puts a wire in place that flips payload bytes inside the signed entity
    before it reaches the receiver.
    """
    def _handler(request:'httpx.Request') -> 'any_':

        body = request.read()
        tampered = body.replace(b'4523891', b'4523892')
        headers = dict(request.headers)

        result = handle(tampered, headers, exchange.receiver_partnerships, exchange.receiver_keystore)
        exchange.results.append(result)

        response = httpx.Response(result.status_code, content=result.body, headers=result.headers)
        return response

    transport = httpx.MockTransport(_handler)
    exchange.client = httpx.Client(transport=transport)

# ################################################################################################################################
# ################################################################################################################################

class TestErrorDispositions:
    """ Failures still produce an MDN with the matching disposition modifier.
    """

    def test_tampered_content_yields_integrity_check_failed(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, True, False)

        _use_tampering_wire(exchange)

        result = do_send(exchange)

        # The sender learns from the MDN that delivery failed ..
        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Integrity_Check_Failed

        # .. and the receiver never handed the payload over.
        inbound = exchange.results[0]
        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Integrity_Check_Failed
        assert len(inbound.payloads) == 0

# ################################################################################################################################

    def test_wrong_key_yields_decryption_failed(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The receiver's own certificate is not the one this message was encrypted to -
        # the fixture is session-scoped, so the change is always undone.
        exchange.sender_keystore.peer_encryption_certificate = parties.sender.signing_certificate

        try:
            result = do_send(exchange)

            assert not result.is_ok
            assert result.mdn
            assert result.mdn.modifier == AS2Error.Decryption_Failed

        finally:
            exchange.sender_keystore.peer_encryption_certificate = parties.receiver.signing_certificate

# ################################################################################################################################

    def test_error_mdn_is_signed_when_a_signed_receipt_was_requested(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, True, False)

        _use_tampering_wire(exchange)

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.is_signed is True

# ################################################################################################################################

    def test_unknown_partner_gets_an_unsigned_explanatory_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The receiver has no partnership for this identity pair at all.
        exchange.receiver_partnerships.clear()

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.is_signed is False
        assert result.mdn.modifier == AS2Error.Unknown_Trading_Relationship

        inbound = exchange.results[0]
        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Unknown_Trading_Relationship
        assert inbound.partnership is None

# ################################################################################################################################

    def test_unsupported_mic_algorithms_yield_a_failure_mdn(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        body, headers, _, _ = build_message(exchange.sender_partnership, exchange.sender_keystore, _payload)

        # The sender insists on a MIC algorithm nobody supports.
        headers['Disposition-Notification-Options'] = \
            'signed-receipt-protocol=required, pkcs7-signature; signed-receipt-micalg=required, md5'

        result = handle(body, headers, exchange.receiver_partnerships, exchange.receiver_keystore)

        assert result.is_error
        assert result.status_code == OK

        # The answer is a failed/Failure MDN, still signed because a signed receipt was requested.
        mdn = parse_mdn(result.body, result.content_type, exchange.sender_keystore)

        assert mdn.is_signed
        assert mdn.disposition == 'failed'
        assert mdn.modifier_kind == 'failure'
        assert mdn.modifier == 'unsupported MIC-algorithms'

# ################################################################################################################################
# ################################################################################################################################
