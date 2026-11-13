# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An HTTP client that sends requests as raw bytes over a socket and parses the raw responses,
# so that every byte the server sends back is available to the tests.

# stdlib
import base64
import json
import socket
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

Host = '127.0.0.1'

_socket_timeout = 30
_receive_size = 65536
_header_end = b'\r\n\r\n'
_line_end = b'\r\n'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class HTTPResponse:
    """ A response as it arrived - its status line, its headers in the order they arrived and its body.
    """
    http_version: str
    status: int
    reason: str
    header_list: 'list[tuple[str, str]]'
    headers: 'strdict'
    body: bytes

    @property
    def text(self) -> 'str':
        out = self.body.decode('utf-8')
        return out

    def json(self) -> 'any_':
        out = json.loads(self.body)
        return out

    def get_header_values(self, name:'str') -> 'strlist':
        """ Returns every value of a header, matched by its name case-insensitively.
        """
        name = name.lower()
        out:'strlist' = []

        for header_name, value in self.header_list:
            if header_name.lower() == name:
                out.append(value)

        return out

# ################################################################################################################################
# ################################################################################################################################

def _is_chunked(headers:'strdict') -> 'bool':
    """ Returns whether a response's body arrives in chunks.
    """
    if 'transfer-encoding' not in headers:
        return False

    out = headers['transfer-encoding'].lower() == 'chunked'
    return out

# ################################################################################################################################

def basic_auth_header(username:'str', password:'str') -> 'str':
    """ Returns the value of an Authorization header with Basic Auth credentials.
    """
    credentials = f'{username}:{password}'.encode('utf-8')
    encoded = base64.b64encode(credentials).decode('ascii')

    out = f'Basic {encoded}'
    return out

# ################################################################################################################################

def build_request(
    method:'str',
    path:'str',
    *,
    headers:'strdict | None' = None,
    body:'bytes' = b'',
    http_version:'str' = 'HTTP/1.1',
    needs_close:'bool' = True,
    needs_content_length:'bool' = True,
    ) -> 'bytes':
    """ Returns the raw bytes of a request.
    """
    lines = [f'{method} {path} {http_version}', f'Host: {Host}']

    if headers:
        for name, value in headers.items():
            lines.append(f'{name}: {value}')

    if needs_content_length:
        if body:
            lines.append(f'Content-Length: {len(body)}')

    if needs_close:
        lines.append('Connection: close')

    head = '\r\n'.join(lines) + '\r\n\r\n'

    out = head.encode('utf-8') + body
    return out

# ################################################################################################################################
# ################################################################################################################################

class ResponseReader:
    """ Reads responses from a connection one by one, keeping whatever arrived past the end of a response.
    """

    def __init__(self, connection:'socket.socket') -> 'None':
        self.connection = connection
        self.buffer = b''
        self.is_closed = False

    def _receive(self) -> 'None':
        data = self.connection.recv(_receive_size)
        if not data:
            self.is_closed = True
        self.buffer += data

    def _read_until(self, marker:'bytes') -> 'bytes':
        while marker not in self.buffer:
            if self.is_closed:
                raise Exception(f'Connection closed before {marker!r}, received {self.buffer!r}')
            self._receive()

        out, _, self.buffer = self.buffer.partition(marker)
        return out

    def _read_exactly(self, size:'int') -> 'bytes':
        while len(self.buffer) < size:
            if self.is_closed:
                raise Exception(f'Connection closed after {len(self.buffer)} of {size} bytes')
            self._receive()

        out = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return out

    def _read_to_close(self) -> 'bytes':
        while not self.is_closed:
            self._receive()

        out = self.buffer
        self.buffer = b''
        return out

    def _read_chunked(self) -> 'bytes':
        out = b''

        while True:
            size_line = self._read_until(_line_end)
            size_text, _, _ = size_line.partition(b';')
            size = int(size_text, 16)

            if size == 0:
                _ = self._read_until(_line_end)
                break

            out += self._read_exactly(size)
            _ = self._read_exactly(len(_line_end))

        return out

    def read_response(self, is_head:'bool' = False) -> 'HTTPResponse':
        """ Reads one complete response.
        """
        head = self._read_until(_header_end)
        lines = head.split(_line_end)

        status_line = lines[0].decode('latin-1')
        http_version, status, reason = status_line.split(' ', 2)

        out = HTTPResponse()
        out.http_version = http_version
        out.status = int(status)
        out.reason = reason
        out.header_list = []
        out.headers = {}

        for line in lines[1:]:
            name, _, value = line.decode('latin-1').partition(':')
            name = name.strip()
            value = value.strip()
            out.header_list.append((name, value))
            out.headers[name.lower()] = value

        if is_head:
            out.body = b''

        elif 'content-length' in out.headers:
            out.body = self._read_exactly(int(out.headers['content-length']))

        elif _is_chunked(out.headers):
            out.body = self._read_chunked()

        else:
            out.body = self._read_to_close()

        return out

# ################################################################################################################################
# ################################################################################################################################

class Connection:
    """ A connection to the server that requests can be sent over one after another.
    """

    def __init__(self, port:'int') -> 'None':
        self.socket = socket.create_connection((Host, port), timeout=_socket_timeout)
        self.reader = ResponseReader(self.socket)

    def send(self, data:'bytes') -> 'None':
        self.socket.sendall(data)

    def read_response(self, is_head:'bool' = False) -> 'HTTPResponse':
        out = self.reader.read_response(is_head)
        return out

    def exchange(self, data:'bytes', is_head:'bool' = False) -> 'HTTPResponse':
        self.send(data)
        out = self.read_response(is_head)
        return out

    def is_closed_by_server(self) -> 'bool':
        """ Returns whether the server has closed its side of the connection.
        """
        if self.reader.buffer:
            return False

        try:
            data = self.socket.recv(_receive_size)
        except ConnectionResetError:
            return True

        out = not data
        return out

    def close(self) -> 'None':
        self.socket.close()

# ################################################################################################################################
# ################################################################################################################################

class ChannelClient:
    """ Sends requests to the server, each over a connection of its own.
    """

    def __init__(self, port:'int') -> 'None':
        self.port = port

    def send_raw(self, data:'bytes', is_head:'bool' = False) -> 'HTTPResponse':
        connection = Connection(self.port)

        try:
            out = connection.exchange(data, is_head)
        finally:
            connection.close()

        return out

    def request(
        self,
        method:'str',
        path:'str',
        *,
        headers:'strdict | None' = None,
        body:'bytes' = b'',
        http_version:'str' = 'HTTP/1.1',
        ) -> 'HTTPResponse':

        data = build_request(method, path, headers=headers, body=body, http_version=http_version)
        is_head = method == 'HEAD'

        out = self.send_raw(data, is_head)
        return out

    def get(self, path:'str', headers:'strdict | None' = None) -> 'HTTPResponse':
        out = self.request('GET', path, headers=headers)
        return out

    def post_json(self, path:'str', data:'any_', headers:'strdict | None' = None) -> 'HTTPResponse':

        all_headers = {'Content-Type': 'application/json'}
        if headers:
            all_headers.update(headers)

        body = json.dumps(data).encode('utf-8')

        out = self.request('POST', path, headers=all_headers, body=body)
        return out

    def connect(self) -> 'Connection':
        out = Connection(self.port)
        return out

# ################################################################################################################################
# ################################################################################################################################
