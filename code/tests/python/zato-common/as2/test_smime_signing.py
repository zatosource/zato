# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# pytest
import pytest

# Zato
from .smime_helpers import EDI_Content_Type as _edi_content_type, EDI_Payload as _edi_payload, new_edi_part
from zato.common.as2.common import AS2Error, AS2ProtocolException, AS2SecurityException
from zato.common.as2.smime import sign, verify
from zato.common.util.xml_.keystore import new_keystore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

class TestSignVerify:
    """ Signing one entity and verifying it back, plus every way the signature can fail to hold.
    """

    def test_sign_verify_roundtrip(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        signed = sign(part, parties.sender)
        result = verify(signed, parties.receiver)

        assert result.part.data == _edi_payload
        assert result.part.content_type == _edi_content_type
        assert result.signer_certificate == parties.sender.signing_certificate
        assert result.digest_algorithm == 'sha-256'

# ################################################################################################################################

    def test_signed_content_type_declares_the_protocol_and_micalg(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        # The input spelling has no dash - the output must use the RFC 5751 one regardless.
        signed = sign(part, parties.sender, digest_algorithm='sha256')

        assert signed.content_type.startswith('multipart/signed')
        assert 'protocol="application/pkcs7-signature"' in signed.content_type
        assert 'micalg=sha-256' in signed.content_type

# ################################################################################################################################

    @pytest.mark.parametrize('algorithm', ['sha-1', 'sha-256', 'sha-384', 'sha-512'])
    def test_sign_verify_all_digest_algorithms(self, parties:'TestParties', algorithm:'any_') -> 'None':
        part = new_edi_part()

        signed = sign(part, parties.sender, digest_algorithm=algorithm)
        result = verify(signed, parties.receiver)

        assert result.digest_algorithm == algorithm
        assert result.part.data == _edi_payload

# ################################################################################################################################

    @pytest.mark.parametrize('algorithm', ['sha-1', 'sha-256'])
    def test_signing_time_is_extracted(self, parties:'TestParties', algorithm:'any_') -> 'None':
        part = new_edi_part()

        before = datetime.now(timezone.utc) - timedelta(minutes=1)
        after = datetime.now(timezone.utc) + timedelta(minutes=1)

        signed = sign(part, parties.sender, digest_algorithm=algorithm)
        result = verify(signed, parties.receiver)

        assert result.signing_time is not None
        assert before <= result.signing_time <= after

# ################################################################################################################################

    def test_tampered_content_is_detected(self, parties:'TestParties') -> 'None':
        part = new_edi_part()
        signed = sign(part, parties.sender)

        signed.data = signed.data.replace(b'PO-2026-001', b'PO-2026-999')

        with pytest.raises(AS2SecurityException) as exception_information:
            _ = verify(signed, parties.receiver)

        assert exception_information.value.modifier == AS2Error.Integrity_Check_Failed

# ################################################################################################################################

    def test_garbage_signature_is_detected(self, parties:'TestParties') -> 'None':
        part = new_edi_part()
        signed = sign(part, parties.sender)

        # The base64 of a DER ContentInfo always starts with MII - corrupting it
        # makes the signature part unparseable.
        signed.data = signed.data.replace(b'MII', b'NII', 1)

        with pytest.raises(AS2SecurityException) as exception_information:
            _ = verify(signed, parties.receiver)

        assert exception_information.value.modifier == AS2Error.Integrity_Check_Failed

# ################################################################################################################################

    def test_trust_anchor_mode_accepts_a_chain_to_the_anchor(self, parties:'TestParties') -> 'None':
        part = new_edi_part()
        signed = sign(part, parties.sender)

        # No pinned certificate - trust flows from the CA anchor alone.
        keystore = new_keystore()
        keystore.trust_anchors = [parties.ca_certificate]

        result = verify(signed, keystore)

        assert result.signer_certificate == parties.sender.signing_certificate

# ################################################################################################################################

    def test_untrusted_ca_is_rejected(self, parties:'TestParties', unrelated_ca_certificate:'any_') -> 'None':
        part = new_edi_part()
        signed = sign(part, parties.sender)

        keystore = new_keystore()
        keystore.trust_anchors = [unrelated_ca_certificate]

        with pytest.raises(AS2SecurityException) as exception_information:
            _ = verify(signed, keystore)

        assert exception_information.value.modifier == AS2Error.Authentication_Failed

# ################################################################################################################################

    def test_wrong_pinned_certificate_is_rejected(self, parties:'TestParties') -> 'None':
        part = new_edi_part()
        signed = sign(part, parties.sender)

        # Pin the receiver's own certificate instead of the sender's.
        keystore = new_keystore()
        keystore.peer_signing_certificate = parties.receiver.signing_certificate

        with pytest.raises(AS2SecurityException) as exception_information:
            _ = verify(signed, keystore)

        assert exception_information.value.modifier == AS2Error.Authentication_Failed

# ################################################################################################################################

    def test_unsigned_entity_is_rejected(self, parties:'TestParties') -> 'None':
        part = new_edi_part()

        with pytest.raises(AS2ProtocolException) as exception_information:
            _ = verify(part, parties.receiver)

        assert exception_information.value.modifier == AS2Error.Insufficient_Message_Security

# ################################################################################################################################

    def test_accepted_certificates_admit_a_listed_signer(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        part = new_edi_part()
        signed = sign(part, parties.sender)

        # An empty keystore would reject the signer - the rotation list alone admits it.
        keystore = new_keystore()
        rotated = make_rotated_pair('as2-sender-rotated')

        accepted = [rotated.certificate, parties.sender.signing_certificate]
        result = verify(signed, keystore, accepted)

        assert result.signer_certificate == parties.sender.signing_certificate

# ################################################################################################################################

    def test_accepted_certificates_reject_an_unlisted_signer(
        self, parties:'TestParties', make_rotated_pair:'any_') -> 'None':
        part = new_edi_part()
        signed = sign(part, parties.sender)

        # The rotation list holds another certificate, so even the pinned keystore
        # entry does not help - the list is the trust decision.
        rotated = make_rotated_pair('as2-sender-rotated')
        accepted = [rotated.certificate]

        with pytest.raises(AS2SecurityException) as exception_information:
            _ = verify(signed, parties.receiver, accepted)

        assert exception_information.value.modifier == AS2Error.Authentication_Failed

# ################################################################################################################################
# ################################################################################################################################
