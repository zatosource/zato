# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import threading
import time
from http.client import OK, SERVICE_UNAVAILABLE
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import NamedTuple
from urllib.parse import urlsplit

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_outgoing.receiver')

# What a plain REST target answers with, which is what most of these connections are pointed at.
_default_content_type = 'application/json'
_default_body = '{}'

# How long the server waits for its thread to notice a shutdown, in seconds.
_shutdown_timeout_seconds = 5

# How long one wait for a request may take at most, in seconds.
_default_wait_timeout_seconds = 60

# How long one polling sleep is, in seconds.
_poll_interval_seconds = 0.1

# ################################################################################################################################
# ################################################################################################################################

class RecordedRequest(NamedTuple):
    """ One request as the target of an outgoing connection saw it.
    """
    method: str
    path: str
    query_string: str
    headers: 'strstrdict'
    body: str

# ################################################################################################################################

request_list = list[RecordedRequest]

# ################################################################################################################################
# ################################################################################################################################

class ReceiverAnswer(NamedTuple):
    """ What a receiver answers one request with. A FHIR target answers differently from a REST one,
    so what a target says is part of how it is set up rather than fixed here.
    """
    status_code: int
    content_type: str
    body: str

# ################################################################################################################################

# What a target that is refusing says, whatever it answers with when it is accepting
_refusal_answer = ReceiverAnswer(SERVICE_UNAVAILABLE, _default_content_type, _default_body)

# ################################################################################################################################
# ################################################################################################################################

class _ReceiverHTTPServer(HTTPServer):
    """ The HTTP server behind one receiver, carrying that receiver so its handlers can reach it.
    """

    receiver: 'RecordingReceiver'

# ################################################################################################################################
# ################################################################################################################################

class _RequestHandler(BaseHTTPRequestHandler):
    """ Records every request in full and answers it the way the receiver was told to.
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

        request = RecordedRequest(
            method=method,
            path=parts.path,
            query_string=parts.query,
            headers=headers,
            body=body.decode('utf-8'),
        )

        answer = self.server.receiver.record(request)
        body = answer.body.encode('utf-8')

        self.send_response(answer.status_code)
        self.send_header('Content-Type', answer.content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        _ = self.wfile.write(body)

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

class RecordingReceiver:
    """ The target of an outgoing connection - it records every request it receives in full,
    which is how a test sees what a connection actually sent, and it can refuse requests
    for as long as a test needs a target that is not accepting anything.
    """

    def __init__(
        self,
        port:'int',
        status_code:'int'=OK,
        content_type:'str'=_default_content_type,
        body:'str'=_default_body,
    ) -> 'None':
        self.port = port
        self.requests:'request_list' = []
        self.rejection_count = 0
        self.rejections_left = 0

        # What this target says when it accepts a request - a FHIR server does not answer
        # the way a plain REST one does, and what a client makes of the answer is part of the test
        self.answer = ReceiverAnswer(status_code, content_type, body)

        self._server:'_ReceiverHTTPServer | None' = None
        self._thread:'threading.Thread | None' = None
        self._lock = threading.Lock()

# ################################################################################################################################

    def record(self, request:'RecordedRequest') -> 'ReceiverAnswer':
        """ Stores one request and answers the way the receiver is currently answering.
        """
        with self._lock:

            # A receiver that was told to refuse does so, and counts down to accepting again ..
            if self.rejections_left > 0:
                self.rejections_left -= 1
                self.rejection_count += 1

                return _refusal_answer

            # .. anything else is accepted and kept.
            self.requests.append(request)

            out = self.answer
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
        """ Stops the receiver, which leaves its port refusing connections.
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

    def clear(self) -> 'None':
        """ Forgets every request recorded so far and accepts again.
        """
        with self._lock:
            self.requests = []
            self.rejection_count = 0
            self.rejections_left = 0

# ################################################################################################################################

    def refuse_next(self, count:'int') -> 'None':
        """ Makes the receiver answer that many requests with 503 before accepting again.
        """
        with self._lock:
            self.rejections_left = count
            self.rejection_count = 0

# ################################################################################################################################

    def wait_for_requests(
        self,
        expected_count:'int'=1,
        timeout:'float'=_default_wait_timeout_seconds,
        ) -> 'request_list':
        """ Blocks until that many requests have been accepted, then returns all of them.
        """
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            with self._lock:
                out = list(self.requests)

            count = len(out)

            if count >= expected_count:
                return out

            time.sleep(_poll_interval_seconds)

        with self._lock:
            out = list(self.requests)

        return out

# ################################################################################################################################
# ################################################################################################################################
