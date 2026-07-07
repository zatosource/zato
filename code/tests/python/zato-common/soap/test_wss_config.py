# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# cryptography
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.soap.common import NS, SOAPSecurityException, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, get_body, parse_body, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.wss import apply_wss, enforce_wss, keystore_from_config, Mode
from zato.common.util.xml_.core import qname

# ################################################################################################################################
# ################################################################################################################################

def _reparse(envelope):
    """ Serializes and reparses an envelope, as would happen over the wire.
    """
    out = etree.fromstring(to_bytes(envelope))
    return out

# ################################################################################################################################

def _sample_envelope():
    """ A CDC IIS style SOAP 1.2 envelope - the kind of message
    immunization gateways exchange.
    """
    request = SOAPMessage()
    request.namespace = 'urn:cdc:iisb:2011'
    request.facilityID = 'FL0001'
    request.hl7Message = 'MSH|^~\\&|MYEHR|FL0001|IIS|FLSHOTS|20260401||VXU^V04^VXU_V04|12345|P|2.5.1'

    envelope = build_envelope(SOAPVersion.V12)
    _ = attach_body(envelope, request, 'submitSingleMessage')

    return envelope

# ################################################################################################################################

def _private_key_pem(key):
    """ Serializes a private key to the PEM string a definition would keep.
    """
    pem_bytes = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())

    out = pem_bytes.decode('ascii')
    return out

# ################################################################################################################################

def _certificate_pem(certificate):
    """ Serializes a certificate to the PEM string a definition would keep.
    """
    pem_bytes = certificate.public_bytes(Encoding.PEM)

    out = pem_bytes.decode('ascii')
    return out

# ################################################################################################################################

def _sender_x509_config(parties, sign, encrypt):
    """ The config dict of an outgoing connection's X.509 definition -
    our own key material plus the other side's certificate.
    """
    out = {
        'mode': Mode.X509,
        'sign': sign,
        'encrypt': encrypt,
        'signing_key': _private_key_pem(parties.sender.signing_key),
        'signing_certificate_chain': _certificate_pem(parties.sender.signing_certificate),
        'peer_certificate': _certificate_pem(parties.receiver.signing_certificate),
    }

    return out

# ################################################################################################################################

def _receiver_x509_config(parties, sign, encrypt):
    """ The config dict of a channel's X.509 definition - our own decryption key
    plus the sender's pinned certificate.
    """
    out = {
        'mode': Mode.X509,
        'sign': sign,
        'encrypt': encrypt,
        'decryption_key': _private_key_pem(parties.receiver.decryption_key),
        'peer_certificate': _certificate_pem(parties.sender.signing_certificate),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestKeystoreFromConfig:
    """ PEM strings out of a plain config dict - the exact shape the server keeps in RAM.
    """

    def test_all_fields(self, parties):
        config = {
            'signing_key': _private_key_pem(parties.sender.signing_key),
            'signing_certificate_chain': _certificate_pem(parties.sender.signing_certificate),
            'decryption_key': _private_key_pem(parties.sender.decryption_key),
            'peer_certificate': _certificate_pem(parties.receiver.signing_certificate),
            'trust_anchors': _certificate_pem(parties.ca_certificate),
        }

        keystore = keystore_from_config(config)

        assert keystore.signing_key is not None
        assert keystore.signing_certificate == parties.sender.signing_certificate
        assert keystore.decryption_key is not None

        # One peer certificate serves both encryption and signature pinning.
        assert keystore.peer_encryption_certificate == parties.receiver.signing_certificate
        assert keystore.peer_signing_certificate == parties.receiver.signing_certificate

        assert keystore.trust_anchors == [parties.ca_certificate]

    def test_empty_config(self):
        keystore = keystore_from_config({})

        assert keystore.signing_key is None
        assert keystore.signing_certificate_chain == []
        assert keystore.decryption_key is None
        assert keystore.peer_encryption_certificate is None
        assert keystore.peer_signing_certificate is None
        assert keystore.trust_anchors == []

# ################################################################################################################################
# ################################################################################################################################

class TestUsernameTokenMode:
    """ The UsernameToken mode - text and digest passwords, driven by config dicts.
    """

    def test_text_roundtrip(self):
        config = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS', 'use_digest': False}

        envelope = _sample_envelope()
        apply_wss(envelope, config)

        enforce_wss(_reparse(envelope), config)

    def test_digest_roundtrip(self):
        config = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS', 'use_digest': True}

        envelope = _sample_envelope()
        apply_wss(envelope, config)

        # The digest form never carries the password itself.
        wire = to_bytes(envelope)
        assert b'MYPASS' not in wire

        enforce_wss(etree.fromstring(wire), config)

    def test_wrong_password_is_rejected(self):
        sender_config = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'WRONG', 'use_digest': False}
        channel_config = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS', 'use_digest': False}

        envelope = _sample_envelope()
        apply_wss(envelope, sender_config)

        with pytest.raises(SOAPSecurityException):
            enforce_wss(_reparse(envelope), channel_config)

    def test_missing_header_is_rejected(self):
        config = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS', 'use_digest': False}

        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            enforce_wss(envelope, config)

# ################################################################################################################################
# ################################################################################################################################

class TestX509Mode:
    """ The X.509 mode - signatures and body encryption out of PEM config material.
    """

    def test_sign_verify_roundtrip(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _sender_x509_config(parties, sign=True, encrypt=False))

        enforce_wss(_reparse(envelope), _receiver_x509_config(parties, sign=True, encrypt=False))

    def test_sign_and_encrypt_roundtrip(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _sender_x509_config(parties, sign=True, encrypt=True))

        # The wire carries no plaintext.
        wire = to_bytes(envelope)
        assert b'FL0001' not in wire

        received = etree.fromstring(wire)
        enforce_wss(received, _receiver_x509_config(parties, sign=True, encrypt=True))

        # After enforcement the body reads back in the clear.
        body = parse_body(received)
        assert body.submitSingleMessage.facilityID == 'FL0001'

    def test_encrypt_only_roundtrip(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _sender_x509_config(parties, sign=False, encrypt=True))

        received = _reparse(envelope)
        enforce_wss(received, _receiver_x509_config(parties, sign=False, encrypt=True))

        body = parse_body(received)
        assert body.submitSingleMessage.facilityID == 'FL0001'

    def test_tampered_body_is_rejected(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _sender_x509_config(parties, sign=True, encrypt=False))

        # Change the facility ID after signing.
        wire = _reparse(envelope)
        body = get_body(wire)
        facility_id = body[0][0]
        facility_id.text = 'FL9999'

        with pytest.raises(SOAPSecurityException):
            enforce_wss(wire, _receiver_x509_config(parties, sign=True, encrypt=False))

    def test_untrusted_signer_is_rejected(self, parties):
        # The receiver signs but the channel's definition pins the sender's certificate.
        signer_config = {
            'mode': Mode.X509,
            'sign': True,
            'encrypt': False,
            'signing_key': _private_key_pem(parties.receiver.signing_key),
            'signing_certificate_chain': _certificate_pem(parties.receiver.signing_certificate),
        }

        envelope = _sample_envelope()
        apply_wss(envelope, signer_config)

        with pytest.raises(SOAPSecurityException):
            enforce_wss(_reparse(envelope), _receiver_x509_config(parties, sign=True, encrypt=False))

    def test_trust_anchor_chain_validation(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _sender_x509_config(parties, sign=True, encrypt=False))

        # No pinned certificate - trust comes from the CA only.
        channel_config = {
            'mode': Mode.X509,
            'sign': True,
            'encrypt': False,
            'trust_anchors': _certificate_pem(parties.ca_certificate),
        }

        enforce_wss(_reparse(envelope), channel_config)

    def test_unsigned_message_is_rejected(self, parties):
        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            enforce_wss(envelope, _receiver_x509_config(parties, sign=True, encrypt=False))

# ################################################################################################################################
# ################################################################################################################################

class TestSAMLMode:
    """ The SAML mode - XUA-style assertions with attributes and an audience.
    """

    def test_roundtrip_with_attributes_and_audience(self):
        sender_config = {
            'mode': Mode.SAML,
            'issuer': 'urn:qhin:example',
            'subject': 'CN=Dr Smith,O=Example Hospital',
            'audience': 'urn:qhin:other',
            'attributes': {
                'urn:oasis:names:tc:xspa:1.0:subject:organization': 'Example Hospital',
                'urn:oasis:names:tc:xacml:2.0:subject:role': '224608005',
            },
        }
        channel_config = {'mode': Mode.SAML, 'issuer': 'urn:qhin:example'}

        envelope = _sample_envelope()
        apply_wss(envelope, sender_config)

        received = _reparse(envelope)
        enforce_wss(received, channel_config)

        # The role and organization travel as assertion attributes.
        attributes = received.findall(f'.//{qname(NS.SAML2, "Attribute")}')
        assert len(attributes) == 2
        assert attributes[1].get('Name') == 'urn:oasis:names:tc:xacml:2.0:subject:role'

        # The audience restriction names the other side.
        audience = received.find(f'.//{qname(NS.SAML2, "Audience")}')
        assert audience.text == 'urn:qhin:other'

    def test_wrong_issuer_is_rejected(self):
        sender_config = {'mode': Mode.SAML, 'issuer': 'urn:idp:untrusted', 'subject': 'user@example.gov'}
        channel_config = {'mode': Mode.SAML, 'issuer': 'urn:qhin:example'}

        envelope = _sample_envelope()
        apply_wss(envelope, sender_config)

        with pytest.raises(SOAPSecurityException):
            enforce_wss(_reparse(envelope), channel_config)

    def test_missing_assertion_is_rejected(self):
        channel_config = {'mode': Mode.SAML, 'issuer': 'urn:qhin:example'}

        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            enforce_wss(envelope, channel_config)

# ################################################################################################################################
# ################################################################################################################################

class TestUnknownMode:
    """ A definition whose mode is not one the server recognizes.
    """

    def test_apply_unknown_mode(self):
        config = {'mode': 'kerberos'}

        with pytest.raises(SOAPSecurityException):
            apply_wss(_sample_envelope(), config)

    def test_enforce_unknown_mode(self):
        config = {'mode': 'kerberos'}

        with pytest.raises(SOAPSecurityException):
            enforce_wss(_sample_envelope(), config)

# ################################################################################################################################
# ################################################################################################################################
