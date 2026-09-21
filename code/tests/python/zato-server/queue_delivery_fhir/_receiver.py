# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The endpoint of an outgoing FHIR connection - an HTTP server that records every request and answers a write with
# the resource it was given, under an id of its own, or with an OperationOutcome, as it is scripted to.

# stdlib
import logging
import threading
from dataclasses import dataclass
from http.client import CREATED, OK, UNPROCESSABLE_ENTITY
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps, loads
from urllib.parse import urlsplit

# Test support
from queue_delivery.receiver import RecordedRequest, RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery_fhir.receiver')

_content_type = 'application/fhir+json'

_shutdown_timeout_seconds = 5

# A GET is a read, never a delivery
_read_method = 'GET'

# What a refused request is answered with - an OperationOutcome saying so
Outcome_Diagnostics = 'The resource was not accepted'
Outcome_Code = 'processing'
_outcome_severity = 'error'
_operation_outcome_type = 'OperationOutcome'

# The ids a created resource is answered with are counted up from here
_first_created_id = 1
_created_id_prefix = 'created-'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class FHIRRecordedRequest(RecordedRequest):
    """ One request as the endpoint of an outgoing FHIR connection saw it - the body is the JSON of the resource.
    """
    method: str = ''
    path: str = ''
    query_string: str = ''
    headers: 'strstrdict' = None # type: ignore[assignment]

    @property
    def status_code(self) -> 'int':
        """ The status the request was answered with.
        """
        out = self.outcome
        return out

# ################################################################################################################################
# ################################################################################################################################

class _ReceiverHTTPServer(HTTPServer):
    """ The HTTP server behind one receiver, carrying that receiver so its handlers can reach it.
    """

    receiver: 'FHIRRecordingReceiver'

# ################################################################################################################################
# ################################################################################################################################

def _operation_outcome() -> 'anydict':
    """ The OperationOutcome a refused request is answered with.
    """
    out = {
        'resourceType': _operation_outcome_type,
        'issue': [{
            'severity': _outcome_severity,
            'code': Outcome_Code,
            'diagnostics': Outcome_Diagnostics,
        }],
    }

    return out

# ################################################################################################################################

def _resource_of_path(path:'str') -> 'anydict':
    """ The resource a read of a path answers with - its type and id are the path's own elements, and a path
    of the type alone, which is what a ping asks for, is answered with a resource of that type and no id.
    """
    elements = path.strip('/').split('/')

    out = {
        'resourceType': elements[0],
    }

    if len(elements) > 1:
        out['id'] = elements[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

class _RequestHandler(BaseHTTPRequestHandler):
    """ Records every request in full and answers it as currently scripted.
    """

    server: '_ReceiverHTTPServer'

    def log_message(self, format:'str', *arguments:'any_') -> 'None':
        message = format % arguments
        logger.debug('[FHIR] %s', message)

# ################################################################################################################################

    def _handle(self, method:'str') -> 'None':

        content_length_header = self.headers.get('Content-Length')
        if content_length_header is None:
            content_length_header = '0'

        content_length = int(content_length_header)
        body = self.rfile.read(content_length).decode('utf-8')

        headers:'strstrdict' = {}

        for key, value in self.headers.items():
            headers[key.lower()] = value

        parts = urlsplit(self.path)

        status_code = self.server.receiver.record(
            method=method,
            path=parts.path,
            query_string=parts.query,
            headers=headers,
            body=body,
        )

        wire_status, answer = self.server.receiver.answer(method, parts.path, body, status_code)
        answer_bytes = dumps(answer).encode('utf-8')

        self.send_response(wire_status)
        self.send_header('Content-Type', _content_type)
        self.send_header('Content-Length', str(len(answer_bytes)))
        self.end_headers()
        _ = self.wfile.write(answer_bytes)

# ################################################################################################################################

    def do_GET(self) -> 'None': # noqa: N802
        self._handle('GET')

    def do_POST(self) -> 'None': # noqa: N802
        self._handle('POST')

    def do_PUT(self) -> 'None': # noqa: N802
        self._handle('PUT')

    def do_PATCH(self) -> 'None': # noqa: N802
        self._handle('PATCH')

    def do_DELETE(self) -> 'None': # noqa: N802
        self._handle('DELETE')

# ################################################################################################################################
# ################################################################################################################################

class FHIRRecordingReceiver(RecordingReceiver):
    """ The endpoint of an outgoing FHIR connection.
    """

    # A write is accepted with the resource created and refused with an OperationOutcome
    Accept_Outcome = CREATED
    Refuse_Outcome = UNPROCESSABLE_ENTITY

    def __init__(self, port:'int') -> 'None':
        super().__init__(port)

        self._server:'_ReceiverHTTPServer | None' = None
        self._thread:'threading.Thread | None' = None

        self._next_created_id = _first_created_id

# ################################################################################################################################

    def record(
        self,
        method:'str',
        path:'str',
        query_string:'str',
        headers:'strstrdict',
        body:'str',
        ) -> 'int':
        """ Stores one request and returns the outcome it is answered with.
        """
        status_code = self.next_outcome()

        request = FHIRRecordedRequest(
            body=body,
            outcome=status_code,
            is_accepted=self.is_accepted(status_code),
            is_read=method == _read_method,
            method=method,
            path=path,
            query_string=query_string,
            headers=headers,
        )

        self.add_request(request)

        return status_code

# ################################################################################################################################

    def answer(self, method:'str', path:'str', body:'str', status_code:'int') -> 'tuple[int, anydict]':
        """ What goes on the wire for one request - the status and the document. A refused request is answered with
        an OperationOutcome, an accepted write with the resource under an id of its own and an accepted read with
        the resource the path names, a read being a 200 rather than the 201 a write is accepted with.
        """
        if not self.is_accepted(status_code):
            out = (status_code, _operation_outcome())
            return out

        if method == _read_method:
            out = (OK, _resource_of_path(path))
            return out

        resource = loads(body)

        with self._lock:
            resource['id'] = f'{_created_id_prefix}{self._next_created_id}'
            self._next_created_id += 1

        out = (status_code, resource)
        return out

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
