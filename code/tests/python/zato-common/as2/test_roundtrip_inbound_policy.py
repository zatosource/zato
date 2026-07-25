# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from .wire import do_send, new_exchange, Payload as _payload, set_security
from zato.common.as2.common import AS2Error
from zato.common.as2.inbound import layers as inbound_layers, pipeline as inbound_pipeline

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestInboundBounds:
    """ Every unbounded quantity on the pre-authentication path has a ceiling, because all of it
    runs before the message is known to come from the partner at all.
    """

    def test_an_oversized_body_is_turned_down(self, parties:'TestParties', monkeypatch:'any_') -> 'None':
        exchange = new_exchange(parties)

        # A ceiling low enough to cross without building a genuinely huge request.
        monkeypatch.setattr(inbound_pipeline, 'Max_Inbound_Bytes', 16)

        result = do_send(exchange)

        assert not result.is_ok

        inbound_result = exchange.results[0]

        assert inbound_result.is_error
        assert inbound_result.error_modifier == AS2Error.Unexpected_Processing_Error
        assert len(inbound_result.payloads) == 0

# ################################################################################################################################

    def test_a_body_within_the_ceiling_is_accepted(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        result = do_send(exchange)

        assert result.is_ok
        assert exchange.results[0].payloads[0].data == _payload

# ################################################################################################################################

    def test_stacked_layers_are_turned_down(self, parties:'TestParties', monkeypatch:'any_') -> 'None':
        exchange = new_exchange(parties)

        # Signing plus encryption is two layers, so a ceiling of one is crossed by the
        # ordinary message the sender builds, exercising the same guard a stacked one would.
        monkeypatch.setattr(inbound_layers, 'Max_Layer_Depth', 1)

        result = do_send(exchange)

        assert not result.is_ok

        inbound_result = exchange.results[0]

        assert inbound_result.is_error
        assert inbound_result.error_modifier == AS2Error.Unexpected_Processing_Error
        assert len(inbound_result.payloads) == 0

# ################################################################################################################################

    def test_the_ordinary_layer_count_stays_within_the_ceiling(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # Compression, signing and encryption together - the deepest shape real messages use.
        exchange.sender_partnership.compress = True

        result = do_send(exchange)

        assert result.is_ok
        assert exchange.results[0].payloads[0].data == _payload

# ################################################################################################################################
# ################################################################################################################################

class TestInboundSecurityPolicy:
    """ The partnership's own signing and encryption terms are enforced on what arrives,
    not merely on what we send - otherwise the identity pair, which travels in the clear
    in every message, would be the only thing standing between a stranger and a delivered document.
    """

    def test_unsigned_message_is_rejected_when_the_partnership_requires_signing(
        self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The sender drops signing while the receiving side still requires it.
        exchange.sender_partnership.sign = False

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Insufficient_Message_Security

        # Nothing was handed over to the application.
        inbound = exchange.results[0]

        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Insufficient_Message_Security
        assert len(inbound.payloads) == 0

# ################################################################################################################################

    def test_unencrypted_message_is_rejected_when_the_partnership_requires_encryption(
        self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        exchange.sender_partnership.encrypt = False

        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Insufficient_Message_Security

        inbound = exchange.results[0]

        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Insufficient_Message_Security
        assert len(inbound.payloads) == 0

# ################################################################################################################################

    def test_plaintext_post_is_rejected_when_the_partnership_requires_both(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The bare payload with only the AS2 identity headers, which is what an attacker
        # who merely read one of the partner's messages is able to construct.
        exchange.sender_partnership.sign = False
        exchange.sender_partnership.encrypt = False

        result = do_send(exchange)

        assert not result.is_ok
        assert exchange.bodies[0] == _payload

        inbound = exchange.results[0]

        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Insufficient_Message_Security
        assert len(inbound.payloads) == 0

# ################################################################################################################################

    def test_the_error_mdn_still_reports_the_received_content_mic(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        exchange.sender_partnership.sign = False
        exchange.sender_partnership.encrypt = False

        _ = do_send(exchange)

        # The MIC is computed before the policy check, so the partner can tell
        # which message we turned down.
        inbound = exchange.results[0]
        assert inbound.mic

# ################################################################################################################################

    def test_a_partnership_requiring_nothing_accepts_a_plaintext_post(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)
        set_security(exchange, False, False)

        result = do_send(exchange)

        assert result.is_ok

        inbound = exchange.results[0]
        assert not inbound.is_error
        assert inbound.payloads[0].data == _payload

# ################################################################################################################################

    def test_more_security_than_required_is_accepted(self, parties:'TestParties') -> 'None':
        exchange = new_exchange(parties)

        # The receiving side asks for signing alone while the sender also encrypts -
        # the requirement is a floor, not an exact match.
        for partnership in exchange.receiver_partnerships:
            partnership.encrypt = False

        result = do_send(exchange)

        assert result.is_ok

        inbound = exchange.results[0]
        assert not inbound.is_error
        assert inbound.payloads[0].data == _payload

# ################################################################################################################################
# ################################################################################################################################
