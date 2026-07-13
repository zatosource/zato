# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode, b64encode
from copy import deepcopy
from hashlib import sha1, sha256

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP, PKCS1v15
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import Encoding

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.wss import apply_wss, Mode

# ################################################################################################################################

from certs import certificate_pem_path, private_key_pem_path

# ################################################################################################################################
# ################################################################################################################################

# Every namespace and identifier below is typed out literally from the governing
# specification, never imported from the code under test - the expected values
# come from the specs, the actual ones from the wire.

# WS-Security 1.0 (OASIS Standard 200401)
_wsse = '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}'
_wsu  = '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}'

# XML Signature (W3C) and XML Encryption 1.0/1.1 (W3C)
_dsig   = '{http://www.w3.org/2000/09/xmldsig#}'
_xenc   = '{http://www.w3.org/2001/04/xmlenc#}'
_xenc11 = '{http://www.w3.org/2009/xmlenc11#}'

# SAML 2.0 (OASIS Standard 200503)
_saml2 = '{urn:oasis:names:tc:SAML:2.0:assertion}'

# UsernameToken Profile 1.0, section 4 - the Type values of wsse:Password
# and the EncodingType of wsse:Nonce.
_password_text_uri   = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'
_password_digest_uri = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest'
_nonce_encoding_uri  = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary'

# X.509 Token Profile 1.0, section 3 - the token ValueType.
_x509v3_uri = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-x509-token-profile-1.0#X509v3'

# Algorithm identifiers from XML Signature 1.0/1.1, RFC 4051 and XML Encryption 1.1.
_c14n_exclusive_uri = 'http://www.w3.org/2001/10/xml-exc-c14n#'
_rsa_sha256_uri     = 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256'
_sha256_uri         = 'http://www.w3.org/2001/04/xmlenc#sha256'
_rsa_oaep_uri       = 'http://www.w3.org/2009/xmlenc11#rsa-oaep'
_mgf1_sha256_uri    = 'http://www.w3.org/2009/xmlenc11#mgf1sha256'
_aes128_gcm_uri     = 'http://www.w3.org/2009/xmlenc11#aes128-gcm'

# SAML profiles - the sender-vouches subject confirmation method.
_sender_vouches_uri = 'urn:oasis:names:tc:SAML:2.0:cm:sender-vouches'

# XML Encryption 1.1, section 5.2.4 - the GCM IV is the first 96 bits of the CipherValue.
_gcm_nonce_size_bytes = 12

# ################################################################################################################################
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

def _reparse(envelope):
    """ Serializes and reparses an envelope, as would happen over the wire.
    """
    out = etree.fromstring(to_bytes(envelope))
    return out

# ################################################################################################################################

def _username_token_config(use_digest):
    out = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS', 'use_digest': use_digest}
    return out

# ################################################################################################################################

def _x509_config(parties, sign, encrypt):
    """ The config dict of an outgoing connection's X.509 definition.
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

def _saml_config():
    out = {
        'mode': Mode.SAML,
        'issuer': 'urn:qhin:example',
        'subject': 'CN=Dr Smith,O=Example Hospital',
        'audience': 'urn:qhin:other',
        'attributes': {
            'urn:oasis:names:tc:xspa:1.0:subject:organization': 'Example Hospital',
            'urn:oasis:names:tc:xacml:2.0:subject:role': '224608005',
        },
    }

    return out

# ################################################################################################################################

def _security_header_of(wire):
    """ Returns the wsse:Security header of a reparsed envelope.
    """
    out = wire.find(f'.//{_wsse}Security')
    assert out is not None

    return out

# ################################################################################################################################

def _validate(schema, element):
    """ Validates a subtree against one of the official schemas.
    """
    schema.assertValid(deepcopy(element))

# ################################################################################################################################

def _canonicalize(element):
    """ Exclusive canonicalization straight through lxml - independent
    of any canonicalization helper in the code under test.
    """
    out = etree.tostring(element, method='c14n', exclusive=True, with_comments=False)
    return out

# ################################################################################################################################

def _find_by_wsu_id(wire, wsu_id):
    """ Finds the element a ds:Reference points at, walking the tree directly.
    """
    for element in wire.iter():
        if element.get(f'{_wsu}Id') == wsu_id:
            out = element
            break
    else:
        out = None

    assert out is not None
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestUsernameTokenConformance:
    """ UsernameToken Profile 1.0 - the header validates against the official
    OASIS schema and the digest recomputes from the profile's own formula.
    """

    def test_text_token_validates_against_wsse_schema(self, wsse_schema):
        envelope = _sample_envelope()
        apply_wss(envelope, _username_token_config(use_digest=False))

        _validate(wsse_schema, _security_header_of(_reparse(envelope)))

    def test_digest_token_validates_against_wsse_schema(self, wsse_schema):
        envelope = _sample_envelope()
        apply_wss(envelope, _username_token_config(use_digest=True))

        _validate(wsse_schema, _security_header_of(_reparse(envelope)))

    def test_password_type_uris_match_the_profile(self):
        # Section 4.1 - the Type attribute distinguishes the two password forms.
        text_envelope = _sample_envelope()
        apply_wss(text_envelope, _username_token_config(use_digest=False))

        digest_envelope = _sample_envelope()
        apply_wss(digest_envelope, _username_token_config(use_digest=True))

        text_password = _reparse(text_envelope).find(f'.//{_wsse}Password')
        digest_password = _reparse(digest_envelope).find(f'.//{_wsse}Password')

        assert text_password.get('Type') == _password_text_uri
        assert digest_password.get('Type') == _password_digest_uri

    def test_nonce_encoding_type_matches_the_profile(self):
        envelope = _sample_envelope()
        apply_wss(envelope, _username_token_config(use_digest=True))

        nonce = _reparse(envelope).find(f'.//{_wsse}Nonce')

        assert nonce.get('EncodingType') == _nonce_encoding_uri

    def test_digest_recomputes_from_the_profile_formula(self):
        # Section 4.1 - Password_Digest = Base64(SHA-1(nonce + created + password)),
        # recomputed here with hashlib alone from the values on the wire.
        envelope = _sample_envelope()
        apply_wss(envelope, _username_token_config(use_digest=True))

        token = _reparse(envelope).find(f'.//{_wsse}UsernameToken')

        nonce = b64decode(token.find(f'{_wsse}Nonce').text)
        created = token.find(f'{_wsu}Created').text
        declared = token.find(f'{_wsse}Password').text

        recomputed_bytes = sha1(nonce + created.encode('utf-8') + b'MYPASS').digest()
        recomputed = b64encode(recomputed_bytes).decode('ascii')

        assert declared == recomputed

# ################################################################################################################################
# ################################################################################################################################

class TestX509SignatureConformance:
    """ X.509 Token Profile 1.0 and XML Signature - the signed header validates
    against the official schemas and every cryptographic value recomputes
    independently with lxml c14n and the cryptography library alone.
    """

    def test_signed_security_header_validates_against_wsse_schema(self, parties, wsse_schema):
        # The secext schema imports wsu and xmldsig, so this validates
        # the BinarySecurityToken, the Timestamp and the whole Signature strictly.
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=True, encrypt=False))

        _validate(wsse_schema, _security_header_of(_reparse(envelope)))

    def test_signature_validates_against_dsig_schema(self, parties, dsig_schema):
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=True, encrypt=False))

        signature = _reparse(envelope).find(f'.//{_dsig}Signature')

        _validate(dsig_schema, signature)

    def test_timestamp_validates_against_wsu_schema(self, parties, wsu_schema):
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=True, encrypt=False))

        timestamp = _reparse(envelope).find(f'.//{_wsu}Timestamp')

        _validate(wsu_schema, timestamp)

    def test_signed_envelope_validates_against_soap12_schema(self, parties, soap12_schema):
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=True, encrypt=False))

        soap12_schema.assertValid(_reparse(envelope))

    def test_algorithm_identifiers_match_the_specs(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=True, encrypt=False))

        wire = _reparse(envelope)
        signed_info = wire.find(f'.//{_dsig}SignedInfo')

        canonicalization_method = signed_info.find(f'{_dsig}CanonicalizationMethod')
        signature_method = signed_info.find(f'{_dsig}SignatureMethod')

        assert canonicalization_method.get('Algorithm') == _c14n_exclusive_uri
        assert signature_method.get('Algorithm') == _rsa_sha256_uri

        for digest_method in signed_info.findall(f'.//{_dsig}DigestMethod'):
            assert digest_method.get('Algorithm') == _sha256_uri

    def test_binary_security_token_carries_the_der_certificate(self, parties):
        # X.509 Token Profile section 3.1 - an X509v3 token is the base64
        # of the DER encoding of the certificate, byte for byte.
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=True, encrypt=False))

        token = _reparse(envelope).find(f'.//{_wsse}BinarySecurityToken')

        assert token.get('ValueType') == _x509v3_uri
        assert b64decode(token.text) == parties.sender.signing_certificate.public_bytes(Encoding.DER)

    def test_reference_digests_recompute_independently(self, parties):
        # XML Signature core validation, step one - each ds:Reference digest
        # is the SHA-256 of the exclusive canonical form of its target element.
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=True, encrypt=False))

        wire = _reparse(envelope)
        references = wire.findall(f'.//{_dsig}Reference')

        # The signature must cover the timestamp and the body.
        assert len(references) == 2

        for reference in references:
            wsu_id = reference.get('URI').removeprefix('#')
            target = _find_by_wsu_id(wire, wsu_id)

            recomputed_bytes = sha256(_canonicalize(target)).digest()
            recomputed = b64encode(recomputed_bytes).decode('ascii')

            declared = reference.find(f'{_dsig}DigestValue').text
            assert declared == recomputed

    def test_signature_value_verifies_with_cryptography_alone(self, parties):
        # XML Signature core validation, step two - the SignatureValue is
        # an RSASSA-PKCS1-v1_5 SHA-256 signature over the canonical SignedInfo,
        # verified here directly against the signer's public key.
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=True, encrypt=False))

        wire = _reparse(envelope)

        signed_info = wire.find(f'.//{_dsig}SignedInfo')
        signature_value = b64decode(wire.find(f'.//{_dsig}SignatureValue').text)

        public_key = parties.sender.signing_certificate.public_key()

        # Raises InvalidSignature if the value does not verify.
        public_key.verify(signature_value, _canonicalize(signed_info), PKCS1v15(), SHA256())

# ################################################################################################################################
# ################################################################################################################################

class TestX509EncryptionConformance:
    """ XML Encryption 1.1 - the encrypted elements validate against the official
    W3C schemas and the ciphertext decrypts with the cryptography library alone,
    using only what the message itself declares.
    """

    def test_encrypted_elements_validate_against_xenc_schemas(self, parties, xenc11_schema):
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=False, encrypt=True))

        wire = _reparse(envelope)

        # The 1.1 schema set knows both namespaces, so the xenc11:MGF
        # inside xenc:EncryptionMethod validates strictly as well.
        _validate(xenc11_schema, wire.find(f'.//{_xenc}EncryptedKey'))
        _validate(xenc11_schema, wire.find(f'.//{_xenc}EncryptedData'))

    def test_encrypted_envelope_validates_against_soap12_schema(self, parties, soap12_schema):
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=True, encrypt=True))

        soap12_schema.assertValid(_reparse(envelope))

    def test_encryption_algorithm_identifiers_match_the_specs(self, parties):
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=False, encrypt=True))

        wire = _reparse(envelope)

        key_method = wire.find(f'.//{_xenc}EncryptedKey/{_xenc}EncryptionMethod')
        data_method = wire.find(f'.//{_xenc}EncryptedData/{_xenc}EncryptionMethod')
        mgf = key_method.find(f'{_xenc11}MGF')

        assert key_method.get('Algorithm') == _rsa_oaep_uri
        assert mgf.get('Algorithm') == _mgf1_sha256_uri
        assert data_method.get('Algorithm') == _aes128_gcm_uri

    def test_ciphertext_decrypts_with_cryptography_alone(self, parties):
        # The declared algorithms must match the actual bytes:
        # unwrap the content key with RSA-OAEP over SHA-256, split the GCM IV
        # off the CipherValue per XML Encryption 1.1 and decrypt - all
        # with the cryptography library directly.
        envelope = _sample_envelope()
        apply_wss(envelope, _x509_config(parties, sign=False, encrypt=True))

        wire = _reparse(envelope)

        wrapped_key = b64decode(wire.find(f'.//{_xenc}EncryptedKey//{_xenc}CipherValue').text)
        oaep_padding = OAEP(mgf=MGF1(SHA256()), algorithm=SHA256(), label=None)
        content_key = parties.receiver.decryption_key.decrypt(wrapped_key, oaep_padding)

        cipher_bytes = b64decode(wire.find(f'.//{_xenc}EncryptedData//{_xenc}CipherValue').text)
        nonce = cipher_bytes[:_gcm_nonce_size_bytes]
        ciphertext = cipher_bytes[_gcm_nonce_size_bytes:]

        plaintext = AESGCM(content_key).decrypt(nonce, ciphertext, None)

        assert b'FL0001' in plaintext
        assert b'submitSingleMessage' in plaintext

# ################################################################################################################################
# ################################################################################################################################

class TestSAMLConformance:
    """ SAML 2.0 - the assertion validates against the official OASIS schema
    and its structure matches what the core specification prescribes.
    """

    def test_assertion_validates_against_official_schema(self, saml_schema):
        envelope = _sample_envelope()
        apply_wss(envelope, _saml_config())

        assertion = _reparse(envelope).find(f'.//{_saml2}Assertion')

        _validate(saml_schema, assertion)

    def test_assertion_structure_matches_the_core_spec(self):
        envelope = _sample_envelope()
        apply_wss(envelope, _saml_config())

        assertion = _reparse(envelope).find(f'.//{_saml2}Assertion')

        # Core section 2.3.3 - Version is always 2.0 and ID and IssueInstant are required.
        assert assertion.get('Version') == '2.0'
        assert assertion.get('ID')
        assert assertion.get('IssueInstant')

        # Profiles - the sender-vouches confirmation method is a spec-defined URN.
        confirmation = assertion.find(f'.//{_saml2}SubjectConfirmation')
        assert confirmation.get('Method') == _sender_vouches_uri

        # Core section 2.5.1 - the validity window attributes on Conditions.
        conditions = assertion.find(f'{_saml2}Conditions')
        assert conditions.get('NotBefore')
        assert conditions.get('NotOnOrAfter')

    def test_secured_envelope_validates_against_soap12_schema(self, soap12_schema):
        envelope = _sample_envelope()
        apply_wss(envelope, _saml_config())

        soap12_schema.assertValid(_reparse(envelope))

# ################################################################################################################################
# ################################################################################################################################
