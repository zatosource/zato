# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64decode, b64encode
from hashlib import sha256
from http.client import BAD_GATEWAY, INTERNAL_SERVER_ERROR, OK
from io import BytesIO

# cryptography
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.x509 import load_der_x509_certificate

# lxml
from lxml import etree

# requests
from requests.exceptions import ReadTimeout, SSLError

# pytest
import pytest

# Zato
from zato.common.audit_log.api import AuditEvent
from zato.common.soap.audit import Mask
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import Content_Type, FaultCode, NS, SOAPException, SOAPFault, SOAPVersion
from zato.common.soap.ebxml import decrypt_payload, EbXMLInfo, verify_payload
from zato.common.soap.envelope import attach_body, build_envelope
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.wss import Mode
from zato.common.util.xml_.mime_ import new_content_id, Part

# ################################################################################################################################

from certs import certificate_pem_path, private_key_pem_path
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_ns_cdc = 'urn:cdc:iisb:2011'

# The soap:Header of a 1.2 envelope, which is where injected header elements land.
_soap_header = f'{{{NS.SOAP12}}}Header'

# Text that only survives a round trip if the encoding is handled - every one of these characters
# is outside ASCII and each has a different byte in iso-8859-2 than it does in UTF-8.
_non_ascii_text = 'zażółć gęślą jaźń'

# ################################################################################################################################
# ################################################################################################################################

def _record_audit(client:'SOAPClient') -> 'list':
    """ Plugs an audit callback into a client and returns the list every event lands in.
    """
    recorded = []

    def callback(cid:'any_', event:'any_', endpoint:'any_', outcome:'any_', data:'any_'):
        recorded.append((event, data))

    client.audit_callback = callback
    return recorded

# ################################################################################################################################

def _sent_request(recorded:'list') -> 'bytes':
    """ Returns the data of the one request event out of a recorded audit exchange.
    """
    for event, data in recorded:
        if event == AuditEvent.Request_Sent:
            return data

    raise AssertionError('No request event was recorded')

# ################################################################################################################################

def _build_response_envelope(text:'str'='ok', encoding:'str'='utf-8', declare:'bool'=True) -> 'bytes':
    """ Builds the bytes of a plain SOAP 1.2 response envelope carrying one status element.

    The encoding and whether the XML declaration names it are what the charset tests vary, so both
    are built here rather than by patching serialized bytes after the fact.
    """
    response = SOAPMessage()
    response.namespace = _ns_cdc
    response.status = text

    envelope = build_envelope(SOAPVersion.V12)
    _ = attach_body(envelope, response, 'opResponse')

    out = cast_('bytes', etree.tostring(envelope, xml_declaration=declare, encoding=encoding))
    return out

# ################################################################################################################################
# ################################################################################################################################

def _sender_x509(parties:'any_', sign:'any_', encrypt:'any_'):
    """ The X.509 security config an outgoing connection presents - paths to our key material
    plus the receiver's certificate.
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

def _receiver_x509(parties:'any_', sign:'any_', encrypt:'any_'):
    """ The X.509 config the server enforces - paths to our decryption key plus the sender's pinned certificate.
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

def _cdc_message():
    """ A CDC IIS style request carrying only business fields - never any credentials.
    """
    out = SOAPMessage()
    out.namespace = _ns_cdc
    out.facilityID = 'FL0001'
    out.hl7Message = 'MSH|^~\\&|MYEHR|FL0001|IIS|FLSHOTS|20260401||VXU^V04|12345|P|2.5.1'
    return out

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

class TestMTOM:
    """ MTOM/XOP - bytes travel as optimized binary parts, not inline base64.
    """

    def test_request_bytes_become_xop(self, soap_server:'any_'):
        soap_server.configure('/mtom-request')

        config = {
            'address': soap_server.url('/mtom-request'),
            'soap_version': SOAPVersion.V12,
            'use_mtom': True,
        }
        message = SOAPMessage()
        message.namespace = 'urn:ihe:iti:xds-b:2007'
        message.Document = b'BINARY-DOCUMENT-BYTES'

        client = SOAPClient(config)
        _ = client.invoke('ProvideAndRegisterDocumentSet', message)
        client.close()

        raw_body = soap_server.last_request['raw_body']

        # The wire is a multipart XOP package, not the base64 of the bytes.
        assert b'application/xop+xml' in raw_body
        assert b'Include' in raw_body
        assert b64encode(b'BINARY-DOCUMENT-BYTES') not in raw_body

        # The server resolves the reference straight back into the original bytes.
        assert soap_server.last_request['body'].ProvideAndRegisterDocumentSet.Document == b'BINARY-DOCUMENT-BYTES'

    def test_response_parts_land_in_attachments(self, soap_server:'any_'):
        soap_server.configure('/mtom-response', respond_attachment=b'RETRIEVED-PDF-BYTES')

        config = {
            'address': soap_server.url('/mtom-response'),
            'soap_version': SOAPVersion.V12,
        }
        client = SOAPClient(config)
        response = client.invoke('RetrieveDocumentSet', _cdc_message())
        client.close()

        assert response.RetrieveDocumentSetResponse.document == b'RETRIEVED-PDF-BYTES'
        assert len(response.attachments) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestEbXML:
    """ ebMS 2.0 message service exchanges - NHS Spine and Norway Helsenett shapes, including
    the enterprise-certificate signing and encryption those frameworks put on the payloads.
    """

    def test_message_and_acknowledgment_over_mutual_tls(self, soap_mtls_server:'any_'):
        material = soap_mtls_server.tls_material
        soap_mtls_server.configure('/ebxml-mtls', ebxml=True)

        config = {
            'address': soap_mtls_server.url('/ebxml-mtls'),
            'soap_version': SOAPVersion.V11,
            'validate_tls': material.ca_path,
            'tls_client_cert': material.client_combined_path,
        }
        info = EbXMLInfo()
        info.from_party = 'urn:sender'
        info.to_party = 'urn:receiver'
        info.cpa_id = 'cpa-1'
        info.conversation_id = 'conv-1'
        info.service = 'urn:nhs:names:services:itk'
        info.action = 'COPC_IN000001UK01'

        part = Part()
        part.content_id = new_content_id()
        part.data = b'<itk:DistributionEnvelope>...</itk:DistributionEnvelope>'

        client = SOAPClient(config)
        acknowledgment = client.invoke_ebxml(info, [part])
        client.close()

        assert acknowledgment.action == 'Acknowledgment'
        assert acknowledgment.ref_to_message_id == info.message_id
        assert len(soap_mtls_server.last_request['parts']) == 1

    def test_signed_and_encrypted_payload_roundtrip(self, soap_server:'any_', parties:'any_'):
        soap_server.configure('/ebxml-secure', ebxml=True)

        config = {
            'address': soap_server.url('/ebxml-secure'),
            'soap_version': SOAPVersion.V11,
            'security': _sender_x509(parties, sign=False, encrypt=False),
        }
        info = EbXMLInfo()
        info.from_party = 'urn:sender'
        info.to_party = 'urn:receiver'
        info.cpa_id = 'cpa-1'
        info.conversation_id = 'conv-1'
        info.service = 'urn:helse:svc'
        info.action = 'Send'

        original = b'<Melding>sensitive HIS payload</Melding>'
        part = Part()
        part.content_id = new_content_id()
        part.data = original

        client = SOAPClient(config)
        acknowledgment = client.invoke_ebxml(info, [part], sign=True, encrypt=True)
        client.close()

        assert acknowledgment.action == 'Acknowledgment'

        # The payload that reached the server is encrypted, and its signature and wrapped key rode along.
        received_part = soap_server.last_request['parts'][0]
        assert received_part.data != original
        assert original not in received_part.data

        security = soap_server.last_request['envelope'].find(f'.//{{{NS.WSSE}}}Security')
        signature = security.find(f'{{{NS.DS}}}Signature')
        encrypted_key = security.find(f'{{{NS.XENC}}}EncryptedKey')
        assert signature is not None
        assert encrypted_key is not None

        # The receiver decrypts the payload and verifies the signature over the recovered plaintext.
        receiver_keystore = _make_receiver_keystore(parties)
        decrypt_payload(encrypted_key, received_part, receiver_keystore)
        assert received_part.data == original
        _ = verify_payload(signature, received_part, receiver_keystore)

    def test_reply_payloads_reach_the_caller(self, soap_server:'any_'):
        """ An ebXML reply keeps its business document in a payload part, the body carrying only a
        Manifest that points at it, so a caller that is handed the header alone is handed nothing of
        what it asked for. The parts used to be parsed and then dropped, which silently lost the
        answer to every exchange that was not a bare acknowledgment.
        """
        first_payload = b'<Melding>first reply document</Melding>'
        second_payload = b'<Melding>second reply document</Melding>'

        soap_server.configure('/ebxml-reply-parts', ebxml=True, ebxml_respond_parts=[first_payload, second_payload])

        config = {
            'address': soap_server.url('/ebxml-reply-parts'),
            'soap_version': SOAPVersion.V11,
        }
        info = EbXMLInfo()
        info.from_party = 'urn:sender'
        info.to_party = 'urn:receiver'
        info.cpa_id = 'cpa-1'
        info.conversation_id = 'conv-1'
        info.service = 'urn:helse:svc'
        info.action = 'Query'

        part = Part()
        part.content_id = new_content_id()
        part.data = b'<Sporring>what I asked for</Sporring>'

        client = SOAPClient(config)
        reply = client.invoke_ebxml(info, [part])
        client.close()

        assert reply.action == 'Acknowledgment'
        assert len(reply.attachments) == 2
        assert reply.attachments[0].data == first_payload
        assert reply.attachments[1].data == second_payload

    def test_a_bare_acknowledgment_has_no_attachments(self, soap_server:'any_'):
        """ A reply that carries no payloads leaves the attachments empty rather than absent, so a
        caller can loop over them without first asking whether there are any.
        """
        soap_server.configure('/ebxml-bare-ack', ebxml=True)

        config = {
            'address': soap_server.url('/ebxml-bare-ack'),
            'soap_version': SOAPVersion.V11,
        }
        info = EbXMLInfo()
        info.from_party = 'urn:sender'
        info.to_party = 'urn:receiver'
        info.cpa_id = 'cpa-1'
        info.conversation_id = 'conv-1'
        info.service = 'urn:helse:svc'
        info.action = 'Send'

        part = Part()
        part.content_id = new_content_id()
        part.data = b'<Melding>a document to file</Melding>'

        client = SOAPClient(config)
        reply = client.invoke_ebxml(info, [part])
        client.close()

        assert reply.action == 'Acknowledgment'
        assert reply.attachments == []

# ################################################################################################################################

def _make_receiver_keystore(parties:'any_'):
    """ The receiver's keystore, holding its decryption key and the sender's pinned certificate.
    """
    from zato.common.util.xml_.keystore import new_keystore

    out = new_keystore()
    out.decryption_key = parties.receiver.decryption_key
    out.peer_signing_certificate = parties.sender.signing_certificate
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestTransport:
    """ The plain transport concerns every connection shares - faults, timeouts, TLS verification
    and the ping used to check a connection is reachable.
    """

    def test_fault_becomes_exception(self, soap_server:'any_'):
        soap_server.configure('/fault', respond_fault=(FaultCode.Receiver, 'Backend unavailable'))

        config = {'address': soap_server.url('/fault'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)

        with pytest.raises(SOAPFault) as exception_info:
            _ = client.invoke('op', _cdc_message())

        client.close()

        assert exception_info.value.reason == 'Backend unavailable'

    def test_timeout(self, soap_server:'any_'):
        soap_server.configure('/slow', delay=1)

        config = {'address': soap_server.url('/slow'), 'soap_version': SOAPVersion.V12, 'timeout': 0.3}
        client = SOAPClient(config)

        with pytest.raises(ReadTimeout):
            _ = client.invoke('op', _cdc_message())

        client.close()

    def test_tls_verification_against_ca(self, soap_tls_server:'any_'):
        soap_tls_server.configure('/tls-ok')

        config = {
            'address': soap_tls_server.url('/tls-ok'),
            'soap_version': SOAPVersion.V12,
            'validate_tls': soap_tls_server.tls_material.ca_path,
        }
        client = SOAPClient(config)
        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == 'ok'

    def test_tls_verification_rejects_untrusted(self, soap_tls_server:'any_'):
        soap_tls_server.configure('/tls-untrusted')

        # Verifying against the system trust store fails - the test CA is not in it.
        config = {
            'address': soap_tls_server.url('/tls-untrusted'),
            'soap_version': SOAPVersion.V12,
            'validate_tls': True,
        }
        client = SOAPClient(config)

        with pytest.raises(SSLError):
            _ = client.invoke('op', _cdc_message())

        client.close()

    def test_tls_verification_disabled(self, soap_tls_server:'any_'):
        soap_tls_server.configure('/tls-off')

        config = {
            'address': soap_tls_server.url('/tls-off'),
            'soap_version': SOAPVersion.V12,
            'validate_tls': False,
        }
        client = SOAPClient(config)
        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == 'ok'

# ################################################################################################################################
# ################################################################################################################################

class TestAuditMasking:
    """ What the audit log is allowed to keep. A record outlives the request and is read by more
    people than the request was made for, so a credential written into one is a credential stored
    in plaintext for as long as the log is kept - while the wire still has to carry the real thing.
    """

    def test_username_token_password_is_masked(self, soap_server:'any_'):
        channel = {'mode': Mode.UsernameToken, 'username': 'MYUSER', 'password': 'MYPASS', 'use_digest': False}
        soap_server.configure('/audit-ut', enforce_wss=channel)

        config = {
            'address': soap_server.url('/audit-ut'),
            'soap_version': SOAPVersion.V12,
            'security': dict(channel),
        }
        client = SOAPClient(config)
        recorded = _record_audit(client)

        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == 'ok'

        request_data = _sent_request(recorded)

        assert b'MYPASS' not in request_data
        assert Mask.encode('utf-8') in request_data

        # The username identifies the exchange rather than proving anything, so it stays readable.
        assert b'MYUSER' in request_data

        # The endpoint still received the real password, otherwise it would have faulted.
        assert b'MYPASS' in soap_server.last_request['raw_body']

    def test_body_credentials_are_masked(self, soap_server:'any_'):
        expected = {'username': 'BODYUSER', 'password': 'BODYPASS'}
        soap_server.configure('/audit-body', expect_credentials=expected)

        config = {
            'address': soap_server.url('/audit-body'),
            'soap_version': SOAPVersion.V12,
            'body_credentials': {'username': 'BODYUSER', 'password': 'BODYPASS'},
        }
        client = SOAPClient(config)
        recorded = _record_audit(client)

        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == 'ok'

        request_data = _sent_request(recorded)

        assert b'BODYPASS' not in request_data
        assert b'BODYPASS' in soap_server.last_request['raw_body']

    def test_a_message_without_credentials_is_recorded_whole(self, soap_server:'any_'):
        soap_server.configure('/audit-plain')

        config = {'address': soap_server.url('/audit-plain'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)
        recorded = _record_audit(client)

        _ = client.invoke('op', _cdc_message())
        client.close()

        request_data = _sent_request(recorded)

        # Masking must not cost the record anything when there is nothing to mask.
        assert b'FL0001' in request_data
        assert Mask.encode('utf-8') not in request_data

# ################################################################################################################################
# ################################################################################################################################

class TestResponseStatus:
    """ What an error status means for a response body. Only a fault is a SOAP answer to a failure -
    a gateway's error page and a non-fault envelope on a 500 are both transport-level failures, and
    each one has to say so rather than surface as whatever the XML parser makes of it.
    """

    def test_gateway_error_page_is_refused(self, soap_server:'any_'):
        page = b'<html><head><title>502 Bad Gateway</title></head><body>nginx</body></html>'
        soap_server.configure('/bad-gateway', respond_raw=(BAD_GATEWAY, page, 'text/html'))

        config = {'address': soap_server.url('/bad-gateway'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)

        with pytest.raises(SOAPException) as exception_info:
            _ = client.invoke('op', _cdc_message())

        client.close()

        message = str(exception_info.value)

        # The status and the content type are what identify the failure, and the body's opening
        # names the intermediary that produced it.
        assert 'HTTP 502' in message
        assert 'text/html' in message
        assert '502 Bad Gateway' in message

    def test_non_fault_envelope_on_an_error_status_is_refused(self, soap_server:'any_'):
        envelope = _build_response_envelope()
        soap_server.configure('/error-body',
            respond_raw=(INTERNAL_SERVER_ERROR, envelope, Content_Type[SOAPVersion.V12]))

        config = {'address': soap_server.url('/error-body'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)

        with pytest.raises(SOAPException) as exception_info:
            _ = client.invoke('op', _cdc_message())

        client.close()

        assert 'Non-fault envelope on HTTP 500' in str(exception_info.value)

    def test_fault_on_an_error_status_is_still_a_fault(self, soap_server:'any_'):
        soap_server.configure('/fault-status', respond_fault=(FaultCode.Receiver, 'Backend unavailable'))

        config = {'address': soap_server.url('/fault-status'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)

        # The status check must not get in the way of the fault that explains the status.
        with pytest.raises(SOAPFault) as exception_info:
            _ = client.invoke('op', _cdc_message())

        client.close()

        assert exception_info.value.reason == 'Backend unavailable'

    def test_mislabelled_successful_response_is_still_parsed(self, soap_server:'any_'):
        envelope = _build_response_envelope()
        soap_server.configure('/mislabelled', respond_raw=(OK, envelope, 'text/plain'))

        config = {'address': soap_server.url('/mislabelled'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)
        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == 'ok'

# ################################################################################################################################
# ################################################################################################################################

class TestResponseCharset:
    """ What the transport says a response is encoded in. A document declaring its own encoding is
    self-describing, but one that declares none is read as UTF-8 unless the Content-Type says
    otherwise, so a peer answering in another encoding has to be honoured or its text comes back
    mangled.
    """

    def test_charset_from_the_transport_is_honoured(self, soap_server:'any_'):
        envelope = _build_response_envelope(text=_non_ascii_text, encoding='iso-8859-2', declare=False)
        content_type = 'application/soap+xml; charset=iso-8859-2'
        soap_server.configure('/latin2', respond_raw=(OK, envelope, content_type))

        config = {'address': soap_server.url('/latin2'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)
        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == _non_ascii_text

    def test_own_declaration_wins_over_the_transport(self, soap_server:'any_'):
        envelope = _build_response_envelope(text=_non_ascii_text, encoding='iso-8859-2', declare=True)

        # The transport is wrong and the document is right - a document saying what it is in is
        # what the parser reads, so the mislabelling has to make no difference.
        content_type = 'application/soap+xml; charset=utf-8'
        soap_server.configure('/declared', respond_raw=(OK, envelope, content_type))

        config = {'address': soap_server.url('/declared'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)
        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == _non_ascii_text

    def test_unknown_charset_falls_back_to_the_bytes_as_they_arrived(self, soap_server:'any_'):
        envelope = _build_response_envelope(declare=False)
        content_type = 'application/soap+xml; charset=not-a-real-charset'
        soap_server.configure('/bad-charset', respond_raw=(OK, envelope, content_type))

        config = {'address': soap_server.url('/bad-charset'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)
        response = client.invoke('op', _cdc_message())
        client.close()

        assert response.opResponse.status == 'ok'

# ################################################################################################################################
# ################################################################################################################################
