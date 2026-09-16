# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode, b64encode
from hashlib import sha256
from io import BytesIO

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.x509 import load_der_x509_certificate

# lxml
import lxml.etree as etree

# requests
from requests.exceptions import SSLError

# pytest
import pytest

# Zato
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import NS, SOAPFault, SOAPVersion
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.wss import Mode
from zato.common.typing_ import cast_

# Test helpers
from certs import certificate_pem_path, private_key_pem_path
from client_fixtures import cdc_message as _cdc_message, _ns_cdc, receiver_x509 as _receiver_x509, \
    sender_x509 as _sender_x509

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The soap:Header of a 1.2 envelope, which is where injected header elements land.
_soap_header = f'{{{NS.SOAP12}}}Header'

# ################################################################################################################################
# ################################################################################################################################

class TestBodyCredentials:
    """ CDC IIS style body authentication - credentials live in the connection, never in service code,
    and the wrapper injects them as elements of the operation, in the order the endpoint requires.
    """

    def test_default_order_first(self, soap_server:'any_'):
        soap_server.configure('/imm-default', expect_credentials={'username': 'prod.client', 'password': 's3cret'})

        config = {
            'address': soap_server.url('/imm-default'),
            'soap_version': SOAPVersion.V12,
            'soap_action': 'submitSingleMessage',
            'body_credentials': {'username': 'prod.client', 'password': 's3cret'},
        }
        client = SOAPClient(config)
        response = client.invoke('submitSingleMessage', _cdc_message())
        client.close()

        assert response.submitSingleMessageResponse.status == 'ok'

        # The wire order is username, password, then the business fields the service built.
        operation = soap_server.last_request['body'].submitSingleMessage
        assert list(operation._children) == ['username', 'password', 'facilityID', 'hl7Message']

    def test_explicit_positions(self, soap_server:'any_'):
        soap_server.configure('/imm-positions', expect_credentials={'username': 'u', 'password': 'p'})

        config = {
            'address': soap_server.url('/imm-positions'),
            'soap_version': SOAPVersion.V12,
            'soap_action': 'uploadDocument',
            'body_credentials': {
                'username': 'u',
                'password': 'p',
                'mappings': [
                    {'name': 'username', 'source': 'username', 'position': 2},
                    {'name': 'password', 'source': 'password', 'position': 3},
                ],
            },
        }
        message = SOAPMessage()
        message.namespace = 'urn:example:upload:1.0'
        message.facilityID = 'FAC-023'
        message.hl7Message = 'MSH|...'

        client = SOAPClient(config)
        _ = client.invoke('uploadDocument', message)
        client.close()

        # The identifier stays first, the credentials slot into positions two and three.
        operation = soap_server.last_request['body'].uploadDocument
        assert list(operation._children) == ['facilityID', 'username', 'password', 'hl7Message']

    def test_credentials_never_in_service_message(self, soap_server:'any_'):
        soap_server.configure('/imm-clean', expect_credentials={'username': 'u', 'password': 'p'})

        message = _cdc_message()

        # The message the service built has no credential fields at all.
        assert 'username' not in message._children
        assert 'password' not in message._children

        config = {
            'address': soap_server.url('/imm-clean'),
            'soap_version': SOAPVersion.V12,
            'body_credentials': {'username': 'u', 'password': 'p'},
        }
        client = SOAPClient(config)
        _ = client.invoke('submitSingleMessage', message)
        client.close()

    def test_wrong_credentials_rejected(self, soap_server:'any_'):
        soap_server.configure('/imm-bad', expect_credentials={'username': 'right', 'password': 'right'})

        config = {
            'address': soap_server.url('/imm-bad'),
            'soap_version': SOAPVersion.V12,
            'body_credentials': {'username': 'right', 'password': 'wrong'},
        }
        client = SOAPClient(config)

        with pytest.raises(SOAPFault):
            _ = client.invoke('submitSingleMessage', _cdc_message())

        client.close()

# ################################################################################################################################
# ################################################################################################################################

class TestCustomSOAPHeaders:
    """ The custom header elements a declarative connection injects into every envelope.

    A great many endpoints want a tenant id, a client version or a routing hint in the header rather
    than the body, and having the connection put it there is what keeps it out of every service that
    calls the connection.
    """

    def test_a_plain_header_is_injected(self, soap_server:'any_'):
        soap_server.configure('/hdr-plain')

        config = {
            'address': soap_server.url('/hdr-plain'),
            'soap_version': SOAPVersion.V12,
        }
        client = SOAPClient(config)
        _ = client.invoke('submitSingleMessage', _cdc_message(), soap_headers={'ClientVersion': '4.1'})
        client.close()

        envelope = soap_server.last_request['envelope']
        element = envelope.find(f'.//{_soap_header}/ClientVersion')

        assert element is not None
        assert element.text == '4.1'

    def test_a_namespaced_header_keeps_its_namespace(self, soap_server:'any_'):
        # A name in Clark notation carries its own namespace, which is how a header belonging to a
        # specification the endpoint names is emitted rather than one in no namespace at all.
        soap_server.configure('/hdr-ns')

        config = {
            'address': soap_server.url('/hdr-ns'),
            'soap_version': SOAPVersion.V12,
        }
        client = SOAPClient(config)
        _ = client.invoke('submitSingleMessage', _cdc_message(),
            soap_headers={f'{{{_ns_cdc}}}TenantID': 'ACME'})
        client.close()

        envelope = soap_server.last_request['envelope']
        element = envelope.find(f'.//{{{_ns_cdc}}}TenantID')

        assert element is not None
        assert element.text == 'ACME'

    def test_several_headers_are_all_injected(self):
        config = {
            'address': 'http://127.0.0.1:1/never-reached',
            'soap_version': SOAPVersion.V12,
        }
        client = SOAPClient(config)

        headers = {'ClientVersion': '4.1', 'TenantID': 'ACME', 'Locale': 'en-GB'}
        body, _, _, _ = client._build_request('submitSingleMessage', _cdc_message(), headers)
        client.close()

        for name, value in headers.items():
            assert f'<{name}>{value}</{name}>'.encode() in body

    def test_a_non_string_value_is_written_in_its_lexical_form(self):
        # The rows a dashboard field produces are strings, but a JSONata expression may evaluate to
        # a number or a boolean, and XML has no way to carry a Python repr.
        config = {
            'address': 'http://127.0.0.1:1/never-reached',
            'soap_version': SOAPVersion.V12,
        }
        client = SOAPClient(config)

        body, _, _, _ = client._build_request('submitSingleMessage', _cdc_message(),
            {'Retries': 3, 'IsTest': True})
        client.close()

        assert b'<Retries>3</Retries>' in body

        # A lexical boolean is lower case, which is what a schema-aware peer expects - Python's own
        # str() would produce True and fail validation.
        assert b'<IsTest>true</IsTest>' in body

    def test_no_headers_leaves_the_envelope_alone(self):
        config = {
            'address': 'http://127.0.0.1:1/never-reached',
            'soap_version': SOAPVersion.V12,
        }
        client = SOAPClient(config)

        body, _, _, _ = client._build_request('submitSingleMessage', _cdc_message(), None)
        client.close()

        assert b'ClientVersion' not in body

    def test_custom_headers_coexist_with_ws_security(self, parties:'any_', soap_server:'any_'):
        # Both write into soap:Header, so a connection doing both has two things appending to the
        # same element - the custom header must arrive and the message must still verify.
        soap_server.configure('/hdr-signed', security=_receiver_x509(parties, sign=True, encrypt=False))

        config = {
            'address': soap_server.url('/hdr-signed'),
            'soap_version': SOAPVersion.V12,
            'security': _sender_x509(parties, sign=True, encrypt=False),
        }
        client = SOAPClient(config)

        # The server enforces the signature, so a failure to verify surfaces there as a fault
        # rather than here as a local error.
        response = client.invoke('submitSingleMessage', _cdc_message(), soap_headers={'ClientVersion': '4.1'})
        client.close()

        assert response.submitSingleMessageResponse.status == 'ok'

        envelope = soap_server.last_request['envelope']

        # The custom header sits alongside the security header rather than inside or instead of it.
        assert envelope.find(f'.//{_soap_header}/ClientVersion') is not None
        assert envelope.find(f'.//{{{NS.WSSE}}}Security') is not None

# ################################################################################################################################
# ################################################################################################################################

class TestClientCertificate:
    """ Mutual TLS - the connection presents a client certificate mounted at a local path,
    which is what CDC IIS client-certificate auth, NHS Spine and IHE ATNA node auth require.
    """

    def test_separate_cert_and_key_files(self, soap_mtls_server:'any_'):
        material = soap_mtls_server.tls_material
        soap_mtls_server.configure('/mtls-a')

        config = {
            'address': soap_mtls_server.url('/mtls-a'),
            'validate_tls': material.ca_path,
            'tls_client_cert': material.client_certificate_path,
            'tls_client_key': material.client_key_path,
        }
        client = SOAPClient(config)
        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == 'ok'

    def test_combined_cert_and_key_file(self, soap_mtls_server:'any_'):
        material = soap_mtls_server.tls_material
        soap_mtls_server.configure('/mtls-b')

        config = {
            'address': soap_mtls_server.url('/mtls-b'),
            'validate_tls': material.ca_path,
            'tls_client_cert': material.client_combined_path,
        }
        client = SOAPClient(config)
        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == 'ok'

    def test_missing_client_certificate_rejected(self, soap_mtls_server:'any_'):
        material = soap_mtls_server.tls_material
        soap_mtls_server.configure('/mtls-c')

        config = {
            'address': soap_mtls_server.url('/mtls-c'),
            'validate_tls': material.ca_path,
        }
        client = SOAPClient(config)

        with pytest.raises(SSLError):
            _ = client.invoke('op', _cdc_message())

        client.close()

    def test_body_credentials_over_mutual_tls(self, soap_mtls_server:'any_'):
        material = soap_mtls_server.tls_material
        soap_mtls_server.configure('/mtls-both', expect_credentials={'username': 'u', 'password': 'p'})

        # CDC IIS allows both at once - credentials in the body and a client certificate on the wire.
        config = {
            'address': soap_mtls_server.url('/mtls-both'),
            'validate_tls': material.ca_path,
            'tls_client_cert': material.client_combined_path,
            'body_credentials': {'username': 'u', 'password': 'p'},
        }
        client = SOAPClient(config)
        response = client.invoke('submitSingleMessage', _cdc_message())
        client.close()

        assert response.submitSingleMessageResponse.status == 'ok'

# ################################################################################################################################
# ################################################################################################################################

def _independent_saml_verify(envelope:'any_', ca_certificate:'any_'):
    """ Verifies an enveloped SAML signature straight from the wire using only lxml, hashlib
    and cryptography - the digest, the signature value and the signer's chain to the CA.
    """
    assertion = envelope.find(f'.//{{{NS.SAML2}}}Assertion')

    signature = assertion.find(f'{{{NS.DS}}}Signature')

    # Recompute the reference digest over the assertion with its signature removed.
    assertion_copy = etree.fromstring(etree.tostring(assertion))
    signature_copy = cast_('any_', assertion_copy.find(f'{{{NS.DS}}}Signature'))
    assertion_copy.remove(signature_copy)

    buffer = BytesIO()
    etree.ElementTree(assertion_copy).write(buffer, method='c14n', exclusive=True, with_comments=False)
    recomputed = b64encode(sha256(buffer.getvalue()).digest()).decode('ascii')

    declared = signature.find(f'{{{NS.DS}}}SignedInfo/{{{NS.DS}}}Reference/{{{NS.DS}}}DigestValue').text
    assert ''.join(declared.split()) == recomputed

    # Verify the signature value over the canonical SignedInfo with the certificate's public key.
    signed_info = signature.find(f'{{{NS.DS}}}SignedInfo')
    signed_info_buffer = BytesIO()
    etree.ElementTree(signed_info).write(signed_info_buffer, method='c14n', exclusive=True, with_comments=False)

    signature_value = b64decode(signature.find(f'{{{NS.DS}}}SignatureValue').text)
    certificate_bytes = b64decode(signature.find(f'.//{{{NS.DS}}}X509Certificate').text)
    certificate = load_der_x509_certificate(certificate_bytes)

    _ = cast_('any_', certificate.public_key()).verify(signature_value, signed_info_buffer.getvalue(), PKCS1v15(), SHA256())

    # And the signer must chain to the trusted CA.
    certificate.verify_directly_issued_by(ca_certificate)

# ################################################################################################################################

class TestSignedSAML:
    """ XUA-style signed assertions - IHE, TEFCA and eHealth Exchange require the assertion
    to be signed by the issuer, with SHA-1 forbidden.
    """

    def test_signed_assertion_independently_verified(self, soap_server:'any_', parties:'any_'):
        channel = {'mode': Mode.SAML, 'issuer': 'urn:qhin:example', 'sign': True,
            'trust_anchors': certificate_pem_path(parties.ca_certificate)}
        soap_server.configure('/xua-signed', enforce_wss=channel)

        config = {
            'address': soap_server.url('/xua-signed'),
            'soap_version': SOAPVersion.V12,
            'security': {
                'mode': Mode.SAML,
                'issuer': 'urn:qhin:example',
                'subject': 'CN=Dr Smith,O=Example Hospital',
                'sign': True,
                'signing_key': private_key_pem_path(parties.sender.signing_key),
                'signing_certificate_chain': certificate_pem_path(parties.sender.signing_certificate),
            },
        }
        client = SOAPClient(config)
        response = client.invoke('DocumentQuery', _cdc_message())
        client.close()

        assert response.DocumentQueryResponse.status == 'ok'

        # Re-verify the signature from the recorded wire bytes, independently of our own code.
        _independent_saml_verify(soap_server.last_request['envelope'], parties.ca_certificate)

    def test_unsigned_assertion_rejected(self, soap_server:'any_'):
        """ An unsigned assertion is trusted on its Issuer text alone, which the sender writes,
        so it has to be refused however the channel is configured.
        """
        channel = {'mode': Mode.SAML, 'issuer': 'urn:idp'}
        soap_server.configure('/xua-unsigned', enforce_wss=channel)

        config = {
            'address': soap_server.url('/xua-unsigned'),
            'soap_version': SOAPVersion.V12,
            'security': {'mode': Mode.SAML, 'issuer': 'urn:idp', 'subject': 'user@example.gov'},
        }
        client = SOAPClient(config)

        with pytest.raises(SOAPFault):
            _ = client.invoke('DocumentQuery', _cdc_message())

        client.close()

    def test_tampered_signed_assertion_rejected(self, soap_server:'any_', parties:'any_'):
        channel = {'mode': Mode.SAML, 'issuer': 'urn:qhin:example', 'sign': True,
            'trust_anchors': certificate_pem_path(parties.ca_certificate)}

        # A definition that pins a different issuer name than the message carries is refused.
        wrong_issuer_channel = dict(channel, issuer='urn:qhin:other')
        soap_server.configure('/xua-wrong', enforce_wss=wrong_issuer_channel)

        config = {
            'address': soap_server.url('/xua-wrong'),
            'soap_version': SOAPVersion.V12,
            'security': {
                'mode': Mode.SAML,
                'issuer': 'urn:qhin:example',
                'subject': 'CN=Dr Smith',
                'sign': True,
                'signing_key': private_key_pem_path(parties.sender.signing_key),
                'signing_certificate_chain': certificate_pem_path(parties.sender.signing_certificate),
            },
        }
        client = SOAPClient(config)

        with pytest.raises(SOAPFault):
            _ = client.invoke('DocumentQuery', _cdc_message())

        client.close()

# ################################################################################################################################
# ################################################################################################################################

class TestUsernameToken:
    """ WS-Security UsernameToken, in both its text and digest password forms.
    """

    def test_text_password(self, soap_server:'any_'):
        channel = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS', 'use_digest': False}
        soap_server.configure('/ut-text', enforce_wss=channel)

        config = {
            'address': soap_server.url('/ut-text'),
            'soap_version': SOAPVersion.V12,
            'security': dict(channel),
        }
        client = SOAPClient(config)
        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == 'ok'

    def test_digest_password(self, soap_server:'any_'):
        channel = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS', 'use_digest': True}
        soap_server.configure('/ut-digest', enforce_wss=channel)

        config = {
            'address': soap_server.url('/ut-digest'),
            'soap_version': SOAPVersion.V12,
            'security': dict(channel),
        }
        client = SOAPClient(config)
        _ = client.invoke('op', _cdc_message())
        client.close()

        # The digest form never puts the password on the wire.
        assert b'MYPASS' not in soap_server.last_request['raw_body']

    def test_wrong_password_rejected(self, soap_server:'any_'):
        channel = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS', 'use_digest': False}
        soap_server.configure('/ut-bad', enforce_wss=channel)

        config = {
            'address': soap_server.url('/ut-bad'),
            'soap_version': SOAPVersion.V12,
            'security': {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'WRONG', 'use_digest': False},
        }
        client = SOAPClient(config)

        with pytest.raises(SOAPFault):
            _ = client.invoke('op', _cdc_message())

        client.close()

# ################################################################################################################################
# ################################################################################################################################

class TestX509:
    """ WS-Security X.509 - signing the body and, on top of it, encrypting it for the recipient.
    """

    def test_sign_only(self, soap_server:'any_', parties:'any_'):
        soap_server.configure('/x509-sign', enforce_wss=_receiver_x509(parties, sign=True, encrypt=False))

        config = {
            'address': soap_server.url('/x509-sign'),
            'soap_version': SOAPVersion.V12,
            'security': _sender_x509(parties, sign=True, encrypt=False),
        }
        client = SOAPClient(config)
        response = client.invoke('submitSingleMessage', _cdc_message())
        client.close()

        assert response.submitSingleMessageResponse.status == 'ok'

    def test_sign_and_encrypt(self, soap_server:'any_', parties:'any_'):
        soap_server.configure('/x509-both', enforce_wss=_receiver_x509(parties, sign=True, encrypt=True))

        config = {
            'address': soap_server.url('/x509-both'),
            'soap_version': SOAPVersion.V12,
            'security': _sender_x509(parties, sign=True, encrypt=True),
        }
        client = SOAPClient(config)
        response = client.invoke('submitSingleMessage', _cdc_message())
        client.close()

        assert response.submitSingleMessageResponse.status == 'ok'

        # The plaintext never appears on the wire.
        assert b'FL0001' not in soap_server.last_request['raw_body']

# ################################################################################################################################
# ################################################################################################################################

class TestAddressing:
    """ WS-Addressing headers on the request and their echo in the reply.
    """

    def test_headers_injected_and_reply_relates(self, soap_server:'any_'):
        soap_server.configure('/wsa')

        config = {
            'address': soap_server.url('/wsa'),
            'soap_version': SOAPVersion.V12,
            'soap_action': 'urn:ihe:iti:2007:CrossGatewayQuery',
            'use_ws_addressing': True,
        }
        client = SOAPClient(config)
        response = client.invoke('CrossGatewayQuery', _cdc_message())
        client.close()

        request_addressing = soap_server.last_request['addressing']

        # The request carries Action, To and a generated MessageID ..
        assert request_addressing.action == 'urn:ihe:iti:2007:CrossGatewayQuery'
        assert request_addressing.to == config['address']
        assert request_addressing.message_id

        # .. and the reply relates back to that message id.
        assert response.addressing.relates_to == request_addressing.message_id

# ################################################################################################################################
# ################################################################################################################################
