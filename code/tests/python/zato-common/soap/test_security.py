# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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
from zato.common.util.xml_.core import qname
from zato.common.util.xml_.keystore import new_keystore

# ################################################################################################################################
# ################################################################################################################################

def _reparse(envelope):
    """ Serializes and reparses an envelope, as would happen over the wire.
    """
    out = etree.fromstring(to_bytes(envelope))
    return out

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

        verify_username_token(_reparse(envelope), 'MYUSER', 'MYPASS')

    def test_digest_wrong_password(self):
        envelope = _sample_envelope()
        _ = add_username_token(envelope, 'MYUSER', 'MYPASS', use_digest=True)

        with pytest.raises(SOAPSecurityException):
            verify_username_token(_reparse(envelope), 'MYUSER', 'WRONG')

    def test_missing_token(self):
        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            verify_username_token(envelope, 'MYUSER', 'MYPASS')

# ################################################################################################################################
# ################################################################################################################################

class TestX509:
    """ The X.509 token profile - what Peppol-style profiles and e-invoicing
    and government gateways demand from message signatures.
    """

    def test_sign_verify_roundtrip(self, parties):
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        signer = verify(_reparse(envelope), parties.receiver)

        assert signer == parties.sender.signing_certificate

    def test_tampered_body_is_detected(self, parties):
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        # Change the invoice number after signing.
        wire = _reparse(envelope)
        body = get_body(wire)
        invoice_number = body[0][0]
        invoice_number.text = 'INV-2026-9999'

        with pytest.raises(SOAPSecurityException):
            _ = verify(wire, parties.receiver)

    def test_wrong_signer_is_rejected_by_pinning(self, parties):
        # The receiver signs but the verifier expects the sender's certificate.
        envelope = _sample_envelope()
        _ = sign(envelope, parties.receiver)

        verifier = new_keystore()
        verifier.peer_signing_certificate = parties.sender.signing_certificate

        with pytest.raises(SOAPSecurityException):
            _ = verify(_reparse(envelope), verifier)

    def test_trust_anchor_chain_validation(self, parties):
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        # No pinned certificate - trust comes from the CA only.
        verifier = new_keystore()
        verifier.trust_anchors = [parties.ca_certificate]

        signer = verify(_reparse(envelope), verifier)
        assert signer == parties.sender.signing_certificate

    def test_unsigned_message_is_rejected(self, parties):
        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            _ = verify(envelope, parties.receiver)

    def test_signature_covers_a_timestamp(self, parties):
        envelope = _sample_envelope()
        _ = sign(envelope, parties.sender)

        wire = _reparse(envelope)
        timestamp = wire.find(f'.//{qname(NS.WSU, "Timestamp")}')

        assert timestamp is not None
        assert timestamp.find(qname(NS.WSU, 'Created')) is not None
        assert timestamp.find(qname(NS.WSU, 'Expires')) is not None

# ################################################################################################################################
# ################################################################################################################################

class TestBodyEncryption:
    """ XML Encryption of the SOAP body - confidentiality the way WS-Security
    mandates it for bodies rather than attachments.
    """

    def test_encrypt_decrypt_roundtrip(self, parties):
        envelope = _sample_envelope()

        encrypt_body(envelope, parties.sender)

        # The wire carries no plaintext.
        wire = to_bytes(envelope)
        assert b'INV-2026-0401' not in wire

        received = etree.fromstring(wire)
        decrypt_body(received, parties.receiver)

        body = parse_body(received)
        assert body.SubmitInvoice.InvoiceNumber == 'INV-2026-0401'

    def test_wrong_key_cannot_decrypt(self, parties):
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
