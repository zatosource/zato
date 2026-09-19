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
    from zato.common.typing_ import any_, intlist, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.queue_delivery_rest.receiver')

_default_content_type = 'application/json'
_default_body = '{}'

_shutdown_timeout_seconds = 5
_default_wait_timeout_seconds = 60
_poll_interval_seconds = 0.1

# ################################################################################################################################
# ################################################################################################################################

class RecordedRequest(NamedTuple):
    """ One request as the endpoint of an outgoing connection saw it.
    """
    method: str
    path: str
    query_string: str
    headers: 'strstrdict'
    body: str
    status_code: int

    # On the monotonic clock
    received_at: float

# ################################################################################################################################

request_list = list[RecordedRequest]

# ################################################################################################################################
# ################################################################################################################################

class _ReceiverHTTPServer(HTTPServer):
    """ The HTTP server behind one receiver, carrying that receiver so its handlers can reach it.
    """

    receiver: 'RecordingReceiver'

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

class RecordingReceiver:
    """ The endpoint of an outgoing connection.
    """

    def __init__(self, port:'int') -> 'None':
        self.port = port

        # Every request received, accepted or not
        self.requests:'request_list' = []

        # The statuses the next requests are answered with, one per request
        self._scripted:'intlist' = []

        # The status once the script has run out
        self._default_status = OK

        self._server:'_ReceiverHTTPServer | None' = None
        self._thread:'threading.Thread | None' = None
        self._lock = threading.Lock()

# ################################################################################################################################

    def record(self, method:'str', path:'str', query_string:'str', headers:'strstrdict', body:'str') -> 'int':
        """ Stores one request and returns the status it is answered with.
        """
        with self._lock:

            if self._scripted:
                status_code = self._scripted.pop(0)
            else:
                status_code = self._default_status

            request = RecordedRequest(
                method=method,
                path=path,
                query_string=query_string,
                headers=headers,
                body=body,
                status_code=status_code,
                received_at=time.monotonic(),
            )

            self.requests.append(request)

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

    def clear(self) -> 'None':
        """ Forgets every recorded request, drops the script and accepts everything again.
        """
        with self._lock:
            self.requests = []
            self._scripted = []
            self._default_status = OK

# ################################################################################################################################

    def answer_next(self, status_codes:'intlist') -> 'None':
        """ Answers the next requests with these statuses, one each, in this order.
        """
        with self._lock:
            self._scripted = list(status_codes)

# ################################################################################################################################

    def refuse_all(self) -> 'None':
        """ Rejects every request from now on with 503.
        """
        with self._lock:
            self._default_status = SERVICE_UNAVAILABLE

# ################################################################################################################################

    def accept_all(self) -> 'None':
        """ Accepts every request from now on.
        """
        with self._lock:
            self._default_status = OK

# ################################################################################################################################

    def accepted(self) -> 'request_list':
        """ The requests answered with 200, in the order they arrived.
        """
        with self._lock:
            out = [request for request in self.requests if request.status_code == OK]

        return out

# ################################################################################################################################

    def wait_for_requests(
        self,
        expected_count:'int'=1,
        timeout:'float'=_default_wait_timeout_seconds,
        ) -> 'request_list':
        """ Blocks until that many requests have arrived, accepted or not, then returns all of them.
        """
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            with self._lock:
                out = list(self.requests)

            if len(out) >= expected_count:
                return out

            time.sleep(_poll_interval_seconds)

        with self._lock:
            out = list(self.requests)

        return out

# ################################################################################################################################

    def wait_for_accepted(
        self,
        expected_count:'int'=1,
        timeout:'float'=_default_wait_timeout_seconds,
        ) -> 'request_list':
        """ Blocks until that many requests have been accepted, then returns the accepted ones.
        """
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:

            out = self.accepted()

            if len(out) >= expected_count:
                return out

            time.sleep(_poll_interval_seconds)

        out = self.accepted()
        return out

# ################################################################################################################################
# ################################################################################################################################
