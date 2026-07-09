# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import shutil
import ssl
import threading
import time
from http.client import BAD_REQUEST, OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# lxml
from lxml import etree

# Zato
from zato.common.soap.addressing import add_addressing, AddressingInfo, parse_addressing
from zato.common.soap.common import Content_Type, FaultCode, SOAPException
from zato.common.soap.ebxml import build_message as build_ebxml_message, EbXMLInfo, parse_message_header
from zato.common.soap.envelope import attach_body, build_envelope, build_fault, get_body, get_version, parse_body, \
    parse_envelope, to_bytes
from zato.common.soap.message import SOAPMessage
from zato.common.soap.mtom import build_mtom, parse_message, to_bytes_map
from zato.common.soap.security.wss import enforce_wss

# ################################################################################################################################

from certs import build_tls_material

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict
    from .certs import TLSMaterial

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# How long to wait for expected requests to arrive.
_Request_Wait_Timeout = 10
_Request_Poll_Interval = 0.05

# ################################################################################################################################
# ################################################################################################################################

class _Handler(BaseHTTPRequestHandler):
    """ Parses each incoming SOAP request, records it, and answers according to the per-path
    configuration the test set up - echoing operations, enforcing WS-Security, checking body
    credentials, returning MTOM responses or SOAP faults.
    """

    protocol_version = 'HTTP/1.1'

    def _read_body(self) -> 'bytes':
        if 'Content-Length' in self.headers:
            length = int(self.headers['Content-Length'])
            out = self.rfile.read(length)
        else:
            out = b''
        return out

# ################################################################################################################################

    def _record(self, raw_body:'bytes', content_type:'str') -> 'stranydict':
        """ Parses one request into a record tests can assert on - the raw bytes, headers,
        the parsed envelope, its attachments, addressing and dot-accessed body.
        """
        record:'stranydict' = {
            'path': self.path,
            'method': self.command,
            'headers': dict(self.headers.items()),
            'raw_body': raw_body,
            'content_type': content_type,
            'envelope': None,
            'parts': [],
            'addressing': None,
            'body': None,
        }

        try:
            envelope_bytes, parts = parse_message(raw_body, content_type)
            envelope = parse_envelope(envelope_bytes)

            record['envelope'] = envelope
            record['parts'] = parts
            record['addressing'] = parse_addressing(envelope)

            parts_map = to_bytes_map(parts) if parts else None
            record['body'] = parse_body(envelope, parts_map)

        # A non-SOAP body is recorded as-is, which is enough for the ping and error paths.
        except (SOAPException, etree.XMLSyntaxError):
            pass

        return record

# ################################################################################################################################

    def _handle(self) -> 'None':

        server:'any_' = self.server

        content_type = self.headers.get('Content-Type', '')
        raw_body = self._read_body()

        record = self._record(raw_body, content_type)

        server.recorded_requests.append(record)
        server.last_request = record

        # A ping or any body-less request just gets an OK, nothing to dispatch on.
        if record['envelope'] is None:
            self._send(OK, b'', 'text/plain')
            return

        config = server.path_config.get(self.path, {})

        try:
            status, body, response_content_type = server.build_response(record, config)
        except _Rejected as rejected:
            status, body, response_content_type = rejected.response

        self._send(status, body, response_content_type)

# ################################################################################################################################

    def _send(self, status:'int', body:'bytes', content_type:'str') -> 'None':
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()

        if self.command != 'HEAD':
            _ = self.wfile.write(body)

# ################################################################################################################################

    do_GET   = _handle
    do_POST  = _handle
    do_HEAD  = _handle

# ################################################################################################################################

    def log_message(self, format:'str', *args:'any_') -> 'None':
        logger.info('[soap_test_server] %s', format % args)

# ################################################################################################################################
# ################################################################################################################################

class _Rejected(Exception):
    """ Raised inside response building to short-circuit with a prepared fault response.
    """
    def __init__(self, response:'any_') -> 'None':
        self.response = response

# ################################################################################################################################
# ################################################################################################################################

class _Server(ThreadingHTTPServer):
    """ A threading HTTP server holding the recorded requests and per-path response configuration,
    plus the response-building logic every scenario shares.
    """
    daemon_threads = True

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        self.recorded_requests:'anylist' = []
        self.last_request:'anydict | None' = None
        self.path_config:'anydict' = {}

# ################################################################################################################################

    def build_response(self, record:'stranydict', config:'stranydict') -> 'any_':
        """ Builds the response for one request from its per-path configuration.
        """
        envelope = record['envelope']
        version = get_version(envelope)

        # An optional delay simulates a slow backend for timeout tests.
        if delay := config.get('delay'):
            time.sleep(delay)

        # A path may answer with a prepared, static body - the way backends whose responses
        # are consumed as raw strings do - bypassing all the SOAP-aware response building.
        if raw := config.get('respond_raw'):
            status, body, content_type = raw
            out = (status, body, content_type)
            return out

        # A path may be configured to always fault, which exercises the client's fault handling.
        if fault := config.get('respond_fault'):
            code, reason = fault
            out = (BAD_REQUEST, to_bytes(build_fault(version, code, reason)), Content_Type[version])
            return out

        # WS-Security enforcement rejects a message that does not satisfy the definition.
        if wss_config := config.get('enforce_wss'):
            self._enforce_wss(envelope, wss_config, version)

        # Body-credential paths check the injected credentials really arrived in the body.
        if expected := config.get('expect_credentials'):
            self._check_credentials(record, expected, version)

        # ebXML paths answer with a message-service acknowledgment instead of a plain operation.
        if config.get('ebxml'):
            out = self._ebxml_response(record)
            return out

        out = self._operation_response(record, config, version)
        return out

# ################################################################################################################################

    def _enforce_wss(self, envelope:'any_', wss_config:'stranydict', version:'str') -> 'None':
        """ Enforces a WS-Security definition, turning a failure into a fault response.
        """
        try:
            enforce_wss(envelope, wss_config)
        except SOAPException as e:
            fault = build_fault(version, FaultCode.Sender, str(e))
            raise _Rejected((BAD_REQUEST, to_bytes(fault), Content_Type[version]))

# ################################################################################################################################

    def _check_credentials(self, record:'stranydict', expected:'stranydict', version:'str') -> 'None':
        """ Checks that the operation carries the expected credential elements, faulting otherwise.
        """
        operation = get_body(record['envelope'])[0]

        found = {}
        for child in operation:
            local_name = child.tag.rpartition('}')[2]
            found[local_name] = child.text

        for name, value in expected.items():
            if found.get(name) != value:
                reason = f'Bad credential `{name}`; got {found.get(name)!r}, expected {value!r}'
                fault = build_fault(version, FaultCode.Sender, reason)
                raise _Rejected((BAD_REQUEST, to_bytes(fault), Content_Type[version]))

# ################################################################################################################################

    def _operation_response(self, record:'stranydict', config:'stranydict', version:'str') -> 'any_':
        """ Builds a plain operation response, optionally as an MTOM package or with addressing.
        """
        operation = get_body(record['envelope'])[0]
        operation_name = operation.tag.rpartition('}')[2]
        namespace = operation.tag[1:].partition('}')[0] if operation.tag.startswith('{') else None

        response = SOAPMessage()
        if namespace:
            response.namespace = namespace
        response.status = 'ok'

        # An MTOM response carries a binary field the client resolves back into bytes.
        attachment = config.get('respond_attachment')
        if attachment is not None:
            response.document = attachment

        envelope = build_envelope(version)
        xop_parts:'anylist | None' = [] if attachment is not None else None

        _ = attach_body(envelope, response, f'{operation_name}Response', xop_parts=xop_parts)

        # When the request used addressing, the reply relates back to its message id.
        if request_addressing := record['addressing']:
            if request_addressing.message_id:
                info = AddressingInfo()
                info.action = f'{request_addressing.action}Response' if request_addressing.action else 'urn:response'
                info.relates_to = request_addressing.message_id
                add_addressing(envelope, info, needs_must_understand=False)

        envelope_bytes = to_bytes(envelope)

        if xop_parts:
            body, content_type = build_mtom(envelope_bytes, xop_parts, version)
        else:
            body = envelope_bytes
            content_type = Content_Type[version]

        out = (OK, body, content_type)
        return out

# ################################################################################################################################

    def _ebxml_response(self, record:'stranydict') -> 'any_':
        """ Builds an ebXML acknowledgment that refers back to the incoming message.
        """
        incoming = parse_message_header(record['envelope'])

        info = EbXMLInfo()
        info.from_party = incoming.to_party
        info.to_party = incoming.from_party
        info.cpa_id = incoming.cpa_id
        info.conversation_id = incoming.conversation_id
        info.service = incoming.service
        info.action = 'Acknowledgment'
        info.ref_to_message_id = incoming.message_id

        envelope = build_ebxml_message(info, [])
        body = to_bytes(envelope)

        out = (OK, body, Content_Type['1.1'])
        return out

# ################################################################################################################################
# ################################################################################################################################

class SOAPTestServer:
    """ A live SOAP server for client tests. It records every request and answers per-path,
    over plain HTTP, HTTPS, or HTTPS with mandatory client certificates for mutual-TLS scenarios.
    """
    def __init__(self, tls:'bool'=False, require_client_cert:'bool'=False) -> 'None':
        self.host = '127.0.0.1'
        self.port = 0
        self.tls = tls
        self.require_client_cert = require_client_cert
        self.scheme = 'https' if tls else 'http'

        self.tls_material:'TLSMaterial | None' = None
        self._httpd:'any_' = None
        self._thread:'any_' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Binds to an ephemeral port and serves in a background thread, wrapping the socket
        in TLS - optionally requiring a client certificate - when configured to.
        """
        self._httpd = _Server((self.host, 0), _Handler)
        self.port = self._httpd.server_address[1]

        if self.tls:
            self.tls_material = build_tls_material(self.host)

            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.tls_material.server_certificate_path, self.tls_material.server_key_path)

            # Mutual TLS makes the client certificate mandatory and pins it to our test CA.
            if self.require_client_cert:
                ssl_context.verify_mode = ssl.CERT_REQUIRED
                ssl_context.load_verify_locations(self.tls_material.ca_path)

            self._httpd.socket = ssl_context.wrap_socket(self._httpd.socket, server_side=True)

        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

        logger.info('[SOAPTestServer] started on %s', self.address)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the server and removes any temporary TLS material.
        """
        self._httpd.shutdown()
        self._httpd.server_close()

        if self.tls_material:
            shutil.rmtree(self.tls_material.directory, ignore_errors=True)

        logger.info('[SOAPTestServer] stopped on %s', self.address)

# ################################################################################################################################

    @property
    def address(self) -> 'str':
        out = f'{self.scheme}://{self.host}:{self.port}'
        return out

# ################################################################################################################################

    def url(self, path:'str') -> 'str':
        """ Returns the full URL of a path on this server.
        """
        out = f'{self.address}{path}'
        return out

# ################################################################################################################################

    def configure(self, path:'str', **config:'any_') -> 'None':
        """ Sets the per-path response configuration - enforce_wss, expect_credentials,
        respond_attachment, respond_fault, ebxml, and so on.
        """
        self._httpd.path_config[path] = config

# ################################################################################################################################

    @property
    def last_request(self) -> 'anydict':
        out = self._httpd.last_request
        return out

# ################################################################################################################################

    @property
    def recorded_requests(self) -> 'anylist':
        out = self._httpd.recorded_requests
        return out

# ################################################################################################################################

    def clear_requests(self) -> 'None':
        self._httpd.recorded_requests.clear()
        self._httpd.last_request = None

# ################################################################################################################################

    def wait_for_request_count(self, count:'int', timeout:'float'=_Request_Wait_Timeout) -> 'anylist':
        """ Waits until at least the given number of requests has been recorded and returns them.
        """
        deadline = time.monotonic() + timeout

        while len(self._httpd.recorded_requests) < count and time.monotonic() < deadline:
            time.sleep(_Request_Poll_Interval)

        out = self._httpd.recorded_requests
        return out

# ################################################################################################################################
# ################################################################################################################################
