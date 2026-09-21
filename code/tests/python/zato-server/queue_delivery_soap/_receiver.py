# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The endpoint of an outgoing SOAP connection - an HTTP server that records the operation element of every envelope
# and answers with a response envelope or with a fault, as it is scripted to.

# stdlib
import logging
import threading
from dataclasses import dataclass
from http.client import INTERNAL_SERVER_ERROR, OK
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

# lxml
from lxml import etree

# Zato
from zato.common.soap.common import Content_Type, FaultCode, SOAPVersion
from zato.common.soap.envelope import build_envelope, build_fault, get_body, get_version, parse_envelope, to_bytes

# Test support
from queue_delivery.receiver import RecordedRequest, RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery_soap.receiver')

_shutdown_timeout_seconds = 5

# What a refused invocation is answered with - a Receiver fault, which SOAP 1.2 carries on a 500
Fault_Reason = 'Service unavailable'

# The element a response envelope answers an operation with and what it says
_response_suffix = 'Response'
_response_status_tag = 'status'
_response_status_text = 'ok'

# The version a request without an envelope, a ping, is answered in
_default_version = SOAPVersion.V12

# The only method that delivers - anything else is a ping
_delivery_method = 'POST'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class SOAPRecordedRequest(RecordedRequest):
    """ One request as the endpoint of an outgoing SOAP connection saw it - the body is the XML of the operation element.
    """
    method: str = ''
    path: str = ''
    operation: str = ''
    soap_version: str = ''
    headers: 'strstrdict' = None # type: ignore[assignment]

    @property
    def status_code(self) -> 'int':
        """ The HTTP status the request was answered with.
        """
        out = self.outcome
        return out

# ################################################################################################################################
# ################################################################################################################################

class _ReceiverHTTPServer(HTTPServer):
    """ The HTTP server behind one receiver, carrying that receiver so its handlers can reach it.
    """

    receiver: 'SOAPRecordingReceiver'

# ################################################################################################################################
# ################################################################################################################################

def _operation_element(envelope_bytes:'bytes') -> 'tuple[str, str, any_]':
    """ The version of an envelope and the name and element of the one operation its body carries.
    """
    envelope = parse_envelope(envelope_bytes)
    version = get_version(envelope)

    body = get_body(envelope)
    operation_element = body[0]

    operation = etree.QName(operation_element).localname

    return version, operation, operation_element

# ################################################################################################################################

def _response_envelope(version:'str', operation:'str') -> 'bytes':
    """ An envelope answering an operation with its response element.
    """
    envelope = build_envelope(version)
    body = get_body(envelope)

    response = etree.SubElement(body, operation + _response_suffix)
    status = etree.SubElement(response, _response_status_tag)
    status.text = _response_status_text

    out = to_bytes(envelope)
    return out

# ################################################################################################################################

def _fault_envelope(version:'str') -> 'bytes':
    """ An envelope carrying the fault a refused invocation is answered with.
    """
    envelope = build_fault(version, FaultCode.Receiver, Fault_Reason)

    out = to_bytes(envelope)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _RequestHandler(BaseHTTPRequestHandler):
    """ Records every request in full and answers it as currently scripted.
    """

    server: '_ReceiverHTTPServer'

    def log_message(self, format:'str', *arguments:'any_') -> 'None':
        message = format % arguments
        logger.debug('[SOAP] %s', message)

# ################################################################################################################################

    def _handle(self, method:'str') -> 'None':

        content_length_header = self.headers.get('Content-Length')
        if content_length_header is None:
            content_length_header = '0'

        content_length = int(content_length_header)
        raw_body = self.rfile.read(content_length)

        headers:'strstrdict' = {}

        for key, value in self.headers.items():
            headers[key.lower()] = value

        parts = urlsplit(self.path)

        # A delivery carries an envelope, whose operation element is what is recorded, a ping carries nothing
        if raw_body:
            version, operation, operation_element = _operation_element(raw_body)
            body = etree.tostring(operation_element, encoding='unicode')
        else:
            version = _default_version
            operation = ''
            body = ''

        status_code = self.server.receiver.record(
            method=method,
            path=parts.path,
            operation=operation,
            soap_version=version,
            headers=headers,
            body=body,
        )

        if status_code == OK:
            answer = _response_envelope(version, operation)
        else:
            answer = _fault_envelope(version)

        self.send_response(status_code)
        self.send_header('Content-Type', Content_Type[version])
        self.send_header('Content-Length', str(len(answer)))
        self.end_headers()

        # A HEAD is answered with headers alone
        if method != 'HEAD':
            _ = self.wfile.write(answer)

# ################################################################################################################################

    def do_GET(self) -> 'None': # noqa: N802
        self._handle('GET')

    def do_HEAD(self) -> 'None': # noqa: N802
        self._handle('HEAD')

    def do_POST(self) -> 'None': # noqa: N802
        self._handle('POST')

# ################################################################################################################################
# ################################################################################################################################

class SOAPRecordingReceiver(RecordingReceiver):
    """ The endpoint of an outgoing SOAP connection.
    """

    Accept_Outcome = OK
    Refuse_Outcome = INTERNAL_SERVER_ERROR

    def __init__(self, port:'int') -> 'None':
        super().__init__(port)

        self._server:'_ReceiverHTTPServer | None' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    def record(
        self,
        method:'str',
        path:'str',
        operation:'str',
        soap_version:'str',
        headers:'strstrdict',
        body:'str',
        ) -> 'int':
        """ Stores one request and returns the HTTP status it is answered with.
        """
        status_code = self.next_outcome()

        request = SOAPRecordedRequest(
            body=body,
            outcome=status_code,
            is_accepted=self.is_accepted(status_code),
            is_read=method != _delivery_method,
            method=method,
            path=path,
            operation=operation,
            soap_version=soap_version,
            headers=headers,
        )

        self.add_request(request)

        return status_code

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the receiver in a thread of its own.
        """
        address = ('127.0.0.1', self.port)

        server = _ReceiverHTTPServer(address, _RequestHandler)
        server.receiver = self

        self._server = server

        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        self._thread = thread

        logger.info('Receiver started on port %d', self.port)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the receiver.
        """
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None

        if self._thread:
            self._thread.join(timeout=_shutdown_timeout_seconds)
            self._thread = None

        logger.info('Receiver stopped on port %d', self.port)

# ################################################################################################################################
# ################################################################################################################################
