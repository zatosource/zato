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
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
from cryptography.x509 import load_der_x509_certificate

# lxml
from lxml import etree

# requests
from requests.exceptions import ReadTimeout, SSLError

# pytest
import pytest

# Zato
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import FaultCode, NS, SOAPFault, SOAPVersion
from zato.common.soap.ebxml import decrypt_payload, EbXMLInfo, verify_payload
from zato.common.soap.message import SOAPMessage
from zato.common.soap.security.wss import Mode
from zato.common.util.xml_.mime_ import new_content_id, Part

# ################################################################################################################################
# ################################################################################################################################

_ns_cdc = 'urn:cdc:iisb:2011'

# ################################################################################################################################
# ################################################################################################################################

def _key_pem(key):
    out = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode('ascii')
    return out

# ################################################################################################################################

def _cert_pem(certificate):
    out = certificate.public_bytes(Encoding.PEM).decode('ascii')
    return out

# ################################################################################################################################

def _sender_x509(parties, sign, encrypt):
    """ The X.509 security config an outgoing connection presents - our key material
    plus the receiver's certificate.
    """
    out = {
        'mode': Mode.X509,
        'sign': sign,
        'encrypt': encrypt,
        'signing_key': _key_pem(parties.sender.signing_key),
        'signing_certificate_chain': _cert_pem(parties.sender.signing_certificate),
        'peer_certificate': _cert_pem(parties.receiver.signing_certificate),
    }
    return out

# ################################################################################################################################

def _receiver_x509(parties, sign, encrypt):
    """ The X.509 config the server enforces - our decryption key plus the sender's pinned certificate.
    """
    out = {
        'mode': Mode.X509,
        'sign': sign,
        'encrypt': encrypt,
        'decryption_key': _key_pem(parties.receiver.decryption_key),
        'peer_certificate': _cert_pem(parties.sender.signing_certificate),
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

    def test_default_order_first(self, soap_server):
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

    def test_explicit_positions(self, soap_server):
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

    def test_credentials_never_in_service_message(self, soap_server):
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

    def test_wrong_credentials_rejected(self, soap_server):
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

class TestClientCertificate:
    """ Mutual TLS - the connection presents a client certificate mounted at a local path,
    which is what CDC IIS client-certificate auth, NHS Spine and IHE ATNA node auth require.
    """

    def test_separate_cert_and_key_files(self, soap_mtls_server):
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

    def test_combined_cert_and_key_file(self, soap_mtls_server):
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

    def test_missing_client_certificate_rejected(self, soap_mtls_server):
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

    def test_body_credentials_over_mutual_tls(self, soap_mtls_server):
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

def _independent_saml_verify(envelope, ca_certificate):
    """ Verifies an enveloped SAML signature straight from the wire using only lxml, hashlib
    and cryptography - the digest, the signature value and the signer's chain to the CA.
    """
    assertion = envelope.find(f'.//{{{NS.SAML2}}}Assertion')

    signature = assertion.find(f'{{{NS.DS}}}Signature')

    # Recompute the reference digest over the assertion with its signature removed.
    assertion_copy = etree.fromstring(etree.tostring(assertion))
    signature_copy = assertion_copy.find(f'{{{NS.DS}}}Signature')
    assertion_copy.remove(signature_copy)

    buffer = BytesIO()
    etree.ElementTree(assertion_copy).write_c14n(buffer, exclusive=True, with_comments=False)
    recomputed = b64encode(sha256(buffer.getvalue()).digest()).decode('ascii')

    declared = signature.find(f'{{{NS.DS}}}SignedInfo/{{{NS.DS}}}Reference/{{{NS.DS}}}DigestValue').text
    assert ''.join(declared.split()) == recomputed

    # Verify the signature value over the canonical SignedInfo with the certificate's public key.
    signed_info = signature.find(f'{{{NS.DS}}}SignedInfo')
    signed_info_buffer = BytesIO()
    etree.ElementTree(signed_info).write_c14n(signed_info_buffer, exclusive=True, with_comments=False)

    signature_value = b64decode(signature.find(f'{{{NS.DS}}}SignatureValue').text)
    certificate_bytes = b64decode(signature.find(f'.//{{{NS.DS}}}X509Certificate').text)
    certificate = load_der_x509_certificate(certificate_bytes)

    certificate.public_key().verify(signature_value, signed_info_buffer.getvalue(), PKCS1v15(), SHA256())

    # And the signer must chain to the trusted CA.
    certificate.verify_directly_issued_by(ca_certificate)

# ################################################################################################################################

class TestSignedSAML:
    """ XUA-style signed assertions - IHE, TEFCA and eHealth Exchange require the assertion
    to be signed by the issuer, with SHA-1 forbidden.
    """

    def test_signed_assertion_independently_verified(self, soap_server, parties):
        channel = {'mode': Mode.SAML, 'issuer': 'urn:qhin:example', 'sign': True,
            'trust_anchors': _cert_pem(parties.ca_certificate)}
        soap_server.configure('/xua-signed', enforce_wss=channel)

        config = {
            'address': soap_server.url('/xua-signed'),
            'soap_version': SOAPVersion.V12,
            'security': {
                'mode': Mode.SAML,
                'issuer': 'urn:qhin:example',
                'subject': 'CN=Dr Smith,O=Example Hospital',
                'sign': True,
                'signing_key': _key_pem(parties.sender.signing_key),
                'signing_certificate_chain': _cert_pem(parties.sender.signing_certificate),
            },
        }
        client = SOAPClient(config)
        response = client.invoke('DocumentQuery', _cdc_message())
        client.close()

        assert response.DocumentQueryResponse.status == 'ok'

        # Re-verify the signature from the recorded wire bytes, independently of our own code.
        _independent_saml_verify(soap_server.last_request['envelope'], parties.ca_certificate)

    def test_unsigned_assertion_still_works(self, soap_server):
        channel = {'mode': Mode.SAML, 'issuer': 'urn:idp'}
        soap_server.configure('/xua-unsigned', enforce_wss=channel)

        config = {
            'address': soap_server.url('/xua-unsigned'),
            'soap_version': SOAPVersion.V12,
            'security': {'mode': Mode.SAML, 'issuer': 'urn:idp', 'subject': 'user@example.gov'},
        }
        client = SOAPClient(config)
        response = client.invoke('DocumentQuery', _cdc_message())
        client.close()

        assert response.DocumentQueryResponse.status == 'ok'

    def test_tampered_signed_assertion_rejected(self, soap_server, parties):
        channel = {'mode': Mode.SAML, 'issuer': 'urn:qhin:example', 'sign': True,
            'trust_anchors': _cert_pem(parties.ca_certificate)}

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
                'signing_key': _key_pem(parties.sender.signing_key),
                'signing_certificate_chain': _cert_pem(parties.sender.signing_certificate),
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

    def test_text_password(self, soap_server):
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

    def test_digest_password(self, soap_server):
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

    def test_wrong_password_rejected(self, soap_server):
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

    def test_sign_only(self, soap_server, parties):
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

    def test_sign_and_encrypt(self, soap_server, parties):
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

    def test_headers_injected_and_reply_relates(self, soap_server):
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

    def test_request_bytes_become_xop(self, soap_server):
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

    def test_response_parts_land_in_attachments(self, soap_server):
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

    def test_message_and_acknowledgment_over_mutual_tls(self, soap_mtls_server):
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

    def test_signed_and_encrypted_payload_roundtrip(self, soap_server, parties):
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

# ################################################################################################################################

def _make_receiver_keystore(parties):
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

    def test_fault_becomes_exception(self, soap_server):
        soap_server.configure('/fault', respond_fault=(FaultCode.Receiver, 'Backend unavailable'))

        config = {'address': soap_server.url('/fault'), 'soap_version': SOAPVersion.V12}
        client = SOAPClient(config)

        with pytest.raises(SOAPFault) as exception_info:
            _ = client.invoke('op', _cdc_message())

        client.close()

        assert exception_info.value.reason == 'Backend unavailable'

    def test_timeout(self, soap_server):
        soap_server.configure('/slow', delay=1)

        config = {'address': soap_server.url('/slow'), 'soap_version': SOAPVersion.V12, 'timeout': 0.3}
        client = SOAPClient(config)

        with pytest.raises(ReadTimeout):
            _ = client.invoke('op', _cdc_message())

        client.close()

    def test_tls_verification_against_ca(self, soap_tls_server):
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

    def test_tls_verification_rejects_untrusted(self, soap_tls_server):
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

    def test_tls_verification_disabled(self, soap_tls_server):
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

    def test_ping(self, soap_server):
        config = {'address': soap_server.url('/ping'), 'ping_method': 'HEAD'}
        client = SOAPClient(config)
        status = client.ping()
        client.close()

        assert status == 200

# ################################################################################################################################
# ################################################################################################################################
