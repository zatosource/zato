# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from uuid import uuid4

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.as4.common import AS4SecurityException, CryptoSuite, EbMSError, NS
from zato.common.as4.ebms import build_envelope, build_user_message, new_message_id
from zato.common.as4.outbound import new_part
from zato.common.as4.pmode import new_pmode
from zato.common.as4.security.encrypt import encrypt_parts
from zato.common.as4.security.sign import sign_envelope
from zato.common.as4.security.verify import decrypt_parts, verify_envelope
from zato.common.util.xml_.constants import Algorithm, TokenType
from zato.common.util.xml_.core import qname, utc_timestamp, XMLSecurityException
from zato.common.util.xml_.keystore import new_keystore
from zato.common.util.xml_.token import build_pkipath, parse_pkipath
from zato.common.util.xml_.xmlsec import encode_base64

# ################################################################################################################################
# ################################################################################################################################

def _signed_message(keystore, token_type=TokenType.X509v3):
    """ Builds one signed user message with a single payload part.
    """
    pmode = new_pmode()
    pmode.initiator.party_id = 'party-a'
    pmode.responder.party_id = 'party-b'
    pmode.security.token_type = token_type

    part = new_part(b'<Invoice>signed content</Invoice>')

    envelope = build_envelope()
    _ = build_user_message(envelope, pmode, [part], new_message_id(), 'conversation-1')
    _ = sign_envelope(envelope, [part], keystore, pmode.security)

    out = (envelope, [part], pmode)
    return out

# ################################################################################################################################

def _reparse(envelope):
    """ Serializes and reparses an envelope, as would happen over the wire.
    """
    out = etree.fromstring(etree.tostring(envelope))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSignVerify:

    def test_sign_verify_roundtrip(self, rsa_parties):
        envelope, parts, _ = _signed_message(rsa_parties.sender)

        result = verify_envelope(_reparse(envelope), parts, rsa_parties.receiver)

        assert result.signer_certificate == rsa_parties.sender.signing_certificate

        # The messaging header, the body and the attachment are all covered.
        assert len(result.signed_references) == 3

    def test_tampered_attachment_is_detected(self, rsa_parties):
        envelope, parts, _ = _signed_message(rsa_parties.sender)

        parts[0].data = b'<Invoice>tampered content</Invoice>'

        with pytest.raises(AS4SecurityException) as exc:
            _ = verify_envelope(_reparse(envelope), parts, rsa_parties.receiver)

        assert exc.value.error_code == EbMSError.Failed_Authentication

    def test_tampered_header_is_detected(self, rsa_parties):
        envelope, parts, _ = _signed_message(rsa_parties.sender)

        # Change the action element after signing.
        wire = _reparse(envelope)
        action = wire.find(f'.//{qname(NS.EBMS, "Action")}')
        action.text = 'SomethingElse'

        with pytest.raises(AS4SecurityException) as exc:
            _ = verify_envelope(wire, parts, rsa_parties.receiver)

        assert exc.value.error_code == EbMSError.Failed_Authentication

    def test_wrong_signer_is_rejected_by_pinning(self, rsa_parties):
        # The receiver signs a message but the verifier expects the sender's certificate.
        envelope, parts, _ = _signed_message(rsa_parties.receiver)

        verifier = new_keystore()
        verifier.peer_signing_certificate = rsa_parties.sender.signing_certificate

        with pytest.raises(AS4SecurityException) as exc:
            _ = verify_envelope(_reparse(envelope), parts, verifier)

        assert exc.value.error_code == EbMSError.Failed_Authentication

    def test_trust_anchor_chain_validation(self, rsa_parties):
        envelope, parts, _ = _signed_message(rsa_parties.sender)

        # No pinned certificate - trust comes from the CA only.
        verifier = new_keystore()
        verifier.trust_anchors = [rsa_parties.ca_certificate]

        result = verify_envelope(_reparse(envelope), parts, verifier)
        assert result.signer_certificate == rsa_parties.sender.signing_certificate

    def test_unknown_ca_is_rejected(self, rsa_parties, eddsa_parties):
        envelope, parts, _ = _signed_message(rsa_parties.sender)

        # The verifier only trusts the other CA.
        verifier = new_keystore()
        verifier.trust_anchors = [eddsa_parties.ca_certificate]

        with pytest.raises(AS4SecurityException) as exc:
            _ = verify_envelope(_reparse(envelope), parts, verifier)

        assert exc.value.error_code == EbMSError.Failed_Authentication

    def test_ed25519_sign_verify_roundtrip(self, eddsa_parties):
        pmode = new_pmode()
        pmode.security.signature_algorithm = Algorithm.Ed25519

        part = new_part(b'<Doc>ed25519</Doc>')
        envelope = build_envelope()
        _ = build_user_message(envelope, pmode, [part], new_message_id(), 'conversation-1')
        _ = sign_envelope(envelope, [part], eddsa_parties.sender, pmode.security)

        result = verify_envelope(_reparse(envelope), [part], eddsa_parties.receiver)
        assert result.signer_certificate == eddsa_parties.sender.signing_certificate

# ################################################################################################################################
# ################################################################################################################################

class TestPKIPath:

    def test_pkipath_roundtrip(self, rsa_parties):
        chain = [rsa_parties.sender.signing_certificate, rsa_parties.ca_certificate]

        encoded = build_pkipath(chain)
        decoded = parse_pkipath(encoded)

        assert decoded == chain

    def test_pkipath_token_carries_the_chain(self, rsa_parties):
        # Sign with a PKIPath token that carries both the leaf and the CA.
        keystore = new_keystore()
        keystore.signing_key = rsa_parties.sender.signing_key
        keystore.signing_certificate_chain = [rsa_parties.sender.signing_certificate, rsa_parties.ca_certificate]

        envelope, parts, _ = _signed_message(keystore, TokenType.PKIPath)

        verifier = new_keystore()
        verifier.trust_anchors = [rsa_parties.ca_certificate]

        result = verify_envelope(_reparse(envelope), parts, verifier)

        assert result.signer_certificate == rsa_parties.sender.signing_certificate
        assert len(result.signer_chain) == 2

# ################################################################################################################################
# ################################################################################################################################

class TestEncryptDecrypt:

    def test_rsa_encrypt_decrypt_roundtrip(self, rsa_parties):
        pmode = new_pmode()
        part = new_part(b'<Secret>rsa suite</Secret>')

        envelope = build_envelope()
        _ = build_user_message(envelope, pmode, [part], new_message_id(), 'conversation-1')

        plaintext = part.data
        encrypt_parts(envelope, [part], rsa_parties.sender, pmode.security)

        # The wire bytes are ciphertext now.
        assert part.data != plaintext

        decrypt_parts(_reparse(envelope), [part], rsa_parties.receiver)
        assert part.data == plaintext

    def test_x25519_encrypt_decrypt_roundtrip(self, eddsa_parties):
        pmode = new_pmode()
        pmode.security.crypto_suite = CryptoSuite.EdDSA

        part = new_part(b'<Secret>eddsa suite</Secret>')

        envelope = build_envelope()
        _ = build_user_message(envelope, pmode, [part], new_message_id(), 'conversation-1')

        plaintext = part.data
        encrypt_parts(envelope, [part], eddsa_parties.sender, pmode.security)
        assert part.data != plaintext

        decrypt_parts(_reparse(envelope), [part], eddsa_parties.receiver)
        assert part.data == plaintext

    def test_wrong_key_cannot_decrypt(self, rsa_parties):
        pmode = new_pmode()
        part = new_part(b'<Secret>for the receiver only</Secret>')

        envelope = build_envelope()
        _ = build_user_message(envelope, pmode, [part], new_message_id(), 'conversation-1')
        encrypt_parts(envelope, [part], rsa_parties.sender, pmode.security)

        # The sender's own key is not the receiver's key.
        with pytest.raises(Exception):
            decrypt_parts(_reparse(envelope), [part], rsa_parties.sender)

# ################################################################################################################################
# ################################################################################################################################

# SAML 2.0 holder-of-key subject confirmation, per SAML Core 2.0 section 3.1.
_holder_of_key = 'urn:oasis:names:tc:SAML:2.0:cm:holder-of-key'

# ################################################################################################################################

def _new_holder_of_key_assertion(certificate):
    """ Builds the kind of SAML 2.0 assertion a security token service issues -
    it vouches that the subject is whoever holds the private key matching
    the certificate carried in the subject confirmation.
    """
    nsmap = {'saml2': NS.SAML2, 'ds': NS.DS}

    assertion = etree.Element(qname(NS.SAML2, 'Assertion'), nsmap=nsmap)
    assertion.set('ID', f'_{uuid4().hex}')
    assertion.set('Version', '2.0')
    assertion.set('IssueInstant', utc_timestamp())

    issuer = etree.SubElement(assertion, qname(NS.SAML2, 'Issuer'))
    issuer.text = 'https://sts.example.gov.au'

    subject = etree.SubElement(assertion, qname(NS.SAML2, 'Subject'))

    name_id = etree.SubElement(subject, qname(NS.SAML2, 'NameID'))
    name_id.text = 'reporting-party'

    confirmation = etree.SubElement(subject, qname(NS.SAML2, 'SubjectConfirmation'))
    confirmation.set('Method', _holder_of_key)

    confirmation_data = etree.SubElement(confirmation, qname(NS.SAML2, 'SubjectConfirmationData'))

    key_info = etree.SubElement(confirmation_data, qname(NS.DS, 'KeyInfo'))
    x509_data = etree.SubElement(key_info, qname(NS.DS, 'X509Data'))
    x509_certificate = etree.SubElement(x509_data, qname(NS.DS, 'X509Certificate'))
    x509_certificate.text = encode_base64(certificate.public_bytes(Encoding.DER))

    out = etree.tostring(assertion)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSAMLToken:
    """ Signatures keyed by a SAML assertion instead of a binary token - the shape
    the Australian SBR's ebMS3 exchanges use, with tokens issued by VANguard.
    """

    def _saml_keystore(self, rsa_parties):
        keystore = new_keystore()
        keystore.signing_key = rsa_parties.sender.signing_key
        keystore.signing_certificate_chain = [rsa_parties.sender.signing_certificate]
        keystore.saml_assertion = _new_holder_of_key_assertion(rsa_parties.sender.signing_certificate)

        return keystore

    def test_saml_token_sign_verify_roundtrip(self, rsa_parties):
        keystore = self._saml_keystore(rsa_parties)
        envelope, parts, _ = _signed_message(keystore, TokenType.SAML20)

        result = verify_envelope(_reparse(envelope), parts, rsa_parties.receiver)

        assert result.signer_certificate == rsa_parties.sender.signing_certificate
        assert len(result.signed_references) == 3

    def test_saml_token_reference_layout(self, rsa_parties):
        keystore = self._saml_keystore(rsa_parties)
        envelope, _, _ = _signed_message(keystore, TokenType.SAML20)

        wire = _reparse(envelope)
        security = wire.find(f'.//{qname(NS.WSSE, "Security")}')

        # The assertion itself travels in the security header, in place of a binary token.
        assertion = security.find(qname(NS.SAML2, 'Assertion'))
        assert assertion is not None
        assert security.find(qname(NS.WSSE, 'BinarySecurityToken')) is None

        # The key info names the token type and points at the assertion by its ID,
        # with the identifiers the SAML Token Profile 1.1 prescribes.
        signature = security.find(qname(NS.DS, 'Signature'))
        token_reference = signature.find(f'.//{qname(NS.WSSE, "SecurityTokenReference")}')

        token_type = token_reference.get(qname(NS.WSSE11, 'TokenType'))
        assert token_type == 'http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.1#SAMLV2.0'

        key_identifier = token_reference.find(qname(NS.WSSE, 'KeyIdentifier'))
        value_type = key_identifier.get('ValueType')
        assert value_type == 'http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.1#SAMLID'

        assert key_identifier.text == assertion.get('ID')

    def test_tampering_is_detected_with_saml_token(self, rsa_parties):
        keystore = self._saml_keystore(rsa_parties)
        envelope, parts, _ = _signed_message(keystore, TokenType.SAML20)

        parts[0].data = b'<Invoice>tampered content</Invoice>'

        with pytest.raises(AS4SecurityException) as exc:
            _ = verify_envelope(_reparse(envelope), parts, rsa_parties.receiver)

        assert exc.value.error_code == EbMSError.Failed_Authentication

    def test_missing_assertion_is_rejected_at_signing_time(self, rsa_parties):
        keystore = self._saml_keystore(rsa_parties)
        keystore.saml_assertion = None

        with pytest.raises(XMLSecurityException):
            _, _, _ = _signed_message(keystore, TokenType.SAML20)

    def test_missing_assertion_on_the_wire_is_rejected(self, rsa_parties):
        keystore = self._saml_keystore(rsa_parties)
        envelope, parts, _ = _signed_message(keystore, TokenType.SAML20)

        # Strip the assertion the signature's key identifier points at.
        wire = _reparse(envelope)
        security = wire.find(f'.//{qname(NS.WSSE, "Security")}')
        assertion = security.find(qname(NS.SAML2, 'Assertion'))
        security.remove(assertion)

        with pytest.raises(AS4SecurityException) as exc:
            _ = verify_envelope(wire, parts, rsa_parties.receiver)

        assert exc.value.error_code == EbMSError.Failed_Authentication

# ################################################################################################################################
# ################################################################################################################################
