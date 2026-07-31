# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import threading
import time
from http.client import OK
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import NamedTuple

# Zato
from hl7_client.ports import find_free_port
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# What every listener here binds to
_Host = '127.0.0.1'

# What the receiver answers with when the caller does not say otherwise
_Default_Response_Body = '{}'
_Default_Content_Type  = 'application/json'

# What the receiver keeps its requests in
request_list = list['ReceivedRequest']

# ################################################################################################################################
# ################################################################################################################################

class ReceivedRequest(NamedTuple):
    """ One HTTP request as this receiver saw it.
    """
    method: 'str'
    path: 'str'
    body: 'str'
    arrived_at: 'float'

# ################################################################################################################################
# ################################################################################################################################

class _RecordingHTTPHandler(BaseHTTPRequestHandler):
    """ Records each request on the receiver it serves and answers with the body the
    receiver is configured to answer with.
    """

    def _handle(self) -> 'None':

        server = cast_('any_', self.server)
        receiver = server.receiver

        content_length = self.headers['Content-Length']

        if content_length:
            body = self.rfile.read(int(content_length)).decode('utf-8')
        else:
            body = ''

        request = ReceivedRequest(self.command, self.path, body, time.monotonic())
        receiver.requests.append(request)

        # A slow receiver takes its time before answering
        if receiver.delay:
            time.sleep(receiver.delay)

        response_body = receiver.response_body.encode('utf-8')

        self.send_response(OK)
        self.send_header('Content-Type', receiver.content_type)
        self.send_header('Content-Length', str(len(response_body)))
        self.end_headers()
        _ = self.wfile.write(response_body)

    def do_GET(self) -> 'None':
        self._handle()

    def do_POST(self) -> 'None':
        self._handle()

    def do_PUT(self) -> 'None':
        self._handle()

    def do_PATCH(self) -> 'None':
        self._handle()

    def do_DELETE(self) -> 'None':
        self._handle()

    def log_message(self, message_format:'str', *args:'object') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class RESTReceiver:
    """ A plain HTTP receiving side recording every request it is sent, with a configurable
    answer and a configurable amount of time taken over each request when a test needs a
    slow receiver.
    """

    def __init__(
        self,
        response_body:'str' = _Default_Response_Body,
        content_type:'str' = _Default_Content_Type,
        delay:'float' = 0.0,
        ) -> 'None':

        self.response_body = response_body
        self.content_type = content_type
        self.delay = delay
        self.port = find_free_port()

        self.requests:'request_list' = []

        self._server:'any_' = None
        self._thread:'threading.Thread | None' = None

# ################################################################################################################################

    def start(self) -> 'None':
        """ Starts the receiver on its port, which stays the same across a stop and a start.
        """
        server = cast_('any_', ThreadingHTTPServer((_Host, self.port), _RecordingHTTPHandler))

        # The handler reads its receiver off the server it runs on
        server.receiver = self

        self._server = server

        self._thread = threading.Thread(target=server.serve_forever, daemon=True)
        self._thread.start()

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops the receiver, leaving its port free for a later start.
        """
        self._server.shutdown()
        self._server.server_close()
        self._server = None

# ################################################################################################################################
# ################################################################################################################################
