# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The endpoint of an outgoing REST connection - an HTTP server that records every request and answers with the status
# it is scripted to.

# stdlib
import logging
import threading
from dataclasses import dataclass, field
from http.client import OK, SERVICE_UNAVAILABLE
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

# Test support
from queue_delivery.receiver import RecordedRequest, RecordingReceiver

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery_rest.receiver')

_default_content_type = 'application/json'
_default_body = '{}'

_shutdown_timeout_seconds = 5

# A GET is a read, never a delivery
_read_method = 'GET'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HTTPRecordedRequest(RecordedRequest):
    """ One request as the endpoint of an outgoing REST connection saw it.
    """
    method: str = ''
    path: str = ''
    query_string: str = ''
    headers: 'strstrdict' = field(default_factory=dict)

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

    receiver: 'HTTPRecordingReceiver'

# ################################################################################################################################
# ################################################################################################################################

class _RequestHandler(BaseHTTPRequestHandler):
    """ Records every request in full and answers it as currently scripted.
    """

    server: '_ReceiverHTTPServer'

    def log_message(self, format:'str', *arguments:'any_') -> 'None':
        message = format % arguments
        logger.debug('[HTTP] %s', message)

# ################################################################################################################################

    def _handle(self, method:'str') -> 'None':

        content_length_header = self.headers.get('Content-Length')
        if content_length_header is None:
            content_length_header = '0'

        content_length = int(content_length_header)
        body = self.rfile.read(content_length)

        headers:'strstrdict' = {}

        for key, value in self.headers.items():
            headers[key.lower()] = value

        parts = urlsplit(self.path)

        status_code = self.server.receiver.record(
            method=method,
            path=parts.path,
            query_string=parts.query,
            headers=headers,
            body=body.decode('utf-8'),
        )

        answer = _default_body.encode('utf-8')

        self.send_response(status_code)
        self.send_header('Content-Type', _default_content_type)
        self.send_header('Content-Length', str(len(answer)))
        self.end_headers()
        _ = self.wfile.write(answer)

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

class HTTPRecordingReceiver(RecordingReceiver[HTTPRecordedRequest]):
    """ The endpoint of an outgoing REST connection.
    """

    Accept_Outcome = OK
    Refuse_Outcome = SERVICE_UNAVAILABLE

    def __init__(self, port:'int') -> 'None':
        super().__init__(port)

        self._server:'_ReceiverHTTPServer | None' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    def record(self, method:'str', path:'str', query_string:'str', headers:'strstrdict', body:'str') -> 'int':
        """ Stores one request and returns the status it is answered with.
        """
        status_code = self.next_outcome()

        request = HTTPRecordedRequest(
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
