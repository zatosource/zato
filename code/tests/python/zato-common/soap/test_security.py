# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.soap.common import NS, SOAPSecurityException, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, get_body, parse_body, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.saml import add_assertion, add_attribute, get_assertion, new_assertion
from zato.common.soap.security.usernametoken import add_username_token, verify_username_token
from zato.common.soap.security.x509 import decrypt_body, encrypt_body, sign, verify
from zato.common.util.xml_.constants import Algorithm
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.keystore import new_keystore
from zato.common.util.xml_.signature import compute_signature_value
from zato.common.util.xml_.xmlsec import encode_base64
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _reparse(envelope:'any_'):
    """ Serializes and reparses an envelope, as would happen over the wire.
    """
    out = etree.fromstring(to_bytes(envelope))
    return out

# ################################################################################################################################

def _drop_reference(envelope:'any_', element_id:'any_'):
    """ Removes one ds:Reference from an envelope's SignedInfo, narrowing what the signature says
    it covers.
    """
    signed_info = envelope.find(f'.//{qname(NS.DS, "SignedInfo")}')

    for reference in signed_info.findall(qname(NS.DS, 'Reference')):
        if reference.get('URI') == f'#{element_id}':
            signed_info.remove(reference)

# ################################################################################################################################

def _resign(envelope:'any_', keystore:'any_'):
    """ Recomputes an envelope's signature value over its SignedInfo as it now stands.

    This is what a sender holding a trusted key does when it chooses to cover less than it should,
    so a test using it produces a message that is genuinely and correctly signed - which is the only
    way to show that a coverage rule, rather than a broken signature value, is what refuses it.
    """
    signature = envelope.find(f'.//{qname(NS.DS, "Signature")}')
    signed_info = signature.find(qname(NS.DS, 'SignedInfo'))

    signature_bytes = compute_signature_value(signed_info, keystore, Algorithm.RSA_SHA256)

    signature_value = signature.find(qname(NS.DS, 'SignatureValue'))
    signature_value.text = encode_base64(signature_bytes)

# ################################################################################################################################

def _sample_envelope():
    """ A SOAP 1.2 envelope with a small business body.
    """
    request = SOAPMessage()
    request.namespace = 'urn:example:invoicing'
    request.InvoiceNumber = 'INV-2026-0401'

    envelope = build_envelope(SOAPVersion.V12)
    _ = attach_body(envelope, request, 'SubmitInvoice')

    return envelope

# ################################################################################################################################
# ################################################################################################################################

class TestUsernameToken:
    """ The UsernameToken profile - the simplest credential scheme,
    used by legacy gateways that predate X.509 profiles.
    """

    def test_plaintext_roundtrip(self):
        envelope = _sample_envelope()
        _ = add_username_token(envelope, 'MYUSER', 'MYPASS')

        verify_username_token(_reparse(envelope), 'MYUSER', 'MYPASS')

    def test_plaintext_wrong_password(self):
        envelope = _sample_envelope()
        _ = add_username_token(envelope, 'MYUSER', 'MYPASS')

        with pytest.raises(SOAPSecurityException):
            verify_username_token(_reparse(envelope), 'MYUSER', 'WRONG')

    def test_digest_roundtrip(self):
        envelope = _sample_envelope()
        _ = add_username_token(envelope, 'MYUSER', 'MYPASS', use_digest=True)

        # The digest form never carries the password itself.
        wire = to_bytes(envelope)
        assert b'MYPASS' not in wire

        verify_username_token(_reparse(envelope), 'MYUSER', 'MYPASS', use_digest=True)

    def test_digest_wrong_password(self):
        envelope = _sample_envelope()
        _ = add_username_token(envelope, 'MYUSER', 'MYPASS', use_digest=True)

        with pytest.raises(SOAPSecurityException):
            verify_username_token(_reparse(envelope), 'MYUSER', 'WRONG', use_digest=True)

    def test_missing_token(self):
        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            verify_username_token(envelope, 'MYUSER', 'MYPASS')

    def test_wrong_username(self):
        envelope = _sample_envelope()
        _ = add_username_token(envelope, 'WRONGUSER', 'MYPASS')

        with pytest.raises(SOAPSecurityException):
            verify_username_token(_reparse(envelope), 'MYUSER', 'MYPASS')

    def test_wrong_username_correct_password(self):
        envelope = _sample_envelope()
        _ = add_username_token(envelope, 'WRONGUSER', 'MYPASS', use_digest=True)

        with pytest.raises(SOAPSecurityException):
            verify_username_token(_reparse(envelope), 'MYUSER', 'MYPASS', use_digest=True)

    def test_wrong_username_and_wrong_password_same_message(self):
        envelope_wrong_username = _sample_envelope()
        _ = add_username_token(envelope_wrong_username, 'WRONGUSER', 'MYPASS')

        envelope_wrong_password = _sample_envelope()
        _ = add_username_token(envelope_wrong_password, 'MYUSER', 'WRONGPASS')

        with pytest.raises(SOAPSecurityException) as wrong_username_info:
            verify_username_token(_reparse(envelope_wrong_username), 'MYUSER', 'MYPASS')

        with pytest.raises(SOAPSecurityException) as wrong_password_info:
            verify_username_token(_reparse(envelope_wrong_password), 'MYUSER', 'MYPASS')

        # Neither failure may reveal which part was wrong.
        assert str(wrong_username_info.value) == str(wrong_password_info.value)

# ################################################################################################################################
# ################################################################################################################################

class TestX509:
    """ The X.509 token profile - what Peppol-style profiles and e-invoicing
    and government gateways demand from message signatures.
    """

    def test_sign_verify_roundtrip(self, parties:'any_'):
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        verified = verify(_reparse(envelope), parties.receiver)

        assert verified.certificate == parties.sender.signing_certificate

    def test_tampered_body_is_detected(self, parties:'any_'):
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        # Change the invoice number after signing.
        wire = _reparse(envelope)
        body = get_body(wire)
        invoice_number = body[0][0]
        invoice_number.text = 'INV-2026-9999'

        with pytest.raises(SOAPSecurityException):
            _ = verify(wire, parties.receiver)

    def test_wrong_signer_is_rejected_by_pinning(self, parties:'any_'):
        # The receiver signs but the verifier expects the sender's certificate.
        envelope = _sample_envelope()
        _ = sign(envelope, parties.receiver)

        verifier = new_keystore()
        verifier.peer_signing_certificate = parties.sender.signing_certificate

        with pytest.raises(SOAPSecurityException):
            _ = verify(_reparse(envelope), verifier)

    def test_trust_anchor_chain_validation(self, parties:'any_'):
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        # No pinned certificate - trust comes from the CA only.
        verifier = new_keystore()
        verifier.trust_anchors = [parties.ca_certificate]

        verified = verify(_reparse(envelope), verifier)
        assert verified.certificate == parties.sender.signing_certificate

    def test_unsigned_message_is_rejected(self, parties:'any_'):
        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            _ = verify(envelope, parties.receiver)

    def test_signature_covers_a_timestamp(self, parties:'any_'):
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        timestamp = wire.find(f'.//{qname(NS.WSU, "Timestamp")}')

        assert timestamp is not None
        assert timestamp.find(qname(NS.WSU, 'Created')) is not None
        assert timestamp.find(qname(NS.WSU, 'Expires')) is not None

# ################################################################################################################################
# ################################################################################################################################

class TestSignatureWrapping:
    """ XML Signature Wrapping - the attack that makes a signature verify against one element while
    the receiver processes another.

    Every case here produces a message whose signature is mathematically valid over content the
    sender really did sign. What makes them attacks is that the element the receiver would go on to
    process is a different one, so a verifier that reports only pass or fail is not enough - it has
    to say what it verified, and the caller has to check that against what it uses.
    """

    def test_a_relocated_signed_body_is_refused(self, parties:'any_'):
        # The classic form. The signed body is moved somewhere the receiver does not read from and an
        # attacker-authored body takes its place, keeping the original's id so the reference still
        # resolves to genuinely signed content.
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        body = get_body(wire)
        signed_id = body.get(qname(NS.WSU, 'Id'))

        # The signed body is parked inside the security header, where a naive receiver never looks ..
        signed_copy = deepcopy(body)
        security = cast_('any_', wire.find(f'.//{qname(NS.WSSE, "Security")}'))
        security.append(signed_copy)

        # .. and what remains in the body's place is the attacker's content under the same id.
        for child in list(body):
            body.remove(child)

        forged = etree.SubElement(body, '{urn:example:invoicing}SubmitInvoice')
        invoice_number = etree.SubElement(forged, '{urn:example:invoicing}InvoiceNumber')
        invoice_number.text = 'INV-2026-9999'

        # Two elements now claim the same id, which is what the index refuses - a reference that
        # resolves to either of two elements resolves to neither.
        assert signed_copy.get(qname(NS.WSU, 'Id')) == signed_id

        with pytest.raises(SOAPSecurityException) as e:
            _ = verify(wire, parties.receiver)

        assert 'is carried by 2 elements' in str(e.value)

    def test_a_duplicate_id_is_refused_on_its_own(self, parties:'any_'):
        # No relocation at all, just a second element carrying the same id as the signed body. The
        # ambiguity is the vulnerability - which of the two a reference points at is then a matter
        # of which one the resolver happens to find first.
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        body = get_body(wire)
        signed_id = body.get(qname(NS.WSU, 'Id'))

        security = cast_('any_', wire.find(f'.//{qname(NS.WSSE, "Security")}'))
        decoy = etree.SubElement(security, '{urn:example:invoicing}Decoy')
        decoy.set(qname(NS.WSU, 'Id'), signed_id)

        with pytest.raises(SOAPSecurityException) as e:
            _ = verify(wire, parties.receiver)

        assert 'is carried by 2 elements' in str(e.value)

    def test_the_verified_body_is_the_processed_body(self, parties:'any_'):
        # The property the whole defence rests on. What comes back names the element that was
        # verified, so a caller can hold it against the body it is about to process rather than
        # trusting that a pass means the right thing was covered.
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        verified = verify(wire, parties.receiver)

        # Identity, not equality - an element that merely looks like the body is not the body.
        assert verified.body is get_body(wire)
        assert any(element is get_body(wire) for element in verified.elements)

    def test_a_second_signature_is_refused(self, parties:'any_'):
        # With two signatures there is no way to report which of them covered a given element, so a
        # receiver would have to guess, and an attacker gets to choose what the second one covers.
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        security = cast_('any_', wire.find(f'.//{qname(NS.WSSE, "Security")}'))
        signature = security.find(qname(NS.DS, 'Signature'))
        security.append(deepcopy(signature))

        with pytest.raises(SOAPSecurityException) as e:
            _ = verify(wire, parties.receiver)

        assert '2 signatures' in str(e.value)

# ################################################################################################################################
# ################################################################################################################################

class TestSignatureCoverage:
    """ What a signature has to cover before the message it protects is worth acting on.

    A sender's own SignedInfo says what it signed, so leaving that choice entirely to the sender
    means a signature over nothing much verifies perfectly well while the parts that matter travel
    unprotected. Each case here narrows the reference set and then re-signs with the sender's real
    key, so the message is genuinely signed by a certificate the receiver trusts and the only thing
    wrong with it is what it leaves out.
    """

    def test_a_signature_that_omits_the_body_is_refused(self, parties:'any_'):
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        body_id = get_body(wire).get(qname(NS.WSU, 'Id'))

        _drop_reference(wire, body_id)
        _resign(wire, parties.sender)

        with pytest.raises(SOAPSecurityException) as e:
            _ = verify(wire, parties.receiver)

        assert 'does not cover the SOAP body' in str(e.value)

    def test_a_signature_that_omits_the_timestamp_is_refused(self, parties:'any_'):
        # An uncovered timestamp says whatever the sender wants it to say, so a message whose
        # validity window is not signed has no validity window at all and could be replayed
        # indefinitely.
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        timestamp = cast_('any_', wire.find(f'.//{qname(NS.WSU, "Timestamp")}'))
        timestamp_id = timestamp.get(qname(NS.WSU, 'Id'))

        _drop_reference(wire, timestamp_id)
        _resign(wire, parties.sender)

        with pytest.raises(SOAPSecurityException) as e:
            _ = verify(wire, parties.receiver)

        assert 'does not cover a Timestamp' in str(e.value)

    def test_narrowing_the_reference_set_without_resigning_is_refused(self, parties:'any_'):
        # Without the sender's key an attacker can still delete a reference, and then the signature
        # value no longer matches the SignedInfo it covers. This is the case the coverage check is
        # not needed for, and it is here to show the two defences are independent.
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        body_id = get_body(wire).get(qname(NS.WSU, 'Id'))

        _drop_reference(wire, body_id)

        with pytest.raises(SOAPSecurityException) as e:
            _ = verify(wire, parties.receiver)

        assert 'Signature value does not verify' in str(e.value)

# ################################################################################################################################
# ################################################################################################################################

class TestBodyEncryption:
    """ XML Encryption of the SOAP body - confidentiality the way WS-Security
    mandates it for bodies rather than attachments.
    """

    def test_encrypt_decrypt_roundtrip(self, parties:'any_'):
        envelope = _sample_envelope()

        encrypt_body(envelope, parties.sender)

        # The wire carries no plaintext.
        wire = to_bytes(envelope)
        assert b'INV-2026-0401' not in wire

        received = etree.fromstring(wire)
        decrypt_body(received, parties.receiver)

        body = parse_body(received)
        assert body.SubmitInvoice.InvoiceNumber == 'INV-2026-0401'

    def test_wrong_key_cannot_decrypt(self, parties:'any_'):
        envelope = _sample_envelope()
        encrypt_body(envelope, parties.sender)

        # The sender's own key is not the receiver's key.
        with pytest.raises(Exception):
            decrypt_body(_reparse(envelope), parties.sender)

# ################################################################################################################################
# ################################################################################################################################

class TestSAML:
    """ SAML 2.0 assertions - the IHE XUA profile that TEFCA and eHealth Exchange
    require for user authentication, and the SBR ebMS3 token scheme.
    """

    def test_assertion_in_security_header(self):
        envelope = _sample_envelope()

        assertion = new_assertion('urn:qhin:example', 'CN=Dr Smith,O=Example Hospital')
        add_assertion(envelope, assertion)

        received = get_assertion(_reparse(envelope))

        issuer = received.find(qname(NS.SAML2, 'Issuer'))
        assert issuer.text == 'urn:qhin:example'

        name_id = received.find(f'.//{qname(NS.SAML2, "NameID")}')
        assert name_id.text == 'CN=Dr Smith,O=Example Hospital'

    def test_xua_style_attributes(self):
        # IHE XUA carries the user's role and organization as SAML attributes.
        assertion = new_assertion('urn:qhin:example', 'CN=Dr Smith', audience='urn:qhin:other')

        add_attribute(assertion, 'urn:oasis:names:tc:xspa:1.0:subject:organization', 'Example Hospital')
        add_attribute(assertion, 'urn:oasis:names:tc:xacml:2.0:subject:role', '224608005')

        statements = assertion.findall(qname(NS.SAML2, 'AttributeStatement'))
        assert len(statements) == 1

        attributes = statements[0].findall(qname(NS.SAML2, 'Attribute'))
        assert len(attributes) == 2
        assert attributes[1].get('Name') == 'urn:oasis:names:tc:xacml:2.0:subject:role'

        audience = assertion.find(f'.//{qname(NS.SAML2, "Audience")}')
        assert audience.text == 'urn:qhin:other'

    def test_external_assertion_bytes(self):
        # An assertion issued by an external identity provider arrives as bytes.
        external = new_assertion('urn:idp:example', 'user@example.gov')
        external_bytes = etree.tostring(external)

        envelope = _sample_envelope()
        add_assertion(envelope, external_bytes)

        received = get_assertion(_reparse(envelope))
        issuer = received.find(qname(NS.SAML2, 'Issuer'))

        assert issuer.text == 'urn:idp:example'

    def test_missing_assertion(self):
        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            _ = get_assertion(envelope)

# ################################################################################################################################
# ################################################################################################################################
