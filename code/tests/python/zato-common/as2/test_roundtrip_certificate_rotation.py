# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# Zato
from .wire import do_send, new_exchange, Payload as _payload
from zato.common.as2.common import AS2Error
from zato.common.as2.partnership import CertificateEntry
from zato.common.util.xml_.keystore import DecryptionEntry, new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

def _certificate_entry(certificate:'any_', valid_from:'any_' = None, valid_until:'any_' = None) -> 'any_':
    """ Builds one entry of a partner's certificate rotation list.
    """
    out = CertificateEntry()

    out.certificate = certificate
    out.valid_from = valid_from
    out.valid_until = valid_until

    return out

# ################################################################################################################################

def _rotated_sender_keystore(parties:'TestParties', rotated:'any_') -> 'any_':
    """ The sending side's keystore after it rotated its signing pair -
    encryption and MDN verification still target the receiver's current certificate.
    """
    out = new_keystore()

    out.signing_key = rotated.key
    out.signing_certificate_chain = [rotated.certificate]
    out.peer_encryption_certificate = parties.receiver.signing_certificate
    out.peer_signing_certificate = parties.receiver.signing_certificate

    return out

# ################################################################################################################################

def _receiver_keystore_with_entry(parties:'TestParties', rotated:'any_') -> 'any_':
    """ The receiving side's keystore during a rotation of its own decryption pair -
    the old key stays primary while the new pair joins the rotation entries.
    """
    out = new_keystore()

    out.signing_key = parties.receiver.signing_key
    out.signing_certificate_chain = parties.receiver.signing_certificate_chain
    out.decryption_key = parties.receiver.decryption_key
    out.peer_signing_certificate = parties.receiver.peer_signing_certificate

    entry = DecryptionEntry()
    entry.key = rotated.key
    entry.certificate = rotated.certificate
    out.decryption_entries.append(entry)

    return out

# ################################################################################################################################

def _receiver_keystore_signing_with(parties:'TestParties', rotated:'any_') -> 'any_':
    """ The receiving side's keystore after it rotated its signing pair - the old
    decryption pair stays on the rotation entries so incoming messages still decrypt.
    """
    out = new_keystore()

    out.signing_key = rotated.key
    out.signing_certificate_chain = [rotated.certificate]
    out.decryption_key = parties.receiver.decryption_key
    out.peer_signing_certificate = parties.receiver.peer_signing_certificate

    entry = DecryptionEntry()
    entry.key = parties.receiver.decryption_key
    entry.certificate = parties.receiver.signing_certificate
    out.decryption_entries.append(entry)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCertificateRotation:
    """ The overlap window end to end - more than two live certificates, staged activation,
    encryption following the most recently activated certificate and rotation of our own keys.
    """

    def test_overlap_window_accepts_signatures_from_all_live_certificates(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        first_rotated = make_rotated_pair('as2-sender-rotation-first')
        second_rotated = make_rotated_pair('as2-sender-rotation-second')

        now = datetime.now(timezone.utc)

        # Three of the partner's certificates are live at once - the original one
        # plus two staged rotations whose activation dates have passed.
        receiver_partnership = exchange.receiver_partnerships[0]

        current_entry = _certificate_entry(parties.sender.signing_certificate)
        first_entry = _certificate_entry(first_rotated.certificate, valid_from=now - timedelta(days=2))
        second_entry = _certificate_entry(second_rotated.certificate, valid_from=now - timedelta(days=1))

        receiver_partnership.verification_certificates.append(current_entry)
        receiver_partnership.verification_certificates.append(first_entry)
        receiver_partnership.verification_certificates.append(second_entry)

        # A message signed with each of the three keys is accepted.
        result = do_send(exchange)
        assert result.is_ok

        exchange.sender_keystore = _rotated_sender_keystore(parties, first_rotated)
        result = do_send(exchange)
        assert result.is_ok

        exchange.sender_keystore = _rotated_sender_keystore(parties, second_rotated)
        result = do_send(exchange)
        assert result.is_ok

        for inbound in exchange.results:
            assert not inbound.is_error
            assert inbound.payloads[0].data == _payload

# ################################################################################################################################

    def test_a_not_yet_activated_certificate_is_rejected(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        rotated = make_rotated_pair('as2-sender-rotation-early')
        now = datetime.now(timezone.utc)

        # The staged certificate only activates a month from now.
        receiver_partnership = exchange.receiver_partnerships[0]

        current_entry = _certificate_entry(parties.sender.signing_certificate)
        staged_entry = _certificate_entry(rotated.certificate, valid_from=now + timedelta(days=30))

        receiver_partnership.verification_certificates.append(current_entry)
        receiver_partnership.verification_certificates.append(staged_entry)

        # A message already signed with the staged key is not accepted yet.
        exchange.sender_keystore = _rotated_sender_keystore(parties, rotated)
        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Authentication_Failed

        inbound = exchange.results[0]
        assert inbound.is_error
        assert inbound.error_modifier == AS2Error.Authentication_Failed

# ################################################################################################################################

    def test_outbound_encrypts_to_the_most_recently_activated_certificate(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        rotated = make_rotated_pair('as2-receiver-rotation')
        now = datetime.now(timezone.utc)

        # The partner's rotation list holds the current certificate plus an activated next one.
        sender_partnership = exchange.sender_partnership

        current_entry = _certificate_entry(parties.receiver.signing_certificate)
        next_entry = _certificate_entry(rotated.certificate, valid_from=now - timedelta(days=1))

        sender_partnership.encryption_certificates.append(current_entry)
        sender_partnership.encryption_certificates.append(next_entry)

        # The receiver still runs with its old key alone, so a message encrypted
        # to the next certificate does not decrypt there - the wire-level proof
        # that encryption switched over.
        result = do_send(exchange)

        assert not result.is_ok
        assert result.mdn
        assert result.mdn.modifier == AS2Error.Decryption_Failed

        # Once the next key joins the receiver's rotation entries, the same send decrypts.
        exchange.receiver_keystore = _receiver_keystore_with_entry(parties, rotated)

        result = do_send(exchange)

        assert result.is_ok
        assert exchange.results[1].payloads[0].data == _payload

# ################################################################################################################################

    def test_the_old_certificate_still_decrypts_during_our_own_rotation(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        # The receiver already carries its next pair on the rotation entries ..
        rotated = make_rotated_pair('as2-receiver-rotation')
        exchange.receiver_keystore = _receiver_keystore_with_entry(parties, rotated)

        # .. while the sender still encrypts to the old certificate - the primary pair handles it.
        result = do_send(exchange)

        assert result.is_ok
        first_payload = exchange.results[0].payloads[0]
        assert first_payload.data == _payload

# ################################################################################################################################

    def test_sync_mdn_signed_with_the_partners_new_certificate_reconciles(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        rotated = make_rotated_pair('as2-receiver-rotation')
        now = datetime.now(timezone.utc)

        # The receiver already signs its MDNs with the new pair ..
        exchange.receiver_keystore = _receiver_keystore_signing_with(parties, rotated)

        # .. and the sender's rotation list carries both of the partner's certificates.
        sender_partnership = exchange.sender_partnership

        current_entry = _certificate_entry(parties.receiver.signing_certificate)
        next_entry = _certificate_entry(rotated.certificate, valid_from=now - timedelta(days=1))

        sender_partnership.verification_certificates.append(current_entry)
        sender_partnership.verification_certificates.append(next_entry)

        result = do_send(exchange)

        assert result.is_ok
        assert result.mdn
        assert result.mdn.signer_certificate.serial_number == rotated.certificate.serial_number

# ################################################################################################################################

    def test_sync_mdn_from_an_unlisted_certificate_does_not_reconcile(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        exchange = new_exchange(parties)

        rotated = make_rotated_pair('as2-receiver-rotation')

        # The receiver signs its MDNs with a pair the sender was never told about ..
        exchange.receiver_keystore = _receiver_keystore_signing_with(parties, rotated)

        # .. and the sender's rotation list only knows the partner's current certificate.
        current_entry = _certificate_entry(parties.receiver.signing_certificate)
        exchange.sender_partnership.verification_certificates.append(current_entry)

        result = do_send(exchange)

        # The MDN's signer is not accepted, so it counts as no MDN received.
        assert not result.is_ok
        assert result.mdn is None

# ################################################################################################################################
# ################################################################################################################################
