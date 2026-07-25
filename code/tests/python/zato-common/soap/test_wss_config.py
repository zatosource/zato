# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone

# lxml
from lxml import etree

# pytest
import pytest

# Zato
from zato.common.soap.common import NS, SOAPSecurityException, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, get_body, parse_body, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.saml import Assertion_TTL_Seconds, sign_assertion
from zato.common.soap.security.wss import apply_wss, enforce_wss, keystore_from_config, Mode
from zato.common.util.xml_.core import qname, to_timestamp

# ################################################################################################################################

from certs import certificate_pem_path, private_key_pem_path

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

def _sender_x509_config(parties, sign, encrypt):
    """ The config dict of an outgoing connection's X.509 definition -
    paths to our own key material plus the other side's certificate.
    """
    out = {
        'mode': Mode.X509,
        'sign': sign,
        'encrypt': encrypt,
        'signing_key': private_key_pem_path(parties.sender.signing_key),
        'signing_certificate_chain': certificate_pem_path(parties.sender.signing_certificate),
        'peer_certificate': certificate_pem_path(parties.receiver.signing_certificate),
    }

    return out

# ################################################################################################################################

def _receiver_x509_config(parties, sign, encrypt):
    """ The config dict of a channel's X.509 definition - paths to our own decryption key
    plus the sender's pinned certificate.
    """
    out = {
        'mode': Mode.X509,
        'sign': sign,
        'encrypt': encrypt,
        'decryption_key': private_key_pem_path(parties.receiver.decryption_key),
        'peer_certificate': certificate_pem_path(parties.sender.signing_certificate),
    }

    return out

# ################################################################################################################################

def _sender_saml_config(parties, issuer='urn:qhin:example', audience=None):
    """ The config dict of an outgoing connection's SAML definition - an XUA-style assertion
    signed with our own key.
    """
    out = {
        'mode': Mode.SAML,
        'issuer': issuer,
        'subject': 'CN=Dr Smith,O=Example Hospital',
        'sign': True,
        'signing_key': private_key_pem_path(parties.sender.signing_key),
        'signing_certificate_chain': certificate_pem_path(parties.sender.signing_certificate),
        'attributes': {
            'urn:oasis:names:tc:xspa:1.0:subject:organization': 'Example Hospital',
            'urn:oasis:names:tc:xacml:2.0:subject:role': '224608005',
        },
    }

    if audience:
        out['audience'] = audience

    return out

# ################################################################################################################################

def _receiver_saml_config(parties, issuer='urn:qhin:example', audience=None):
    """ The config dict of a channel's SAML definition - the issuer it expects and the CA the
    issuer's signing certificate has to chain to.
    """
    out = {
        'mode': Mode.SAML,
        'issuer': issuer,
        'trust_anchors': certificate_pem_path(parties.ca_certificate),
    }

    if audience:
        out['audience'] = audience

    return out

# ################################################################################################################################

def _reissue_assertion_window(assertion, parties, seconds_ago):
    """ Moves an assertion's validity window into the past and re-signs it, which is what an
    issuer with a badly-set clock produces and what a captured assertion looks like once its
    window has closed.
    """
    now = datetime.now(timezone.utc)
    not_before = now - timedelta(seconds=seconds_ago)
    not_on_or_after = not_before + timedelta(seconds=Assertion_TTL_Seconds)

    conditions = assertion.find(qname(NS.SAML2, 'Conditions'))
    conditions.set('NotBefore', to_timestamp(not_before))
    conditions.set('NotOnOrAfter', to_timestamp(not_on_or_after))

    # The old signature covered the old window, so it has to go before the new one is computed.
    signature = assertion.find(qname(NS.DS, 'Signature'))
    assertion.remove(signature)

    keystore = keystore_from_config({
        'signing_key': private_key_pem_path(parties.sender.signing_key),
        'signing_certificate_chain': certificate_pem_path(parties.sender.signing_certificate),
    })

    _ = sign_assertion(assertion, keystore)

# ################################################################################################################################
# ################################################################################################################################

class TestKeystoreFromConfig:
    """ PEM files out of a plain config dict of paths - the exact shape the server keeps in RAM.
    """

    def test_all_fields(self, parties):
        config = {
            'signing_key': private_key_pem_path(parties.sender.signing_key),
            'signing_certificate_chain': certificate_pem_path(parties.sender.signing_certificate),
            'decryption_key': private_key_pem_path(parties.sender.decryption_key),
            'peer_certificate': certificate_pem_path(parties.receiver.signing_certificate),
            'trust_anchors': certificate_pem_path(parties.ca_certificate),
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

    def test_a_definition_without_the_digest_flag_uses_clear_text(self):
        # The flag is an optional field kept in a definition's opaque attributes, so a definition
        # written without it - which an enmasse YAML definition for a plaintext password naturally
        # is - simply has no such key. Reading it directly used to raise a KeyError, and since only
        # a security failure is caught on the channel path, the caller saw a 500 on every request
        # instead of being authenticated. Absent means clear text, which is what the UsernameToken
        # profile itself reads an absent password type as.
        config = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS'}

        envelope = _sample_envelope()
        apply_wss(envelope, config)

        enforce_wss(_reparse(envelope), config)

    def test_a_definition_without_the_digest_flag_still_refuses_a_wrong_password(self):
        sender_config = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'WRONG'}
        channel_config = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS'}

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
    """ The X.509 mode - signatures and body encryption out of the PEM files the config points to.
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
            'signing_key': private_key_pem_path(parties.receiver.signing_key),
            'signing_certificate_chain': certificate_pem_path(parties.receiver.signing_certificate),
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
            'trust_anchors': certificate_pem_path(parties.ca_certificate),
        }

        enforce_wss(_reparse(envelope), channel_config)

    def test_unsigned_message_is_rejected(self, parties):
        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            enforce_wss(envelope, _receiver_x509_config(parties, sign=True, encrypt=False))

# ################################################################################################################################
# ################################################################################################################################

class TestTrustMaterial:
    """ A definition with signature verification enabled and nothing to verify against.

    The signer's certificate travels inside the message being verified, so a definition holding
    neither trust anchors nor a pinned peer certificate has nothing to check it against, and a
    verifier that carried on regardless would accept any self-signed certificate an attacker cared
    to generate. What it would then report is that somebody signed something, which is not the
    question a signature is asked.
    """

    def test_a_definition_with_no_trust_material_refuses_a_signed_message(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _sender_x509_config(parties, sign=True, encrypt=False))

        # Signature verification is on, and there is nothing configured to establish trust with.
        channel_config = {
            'mode': Mode.X509,
            'sign': True,
            'encrypt': False,
        }

        with pytest.raises(SOAPSecurityException) as e:
            enforce_wss(_reparse(envelope), channel_config)

        assert 'No trust anchors and no pinned peer certificate' in str(e.value)

    def test_a_self_signed_certificate_is_not_accepted_in_place_of_trust(self, parties):
        # The attack the rule exists for. An attacker signs with a certificate it generated itself
        # and attaches it to the message, so the signature is internally consistent and verifies
        # against the key it travels with.
        attacker_config = {
            'mode': Mode.X509,
            'sign': True,
            'encrypt': False,
            'signing_key': private_key_pem_path(parties.receiver.signing_key),
            'signing_certificate_chain': certificate_pem_path(parties.receiver.signing_certificate),
        }

        envelope = _sample_envelope()
        apply_wss(envelope, attacker_config)

        channel_config = {
            'mode': Mode.X509,
            'sign': True,
            'encrypt': False,
        }

        with pytest.raises(SOAPSecurityException):
            enforce_wss(_reparse(envelope), channel_config)

    def test_trust_anchors_alone_are_enough(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _sender_x509_config(parties, sign=True, encrypt=False))

        channel_config = {
            'mode': Mode.X509,
            'sign': True,
            'encrypt': False,
            'trust_anchors': certificate_pem_path(parties.ca_certificate),
        }

        enforce_wss(_reparse(envelope), channel_config)

    def test_a_pinned_certificate_alone_is_enough(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _sender_x509_config(parties, sign=True, encrypt=False))

        channel_config = {
            'mode': Mode.X509,
            'sign': True,
            'encrypt': False,
            'peer_certificate': certificate_pem_path(parties.sender.signing_certificate),
        }

        enforce_wss(_reparse(envelope), channel_config)

    def test_encryption_without_verification_needs_no_trust_material(self, parties):
        # An encrypt-only definition verifies no signature, so it has nothing to establish trust
        # for and must not be refused for lacking the means to do it.
        envelope = _sample_envelope()
        apply_wss(envelope, _sender_x509_config(parties, sign=False, encrypt=True))

        received = _reparse(envelope)
        enforce_wss(received, _receiver_x509_config(parties, sign=False, encrypt=True))

        body = parse_body(received)
        assert body.submitSingleMessage.facilityID == 'FL0001'

# ################################################################################################################################
# ################################################################################################################################

class TestSAMLMode:
    """ The SAML mode - XUA-style assertions with attributes and an audience.
    """

    def test_roundtrip_with_attributes_and_audience(self, parties):
        sender_config = _sender_saml_config(parties, audience='urn:qhin:other')
        channel_config = _receiver_saml_config(parties, audience='urn:qhin:other')

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

    def test_wrong_issuer_is_rejected(self, parties):
        sender_config = _sender_saml_config(parties, issuer='urn:idp:untrusted')
        channel_config = _receiver_saml_config(parties)

        envelope = _sample_envelope()
        apply_wss(envelope, sender_config)

        with pytest.raises(SOAPSecurityException):
            enforce_wss(_reparse(envelope), channel_config)

    def test_missing_assertion_is_rejected(self, parties):
        channel_config = _receiver_saml_config(parties)

        envelope = _sample_envelope()

        with pytest.raises(SOAPSecurityException):
            enforce_wss(envelope, channel_config)

    def test_unsigned_assertion_is_rejected(self, parties):
        """ The Issuer is a string the sender writes, so an unsigned assertion proves nothing
        and has to be refused however the channel is configured.
        """
        sender_config = _sender_saml_config(parties)
        del sender_config['sign']

        channel_config = _receiver_saml_config(parties)

        envelope = _sample_envelope()
        apply_wss(envelope, sender_config)

        with pytest.raises(SOAPSecurityException):
            enforce_wss(_reparse(envelope), channel_config)

    def test_assertion_for_another_audience_is_rejected(self, parties):
        """ An assertion minted for a different service is valid, just not addressed to us.
        """
        sender_config = _sender_saml_config(parties, audience='urn:qhin:somebody-else')
        channel_config = _receiver_saml_config(parties, audience='urn:qhin:us')

        envelope = _sample_envelope()
        apply_wss(envelope, sender_config)

        with pytest.raises(SOAPSecurityException):
            enforce_wss(_reparse(envelope), channel_config)

    def test_assertion_without_audience_restriction_is_rejected(self, parties):
        """ A channel that names an audience will not take an assertion that restricts none.
        """
        sender_config = _sender_saml_config(parties)
        channel_config = _receiver_saml_config(parties, audience='urn:qhin:us')

        envelope = _sample_envelope()
        apply_wss(envelope, sender_config)

        with pytest.raises(SOAPSecurityException):
            enforce_wss(_reparse(envelope), channel_config)

    def test_expired_assertion_is_rejected(self, parties):
        """ An assertion whose validity window has closed is a captured credential.
        """
        sender_config = _sender_saml_config(parties)
        channel_config = _receiver_saml_config(parties)

        envelope = _sample_envelope()
        apply_wss(envelope, sender_config)

        # Move the window into the past, after signing, so what fails is the expiry rather than
        # the signature - Conditions are attributes on an element the signature does cover, so
        # the assertion is re-signed over its new shape.
        received = _reparse(envelope)
        assertion = received.find(f'.//{qname(NS.SAML2, "Assertion")}')
        _reissue_assertion_window(assertion, parties, seconds_ago=Assertion_TTL_Seconds * 10)

        with pytest.raises(SOAPSecurityException):
            enforce_wss(received, channel_config)

    def test_replayed_assertion_is_rejected(self, parties):
        """ An assertion is a bearer credential for the length of its window, so it is accepted
        once and once only.
        """
        sender_config = _sender_saml_config(parties)
        channel_config = _receiver_saml_config(parties)

        envelope = _sample_envelope()
        apply_wss(envelope, sender_config)

        wire = to_bytes(envelope)

        enforce_wss(etree.fromstring(wire), channel_config)

        with pytest.raises(SOAPSecurityException):
            enforce_wss(etree.fromstring(wire), channel_config)

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
