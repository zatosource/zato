# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from typing import NamedTuple

# gevent
from gevent.pywsgi import WSGIServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_

# ################################################################################################################################
# ################################################################################################################################

# The address that the endpoints listen on, with a port that the operating system assigns.
_host = '127.0.0.1'
_any_port = 0

# The headers of a push request that identify the message and its attempt, as WSGI names them.
_header_msg_id = 'HTTP_X_ZATO_MSG_ID'
_header_attempt = 'HTTP_X_ZATO_DELIVERY_ATTEMPT'

# The keys of an envelope that identify the message and its attempt, which a push of several messages carries
# in each envelope rather than in the headers.
_envelope_msg_id = 'msg_id'
_envelope_attempt = 'delivery_attempt'

# The responses of an endpoint that accepted a push and of one that rejected it.
_status_accepted = '200 OK'
_status_rejected = '500 Internal Server Error'
_response_headers = [('Content-Type', 'application/json')]
_response_body = [b'{}']

# How long the endpoints are given to complete the requests in progress when they stop, in seconds.
_stop_timeout = 1

# ################################################################################################################################
# ################################################################################################################################

class Push(NamedTuple):
    """ One push request that reached an endpoint - its path, the message and its attempt, and the message as pushed.
    """
    path: 'str'
    msg_id: 'str'
    attempt: 'int'
    envelope: 'anydict'

# ################################################################################################################################
# ################################################################################################################################

class PushReceiver:
    """ The local HTTP endpoints that a server pushes messages to. Each push is handed to a handler, which returns
    whether the endpoint accepts it, and the endpoint responds with HTTP 200 or HTTP 500 accordingly. A push of several
    messages, a JSON list of envelopes, hands each message to the handler and is answered with HTTP 200
    and the JSON list of the IDs of the messages that the handler accepted.
    """

    def __init__(self, handler:'callable_') -> 'None':
        self.handler = handler
        self.port = 0
        self._server:'any_' = None

# ################################################################################################################################

    def _handle(self, environ:'anydict', start_response:'callable_') -> 'anylist':

        # The body is read in full, as a real endpoint reads it ..
        body = environ['wsgi.input'].read()
        document = json.loads(body)

        # .. a list of envelopes is handled message by message ..
        if isinstance(document, list):
            out = self._handle_list(environ['PATH_INFO'], document, start_response)
            return out

        push = Push(
            path=environ['PATH_INFO'],
            msg_id=environ[_header_msg_id],
            attempt=int(environ[_header_attempt]),
            envelope=document,
        )

        # .. the handler decides whether the endpoint accepts the push ..
        is_accepted = self.handler(push)

        # .. and the response tells the server how it went.
        if is_accepted:
            start_response(_status_accepted, _response_headers)
        else:
            start_response(_status_rejected, _response_headers)

        return _response_body

# ################################################################################################################################

    def _handle_list(self, path:'str', envelopes:'anylist', start_response:'callable_') -> 'anylist':
        """ Hands each message of a push of several messages to the handler and responds with the IDs it accepted.
        """
        accepted:'anylist' = []

        for envelope in envelopes:
            push = Push(
                path=path,
                msg_id=envelope[_envelope_msg_id],
                attempt=envelope[_envelope_attempt],
                envelope=envelope,
            )

            if self.handler(push):
                accepted.append(push.msg_id)

        start_response(_status_accepted, _response_headers)

        out = [json.dumps(accepted).encode('utf8')]
        return out

# ################################################################################################################################

    def start(self) -> 'None':
        self._server = WSGIServer((_host, _any_port), self._handle, log=None, error_log=None)
        self._server.start()
        self.port = self._server.server_port

# ################################################################################################################################

    def stop(self) -> 'None':
        self._server.stop(timeout=_stop_timeout)

# ################################################################################################################################
# ################################################################################################################################
