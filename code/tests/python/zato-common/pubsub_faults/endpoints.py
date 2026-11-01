# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Push endpoints of item 15.12, each a TCP server of its own that reads and answers HTTP requests itself, so that it can
# read a request one byte per second, never respond, respond after the delivery timeout, close the connection
# in the middle of a response, stall the TLS handshake or redirect.

# stdlib
from dataclasses import dataclass
from http.client import OK, responses, TEMPORARY_REDIRECT
from time import monotonic

# gevent
from gevent import sleep
from gevent.server import StreamServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent.socket import socket
    from zato.common.typing_ import any_, intnone, strstrdict

    request_head = tuple[strstrdict, bytes]

# ################################################################################################################################
# ################################################################################################################################

_host = '127.0.0.1'

# The behaviors of the endpoints.
Behavior_Normal      = 'normal'
Behavior_Slow_Reader = 'slow-reader'
Behavior_Silent      = 'silent'
Behavior_Late_OK     = 'late-ok'
Behavior_Mid_Close   = 'mid-close'
Behavior_TLS_Stall   = 'tls-stall'
Behavior_Redirect    = 'redirect'

# How long a silent endpoint or a stalled TLS handshake holds a connection, how long a late response takes,
# which is beyond the timeout of the delivery, and how often a slow reader reads one byte, in seconds.
_hold_seconds = 3600
_late_response_seconds = 12
_slow_read_seconds = 1

_read_size = 65536

# The responses - a complete one, one that ends in the middle of its body, and a redirect to another endpoint.
_response_ok = f'HTTP/1.1 {OK} {responses[OK]}\r\nContent-Type: application/json\r\nContent-Length: 2\r\n' + \
    'Connection: close\r\n\r\n{}'

_response_partial = f'HTTP/1.1 {OK} {responses[OK]}\r\nContent-Type: application/json\r\nContent-Length: 100\r\n' + \
    '\r\n{"part'

_response_redirect = f'HTTP/1.1 {TEMPORARY_REDIRECT} {responses[TEMPORARY_REDIRECT]}\r\nLocation: http://{_host}:{{}}/\r\n' + \
    'Content-Length: 0\r\nConnection: close\r\n\r\n'

_header_msg_id = 'x-zato-msg-id'
_header_attempt = 'x-zato-delivery-attempt'
_header_length = 'content-length'

_header_end = b'\r\n\r\n'
_encoding = 'latin1'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class EndpointRequest:
    """ One request that an endpoint received - a stalled TLS handshake records a connection without a message.
    """
    msg_id: 'str'
    attempt: 'int'
    received_at: 'float'
    is_accepted: 'bool'

requestlist = list[EndpointRequest]

# ################################################################################################################################
# ################################################################################################################################

def _read_head(client:'socket') -> 'request_head | None':
    """ Reads the request line and the headers, returning the headers by their lowercase names
    and what was read of the body, or None if the client closed the connection first.
    """
    data = b''

    while _header_end not in data:
        chunk = client.recv(_read_size)
        if not chunk:
            return None
        data += chunk

    head, body = data.split(_header_end, 1)
    lines = head.decode(_encoding).split('\r\n')

    headers:'strstrdict' = {}

    for line in lines[1:]:
        name, value = line.split(':', 1)
        name = name.strip().lower()
        headers[name] = value.strip()

    out = headers, body
    return out

# ################################################################################################################################

def _send(client:'socket', response:'str') -> 'None':
    data = response.encode(_encoding)
    client.sendall(data)

# ################################################################################################################################
# ################################################################################################################################

class Endpoint:
    """ One push endpoint with one behavior, which a misbehaving endpoint applies to the first attempt
    of each message only, apart from a silent one, a stalled TLS handshake and a redirect, which apply it to every attempt.
    """

    def __init__(self, name:'str', behavior:'str', redirect_port:'intnone'=None) -> 'None':
        self.name = name
        self.behavior = behavior
        self.redirect_port = redirect_port
        self.requests:'requestlist' = []

        self.server = StreamServer((_host, 0), self._handle)
        self.server.start()

        port = self.server.server_port
        assert port is not None
        self.port = port

# ################################################################################################################################

    def stop(self) -> 'None':
        self.server.stop(timeout=1)

# ################################################################################################################################

    def _read_body(self, client:'socket', headers:'strstrdict', body:'bytes', is_slow:'bool') -> 'bool':
        """ Reads the rest of the body, one byte at a time if slowly, and returns whether it was read in full.
        """
        length = int(headers[_header_length])
        remaining = length - len(body)

        while remaining > 0:

            if is_slow:
                sleep(_slow_read_seconds)
                chunk = client.recv(1)
            else:
                read_size = min(remaining, _read_size)
                chunk = client.recv(read_size)

            if not chunk:
                return False

            remaining -= len(chunk)

        return True

# ################################################################################################################################

    def _respond_late(self, client:'socket', request:'EndpointRequest') -> 'None':
        """ Processes the message after the delivery gave up waiting and closed the connection.
        """
        sleep(_late_response_seconds)
        request.is_accepted = True

        try:
            _send(client, _response_ok)
        except OSError:
            pass

# ################################################################################################################################

    def _handle(self, client:'socket', address:'any_') -> 'None':

        request = EndpointRequest()
        request.msg_id = ''
        request.attempt = 0
        request.received_at = monotonic()
        request.is_accepted = False

        # A stalled handshake never reads what the client sends ..
        if self.behavior == Behavior_TLS_Stall:
            self.requests.append(request)
            sleep(_hold_seconds)
            return

        head = _read_head(client)
        if head is None:
            return

        headers, body = head

        request.msg_id = headers[_header_msg_id]
        request.attempt = int(headers[_header_attempt])
        self.requests.append(request)

        is_first = request.attempt == 1

        # .. each other endpoint reads the body, slowly if it is a slow reader, whom the delivery gives up on ..
        is_slow = False

        if self.behavior == Behavior_Slow_Reader:
            is_slow = is_first

        if not self._read_body(client, headers, body, is_slow):
            return

        # .. and responds as it behaves - a silent one never ..
        if self.behavior == Behavior_Silent:
            sleep(_hold_seconds)
            return

        # .. a redirect sends the delivery to another endpoint ..
        if self.behavior == Behavior_Redirect:
            response = _response_redirect.format(self.redirect_port)
            _send(client, response)
            return

        # .. the first attempt receives a late or a partial response ..
        if is_first:

            if self.behavior == Behavior_Late_OK:
                self._respond_late(client, request)
                return

            if self.behavior == Behavior_Mid_Close:
                _send(client, _response_partial)
                return

        # .. and anything else is accepted.
        request.is_accepted = True
        _send(client, _response_ok)

# ################################################################################################################################
# ################################################################################################################################
