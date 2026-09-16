# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The client tests that reach past the envelope - MTOM parts, ebXML, the transport and its errors, what the audit
# log masks and how a response's status and charset are read. The envelope and security tests stay in test_client.

# stdlib
from base64 import b64encode
from http.client import BAD_GATEWAY, INTERNAL_SERVER_ERROR, OK

# lxml
import lxml.etree as etree

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
from zato.common.typing_ import cast_
from zato.common.util.xml_.mime_ import new_content_id, Part

# Test helpers
from client_fixtures import cdc_message as _cdc_message, sender_x509 as _sender_x509

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The CDC IIS namespace the messages of these tests are in
_ns_cdc = 'urn:cdc:iisb:2011'

# Text that only survives a round trip if the encoding is handled - every one of these characters
# is outside ASCII and each has a different byte in iso-8859-2 than it does in UTF-8.
_non_ascii_text = 'zażółć gęślą jaźń'

# ################################################################################################################################
# ################################################################################################################################

def _record_audit(client:'SOAPClient') -> 'list':
    """ Plugs an audit callback into a client and returns the list every event lands in.
    """
    recorded = []

    def callback(cid:'any_', event:'any_', endpoint:'any_', outcome:'any_', data:'any_', status:'any_'='',
        application_outcome:'any_'=''):
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
