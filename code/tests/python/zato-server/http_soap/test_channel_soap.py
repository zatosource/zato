# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from base64 import b64encode
from unittest.mock import MagicMock

# lxml
from lxml.etree import tostring as etree_tostring

# Zato
from zato.common.api import URL_TYPE
from zato.common.exception import BadRequest, NotFound
from zato.common.soap.addressing import add_addressing, AddressingInfo
from zato.common.soap.common import Content_Type, SOAPVersion
from zato.common.soap.envelope import attach_body, build_envelope, parse_body, parse_envelope, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.mtom import build_mtom, parse_message, to_bytes_map
from zato.common.soap.security.saml import add_assertion, new_assertion
from zato.common.soap.security.wss import Mode
from zato.server.connection.http_soap.channel import RequestDispatcher, RequestHandler
from zato.server.connection.http_soap.channel_soap import build_soap_fault_response, build_soap_response, \
    parse_soap_request, resolve_soap_payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strnone

# ################################################################################################################################
# ################################################################################################################################

_test_cid = 'zcid-test-0001'

_test_operation = 'submitSingleMessage'
_test_hl7_message = 'MSH|^~\\&|MYAPP|MYFAC|IIS|STATE|20260115||VXU^V04^VXU_V04|CTRL-0001|P|2.5.1'
_test_facility = 'FL0001'

# ################################################################################################################################
# ################################################################################################################################

def _make_channel_item(overrides:'anydict | None'=None) -> 'anydict':
    """ Builds a minimal SOAP channel item.
    """
    out:'anydict' = {
        'id': 1,
        'name': 'test.soap.channel',
        'transport': URL_TYPE.SOAP,
        'data_format': 'xml',
        'soap_version': SOAPVersion.V11,
        'use_mtom': False,
    }
    if overrides:
        out.update(overrides)
    return out

# ################################################################################################################################

def _make_request_message() -> 'SOAPMessage':
    """ Builds the operation message every test sends.
    """
    out = SOAPMessage()
    out.hl7Message = _test_hl7_message
    out.facilityID = _test_facility
    return out

# ################################################################################################################################

def _make_envelope_bytes(version:'str', addressing:'AddressingInfo | None'=None) -> 'bytes':
    """ Builds the wire bytes of a request envelope of the given version.
    """
    envelope = build_envelope(version)
    _ = attach_body(envelope, _make_request_message(), _test_operation)

    if addressing:
        add_addressing(envelope, addressing)

    out = to_bytes(envelope)
    return out

# ################################################################################################################################

def _parse_context(version:'str'=SOAPVersion.V11, addressing:'AddressingInfo | None'=None,
    channel_overrides:'anydict | None'=None) -> 'any_':
    """ Parses a sample request all the way through to a resolved context.
    """
    body = _make_envelope_bytes(version, addressing)
    channel_item = _make_channel_item(channel_overrides)

    out = parse_soap_request(_test_cid, body, Content_Type[version], channel_item)
    resolve_soap_payload(_test_cid, out, {})

    return out

# ################################################################################################################################
# ################################################################################################################################

class ParseSOAPRequestTestCase(unittest.TestCase):
    """ Tests for parse_soap_request and resolve_soap_payload.
    """

# ################################################################################################################################

    def test_soap_11_envelope_is_unwrapped(self) -> 'None':
        context = _parse_context(SOAPVersion.V11)

        self.assertEqual(context.soap_version, SOAPVersion.V11)
        self.assertEqual(context.operation, _test_operation)
        self.assertEqual(context.payload.hl7Message, _test_hl7_message)
        self.assertEqual(context.payload.facilityID, _test_facility)

# ################################################################################################################################

    def test_soap_12_envelope_is_unwrapped(self) -> 'None':
        context = _parse_context(SOAPVersion.V12)

        self.assertEqual(context.soap_version, SOAPVersion.V12)
        self.assertEqual(context.payload.hl7Message, _test_hl7_message)

# ################################################################################################################################

    def test_raw_envelope_stays_available(self) -> 'None':
        body = _make_envelope_bytes(SOAPVersion.V11)

        context = parse_soap_request(_test_cid, body, Content_Type[SOAPVersion.V11], _make_channel_item())

        self.assertEqual(context.envelope, body)

# ################################################################################################################################

    def test_addressing_headers_are_parsed(self) -> 'None':
        addressing = AddressingInfo()
        addressing.action = 'urn:cdc:iisb:2011:submitSingleMessage'
        addressing.message_id = 'urn:uuid:11112222-3333-4444-5555-666677778888'

        context = _parse_context(SOAPVersion.V12, addressing)

        self.assertEqual(context.addressing.action, 'urn:cdc:iisb:2011:submitSingleMessage')
        self.assertEqual(context.addressing.message_id, 'urn:uuid:11112222-3333-4444-5555-666677778888')

# ################################################################################################################################

    def test_invalid_xml_raises_bad_request(self) -> 'None':
        with self.assertRaises(BadRequest):
            _ = parse_soap_request(_test_cid, b'this is not an envelope', 'text/xml', _make_channel_item())

# ################################################################################################################################

    def test_non_envelope_root_raises_bad_request(self) -> 'None':
        with self.assertRaises(BadRequest):
            _ = parse_soap_request(_test_cid, b'<data>value</data>', 'text/xml', _make_channel_item())

# ################################################################################################################################

    def test_empty_body_raises_bad_request(self) -> 'None':
        envelope = build_envelope(SOAPVersion.V11)
        body = to_bytes(envelope)

        context = parse_soap_request(_test_cid, body, Content_Type[SOAPVersion.V11], _make_channel_item())

        with self.assertRaises(BadRequest):
            resolve_soap_payload(_test_cid, context, {})

# ################################################################################################################################

    def test_multipart_attachments_resolve_to_bytes(self) -> 'None':

        # Build an MTOM request whose document travels as a part.
        document = b'PDF-1.7 test document bytes'

        message = SOAPMessage()
        message.patientID = 'PAT-0001'
        message.Document = document

        envelope = build_envelope(SOAPVersion.V12)
        xop_parts:'any_' = []
        _ = attach_body(envelope, message, 'ProvideAndRegisterDocumentSetRequest', xop_parts=xop_parts)

        body, content_type = build_mtom(to_bytes(envelope), xop_parts, SOAPVersion.V12)

        context = parse_soap_request(_test_cid, body, content_type, _make_channel_item())
        resolve_soap_payload(_test_cid, context, {})

        # The xop:Include reference reads back as the original bytes ..
        self.assertEqual(context.payload.Document, document)

        # .. and the raw MIME parts are available too.
        self.assertEqual(len(context.attachments), 1)
        self.assertEqual(context.attachments[0].data, document)

# ################################################################################################################################

    def test_username_token_security_is_surfaced(self) -> 'None':
        body = _make_envelope_bytes(SOAPVersion.V11)
        context = parse_soap_request(_test_cid, body, Content_Type[SOAPVersion.V11], _make_channel_item())

        wsgi_environ = {
            'zato.sec_def': {
                'impl': {'mode': Mode.UsernameToken, 'username': 'MYUSER'},
            },
        }
        resolve_soap_payload(_test_cid, context, wsgi_environ)

        self.assertEqual(context.security.mode, Mode.UsernameToken)
        self.assertEqual(context.security.username, 'MYUSER')

# ################################################################################################################################

    def test_saml_security_is_surfaced(self) -> 'None':

        # The incoming message carries an assertion whose subject the service can read.
        envelope = build_envelope(SOAPVersion.V12)
        _ = attach_body(envelope, _make_request_message(), _test_operation)

        assertion = new_assertion('urn:qhin:example', 'clinician@example.gov')
        add_assertion(envelope, assertion)

        body = to_bytes(envelope)
        context = parse_soap_request(_test_cid, body, Content_Type[SOAPVersion.V12], _make_channel_item())

        wsgi_environ = {
            'zato.sec_def': {
                'impl': {'mode': Mode.SAML, 'issuer': 'urn:qhin:example'},
            },
        }
        resolve_soap_payload(_test_cid, context, wsgi_environ)

        self.assertEqual(context.security.mode, Mode.SAML)
        self.assertEqual(context.security.issuer, 'urn:qhin:example')
        self.assertEqual(context.security.subject, 'clinician@example.gov')

# ################################################################################################################################

    def test_no_security_definition_leaves_security_empty(self) -> 'None':
        context = _parse_context(SOAPVersion.V11)

        self.assertIsNone(context.security.mode)
        self.assertIsNone(context.security.username)

# ################################################################################################################################
# ################################################################################################################################

class BuildSOAPResponseTestCase(unittest.TestCase):
    """ Tests for build_soap_response.
    """

# ################################################################################################################################

    def _response_message(self) -> 'SOAPMessage':
        out = SOAPMessage()
        out.return_ = 'MSH|^~\\&|IIS|STATE|MYAPP|MYFAC|20260115||ACK^V04^ACK|CTRL-0001|P|2.5.1\rMSA|AA|CTRL-0001'
        return out

# ################################################################################################################################

    def test_response_matches_request_version_11(self) -> 'None':
        context = _parse_context(SOAPVersion.V11)

        body, content_type = build_soap_response(context, self._response_message())

        self.assertEqual(content_type, Content_Type[SOAPVersion.V11])

        envelope = parse_envelope(body)
        response_body = parse_body(envelope)
        self.assertIn('MSA|AA|CTRL-0001', response_body.submitSingleMessageResponse.return_)

# ################################################################################################################################

    def test_response_matches_request_version_12(self) -> 'None':
        context = _parse_context(SOAPVersion.V12)

        body, content_type = build_soap_response(context, self._response_message())

        self.assertEqual(content_type, Content_Type[SOAPVersion.V12])

        envelope = parse_envelope(body)
        self.assertIn(b'http://www.w3.org/2003/05/soap-envelope', etree_tostring(envelope))

# ################################################################################################################################

    def test_addressing_reply_headers(self) -> 'None':
        addressing = AddressingInfo()
        addressing.action = 'urn:cdc:iisb:2011:submitSingleMessage'
        addressing.message_id = 'urn:uuid:11112222-3333-4444-5555-666677778888'

        context = _parse_context(SOAPVersion.V12, addressing)

        body, _ = build_soap_response(context, self._response_message())
        envelope = parse_envelope(body)

        wire = etree_tostring(envelope).decode('utf-8')

        # The reply relates to the request's message id under the default response action ..
        self.assertIn('urn:uuid:11112222-3333-4444-5555-666677778888', wire)
        self.assertIn('urn:cdc:iisb:2011:submitSingleMessageResponse', wire)

        # .. and carries a fresh message id of its own.
        self.assertIn('MessageID', wire)

# ################################################################################################################################

    def test_no_addressing_in_request_means_none_in_reply(self) -> 'None':
        context = _parse_context(SOAPVersion.V11)

        body, _ = build_soap_response(context, self._response_message())

        self.assertNotIn(b'MessageID', body)
        self.assertNotIn(b'RelatesTo', body)

# ################################################################################################################################

    def test_mtom_response_with_bytes(self) -> 'None':
        context = _parse_context(SOAPVersion.V12, channel_overrides={'use_mtom': True})

        digest = b'\x01\x02\x03\x04 binary receipt bytes'

        message = SOAPMessage()
        message.status = 'urn:ihe:iti:2007:ResponseStatusType:Success'
        message.receipt = digest

        body, content_type = build_soap_response(context, message)

        # The reply is a multipart package whose part carries the raw bytes.
        self.assertIn('multipart/related', content_type)

        envelope_bytes, parts = parse_message(body, content_type)
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0].data, digest)

        # The envelope resolves the reference back into the same bytes.
        envelope = parse_envelope(envelope_bytes)
        response_body = parse_body(envelope, to_bytes_map(parts))
        self.assertEqual(response_body.submitSingleMessageResponse.receipt, digest)

# ################################################################################################################################

    def test_bytes_without_mtom_stay_inline(self) -> 'None':
        context = _parse_context(SOAPVersion.V12)

        message = SOAPMessage()
        message.receipt = b'binary receipt bytes'

        body, content_type = build_soap_response(context, message)

        self.assertEqual(content_type, Content_Type[SOAPVersion.V12])

        # Without MTOM the bytes travel as inline base64.
        expected = b64encode(b'binary receipt bytes').decode('ascii')

        envelope = parse_envelope(body)
        response_body = parse_body(envelope)
        self.assertEqual(response_body.submitSingleMessageResponse.receipt, expected)

# ################################################################################################################################
# ################################################################################################################################

class BuildSOAPFaultTestCase(unittest.TestCase):
    """ Tests for build_soap_fault_response.
    """

# ################################################################################################################################

    def test_client_error_becomes_sender_fault_11(self) -> 'None':
        exception = BadRequest(_test_cid, 'facilityID is required')

        body, content_type = build_soap_fault_response(SOAPVersion.V11, exception, 'Internal error')

        self.assertEqual(content_type, Content_Type[SOAPVersion.V11])
        self.assertIn(b'soap:Client', body)
        self.assertIn(b'facilityID is required', body)

# ################################################################################################################################

    def test_client_error_becomes_sender_fault_12(self) -> 'None':
        exception = NotFound(_test_cid, 'No such document')

        body, content_type = build_soap_fault_response(SOAPVersion.V12, exception, 'Internal error')

        self.assertEqual(content_type, Content_Type[SOAPVersion.V12])
        self.assertIn(b'soap:Sender', body)
        self.assertIn(b'No such document', body)

# ################################################################################################################################

    def test_server_error_becomes_receiver_fault_with_default_message(self) -> 'None':
        exception = Exception('A stack trace would show module paths and line numbers')

        body, _ = build_soap_fault_response(SOAPVersion.V11, exception, 'Internal error')

        self.assertIn(b'soap:Server', body)
        self.assertIn(b'Internal error', body)

        # Nothing of the exception itself ever reaches the caller.
        self.assertNotIn(b'stack trace', body)

# ################################################################################################################################

    def test_server_error_receiver_fault_12(self) -> 'None':
        exception = Exception('Database connection details')

        body, _ = build_soap_fault_response(SOAPVersion.V12, exception, 'Internal error')

        self.assertIn(b'soap:Receiver', body)
        self.assertNotIn(b'Database connection details', body)

# ################################################################################################################################
# ################################################################################################################################

class SetPayloadSOAPTestCase(unittest.TestCase):
    """ Tests for the SOAP branch of RequestHandler.set_payload.
    """

# ################################################################################################################################

    def _make_handler(self) -> 'RequestHandler':
        out = RequestHandler(MagicMock())
        return out

# ################################################################################################################################

    def test_message_is_wrapped_in_envelope(self) -> 'None':
        handler = self._make_handler()
        context = _parse_context(SOAPVersion.V11)

        service_instance = MagicMock()
        service_instance.request.soap = context

        message = SOAPMessage()
        message.status = 'Accepted'

        response = MagicMock()
        response.payload = message

        handler.set_payload(response, 'xml', URL_TYPE.SOAP, service_instance)

        envelope = parse_envelope(response.payload)
        response_body = parse_body(envelope)

        self.assertEqual(response_body.submitSingleMessageResponse.status, 'Accepted')
        self.assertEqual(response.content_type, Content_Type[SOAPVersion.V11])

# ################################################################################################################################

    def test_string_payload_passes_through(self) -> 'None':
        handler = self._make_handler()

        service_instance = MagicMock()

        response = MagicMock()
        response.payload = '<myResponse>as-is</myResponse>'

        handler.set_payload(response, 'xml', URL_TYPE.SOAP, service_instance)

        self.assertEqual(response.payload, '<myResponse>as-is</myResponse>')

# ################################################################################################################################
# ################################################################################################################################

class DispatchErrorSOAPTestCase(unittest.TestCase):
    """ Tests for _handle_dispatch_error on SOAP channels.
    """

# ################################################################################################################################

    def _dispatch_error(self, exception:'Exception', wsgi_environ:'anydict',
        soap_version:'strnone'=SOAPVersion.V11) -> 'any_':
        """ Runs _handle_dispatch_error through a dispatcher with mocked dependencies.
        """
        dispatcher = RequestDispatcher(
            server=MagicMock(),
            url_data=MagicMock(),
            request_handler=MagicMock(),
            return_tracebacks=True,
            default_error_message='Internal error',
            http_methods_allowed=['GET', 'POST'],
        )

        channel_item = _make_channel_item({'soap_version': soap_version})

        out = dispatcher._handle_dispatch_error(_test_cid, exception, channel_item, wsgi_environ)
        return out

# ################################################################################################################################

    def test_client_error_returns_sender_fault(self) -> 'None':
        wsgi_environ:'anydict' = {'zato.http.response.headers': {}}

        result = self._dispatch_error(BadRequest(_test_cid, 'facilityID is required'), wsgi_environ)

        self.assertIn(b'soap:Client', result)
        self.assertIn('400', wsgi_environ['zato.http.response.status'])
        self.assertEqual(wsgi_environ['zato.http.response.headers']['Content-Type'], Content_Type[SOAPVersion.V11])

# ################################################################################################################################

    def test_server_error_hides_details_even_with_tracebacks_enabled(self) -> 'None':
        wsgi_environ:'anydict' = {'zato.http.response.headers': {}}

        result = self._dispatch_error(Exception('Sensitive database details'), wsgi_environ)

        self.assertIn(b'soap:Server', result)
        self.assertNotIn(b'Sensitive database details', result)
        self.assertIn('500', wsgi_environ['zato.http.response.status'])

# ################################################################################################################################

    def test_version_comes_from_parsed_request(self) -> 'None':

        # The channel is configured for 1.1 but the request arrived as 1.2 -
        # the fault follows the request.
        context = _parse_context(SOAPVersion.V12)
        wsgi_environ:'anydict' = {
            'zato.http.response.headers': {},
            'zato.request.soap': context,
        }

        result = self._dispatch_error(BadRequest(_test_cid, 'facilityID is required'), wsgi_environ)

        self.assertIn(b'soap:Sender', result)
        self.assertEqual(wsgi_environ['zato.http.response.headers']['Content-Type'], Content_Type[SOAPVersion.V12])

# ################################################################################################################################

    def test_version_defaults_to_channel_config_when_parsing_failed(self) -> 'None':
        wsgi_environ:'anydict' = {'zato.http.response.headers': {}}

        result = self._dispatch_error(BadRequest(_test_cid, 'Invalid SOAP request'), wsgi_environ, SOAPVersion.V12)

        self.assertIn(b'soap:Sender', result)
        self.assertEqual(wsgi_environ['zato.http.response.headers']['Content-Type'], Content_Type[SOAPVersion.V12])

# ################################################################################################################################

    def test_version_defaults_to_11_without_channel_config(self) -> 'None':
        wsgi_environ:'anydict' = {'zato.http.response.headers': {}}

        result = self._dispatch_error(BadRequest(_test_cid, 'Invalid SOAP request'), wsgi_environ, None)

        self.assertIn(b'soap:Client', result)
        self.assertEqual(wsgi_environ['zato.http.response.headers']['Content-Type'], Content_Type[SOAPVersion.V11])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
