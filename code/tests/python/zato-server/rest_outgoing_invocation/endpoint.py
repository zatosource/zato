# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The endpoint the outgoing REST invocation tests send their requests to. It listens on a plain HTTP port
# and on three HTTPS ports - one with a certificate for the loopback address, one with a certificate
# for another host name and one that requires a client certificate - records every request it receives
# and answers each path with the responses a test configured for it.

# stdlib
import gzip
import socket
import ssl
import struct
from dataclasses import dataclass, field as dc_field
from http.client import OK, responses as http_responses
from itertools import count

# gevent
from gevent import sleep as gevent_sleep
from gevent.server import StreamServer

# Test support
from endpoint_certificates import CertificateSet

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist

# ################################################################################################################################
# ################################################################################################################################

# The address every listener binds to
Host = '127.0.0.1'

# How much one receive call reads
_read_size = 65536

# The SO_LINGER value that makes a close send a reset instead of an orderly shutdown
_linger_reset = struct.pack('ii', 1, 0)

# How many bytes of a body are sent before a connection is cut during the response
_partial_body_size = 3

# ################################################################################################################################
# ################################################################################################################################

class CloseMode:
    """ How the endpoint ends a connection instead of completing a response.
    """
    Reset_Before_Response = 'reset-before-response'
    Close_Before_Response = 'close-before-response'
    Reset_During_Response = 'reset-during-response'
    Close_After_Response  = 'close-after-response'

# ################################################################################################################################
# ################################################################################################################################

header_list = list[tuple[str, str]]

@dataclass(init=False)
class EndpointResponse:
    """ One response the endpoint answers a request with.
    """
    status:  int
    reason:  str
    headers: header_list
    body:    bytes

    # Seconds to wait before the response is sent
    delay: float

    # The body is sent with chunked transfer encoding
    is_chunked: bool

    # The body is compressed with gzip and sent with the matching content encoding
    is_gzip: bool

    # The body is sent without a length, the end of the connection marking its end
    has_no_length: bool

    # The response carries `Connection: close` and the connection is closed after it
    needs_close: bool

    # How the connection is ended instead of, or after, a complete response - a CloseMode value or an empty string
    close_mode: str

    def __init__(
        self,
        status:'int'=OK,
        body:'bytes | str'=b'',
        *,
        reason:'str'='',
        headers:'header_list | None'=None,
        delay:'float'=0.0,
        is_chunked:'bool'=False,
        is_gzip:'bool'=False,
        has_no_length:'bool'=False,
        needs_close:'bool'=False,
        close_mode:'str'='',
        ) -> 'None':

        if isinstance(body, str):
            body = body.encode('utf8')

        if headers is None:
            headers = []

        if not reason:
            reason = http_responses[status]

        self.status = status
        self.reason = reason
        self.headers = headers
        self.body = body
        self.delay = delay
        self.is_chunked = is_chunked
        self.is_gzip = is_gzip
        self.has_no_length = has_no_length
        self.needs_close = needs_close
        self.close_mode = close_mode

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class RecordedRequest:
    """ One request the endpoint received, exactly as it arrived.
    """
    method:  str
    target:  str
    path:    str
    query:   str
    version: str
    headers: header_list = dc_field(default_factory=list)
    body:    bytes = b''

    # Which accepted connection the request arrived on and on which port
    connection_id: int = 0
    port:          int = 0

    # The common name of the client certificate the request was sent with, if any
    client_common_name: str = ''

# ################################################################################################################################

    def get_header(self, name:'str') -> 'str | None':
        """ Returns the value of the first header of the given name, compared case-insensitively, or None.
        """
        name = name.lower()

        for header_name, value in self.headers:
            if header_name.lower() == name:
                out = value
                break
        else:
            out = None

        return out

# ################################################################################################################################

    def get_header_list(self, name:'str') -> 'strlist':
        """ Returns the values of all the headers of the given name, compared case-insensitively.
        """
        name = name.lower()
        out:'strlist' = []

        for header_name, value in self.headers:
            if header_name.lower() == name:
                out.append(value)

        return out

# ################################################################################################################################
# ################################################################################################################################

recorded_request_list = list[RecordedRequest]
endpoint_response_list = list[EndpointResponse]

class TestEndpoint:
    """ The local endpoint of the suite - its listeners, the responses configured per path and the requests received.
    """

    def __init__(self, directory:'str') -> 'None':
        self.certificates = CertificateSet(directory)

        self.http_port = 0
        self.https_port = 0
        self.https_mismatch_port = 0
        self.https_mtls_port = 0

        self._servers:'list[StreamServer]' = []
        self._responses:'dict[str, endpoint_response_list]' = {}
        self._requests:'recorded_request_list' = []
        self._connection_ids = count(1)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Generates the certificates and starts all the listeners.
        """
        self.certificates.generate()

        # Plain HTTP ..
        self.http_port = self._start_server(None)

        # .. HTTPS with a certificate for the loopback address and for localhost ..
        context = self._new_server_context(self.certificates.server_cert_path, self.certificates.server_key_path)
        self.https_port = self._start_server(context)

        # .. HTTPS with a certificate that names a different host ..
        context = self._new_server_context(self.certificates.mismatch_cert_path, self.certificates.mismatch_key_path)
        self.https_mismatch_port = self._start_server(context)

        # .. and HTTPS that requires a client certificate issued by the client CA.
        context = self._new_server_context(self.certificates.server_cert_path, self.certificates.server_key_path)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(self.certificates.client_ca_path)
        self.https_mtls_port = self._start_server(context)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops all the listeners and removes the certificates.
        """
        for server in self._servers:
            server.stop()

        self.certificates.remove()

# ################################################################################################################################

    def _new_server_context(self, cert_path:'str', key_path:'str') -> 'ssl.SSLContext':
        out = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        out.load_cert_chain(cert_path, key_path)
        return out

# ################################################################################################################################

    def _start_server(self, context:'ssl.SSLContext | None') -> 'int':
        """ Starts one listener on a free port and returns the port.
        """
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((Host, 0))
        listener.listen(1024)

        if context:
            server = StreamServer(listener, self._handle_connection, ssl_context=context)
        else:
            server = StreamServer(listener, self._handle_connection)

        server.start()
        self._servers.append(server)

        out = listener.getsockname()[1]
        return out

# ################################################################################################################################

    @property
    def http_base(self) -> 'str':
        out = f'http://{Host}:{self.http_port}'
        return out

    @property
    def https_base(self) -> 'str':
        out = f'https://{Host}:{self.https_port}'
        return out

    @property
    def https_localhost_base(self) -> 'str':
        out = f'https://localhost:{self.https_port}'
        return out

    @property
    def https_mismatch_base(self) -> 'str':
        out = f'https://{Host}:{self.https_mismatch_port}'
        return out

    @property
    def https_mtls_base(self) -> 'str':
        out = f'https://{Host}:{self.https_mtls_port}'
        return out

# ################################################################################################################################

    def set_response(self, path:'str', response:'EndpointResponse') -> 'None':
        """ Answers every request for the path with the given response.
        """
        self._responses[path] = [response]

# ################################################################################################################################

    def set_responses(self, path:'str', responses:'endpoint_response_list') -> 'None':
        """ Answers consecutive requests for the path with consecutive responses, the last one answering all the remaining requests.
        """
        self._responses[path] = list(responses)

# ################################################################################################################################

    def get_requests(self, path:'str') -> 'recorded_request_list':
        """ Returns all the requests received for the path, oldest first.
        """
        out:'recorded_request_list' = []

        for item in self._requests:
            if item.path == path:
                out.append(item)

        return out

# ################################################################################################################################

    def get_request(self, path:'str') -> 'RecordedRequest':
        """ Returns the only request received for the path.
        """
        requests = self.get_requests(path)
        request_count = len(requests)

        if request_count != 1:
            raise Exception(f'Expected one request for `{path}`, received {request_count}')

        out = requests[0]
        return out

# ################################################################################################################################

    def _get_response(self, path:'str') -> 'EndpointResponse':
        """ Returns the response to answer the next request for the path with.
        """
        if responses := self._responses.get(path):
            response_count = len(responses)
            if response_count > 1:
                out = responses.pop(0)
            else:
                out = responses[0]

        # A path no test configured is answered with an empty 200 OK
        else:
            out = EndpointResponse()

        return out

# ################################################################################################################################

    def _handle_connection(self, sock:'any_', address:'any_') -> 'None':
        """ Serves the requests of one connection until either side ends it.
        """
        connection_id = next(self._connection_ids)
        port = sock.getsockname()[1]

        try:
            client_common_name = self._get_client_common_name(sock)
            buffer = b''

            while True:
                request, buffer = self._read_request(sock, buffer)
                if not request:
                    break

                request.connection_id = connection_id
                request.port = port
                request.client_common_name = client_common_name

                self._requests.append(request)

                response = self._get_response(request.path)
                needs_more = self._send_response(sock, request, response)

                if not needs_more:
                    break

        # A client that fails a TLS handshake or goes away mid-request ends the connection, which is all there is to do
        except (OSError, ssl.SSLError):
            pass

        finally:
            sock.close()

# ################################################################################################################################

    def _get_client_common_name(self, sock:'any_') -> 'str':
        """ Returns the common name of the client certificate of a TLS connection, or an empty string.
        """
        if not isinstance(sock, ssl.SSLSocket):
            return ''

        sock.do_handshake()
        peer_cert = sock.getpeercert()

        if not peer_cert:
            return ''

        for item in peer_cert['subject']:
            name, value = item[0]
            if name == 'commonName':
                out = value
                break
        else:
            out = ''

        return out

# ################################################################################################################################

    def _receive(self, sock:'any_', buffer:'bytes') -> 'bytes':
        """ Reads more bytes into the buffer, raising when the client closed the connection.
        """
        data = sock.recv(_read_size)

        if not data:
            raise ConnectionAbortedError('The client closed the connection')

        out = buffer + data
        return out

# ################################################################################################################################

    def _read_request(self, sock:'any_', buffer:'bytes') -> 'tuple[RecordedRequest | None, bytes]':
        """ Reads one complete request, returning it with whatever followed it in the buffer, or None when the client closed an idle connection.
        """
        # Read the head ..
        while b'\r\n\r\n' not in buffer:
            data = sock.recv(_read_size)
            if not data:
                return None, b''
            buffer += data

        head, buffer = buffer.split(b'\r\n\r\n', 1)
        lines = head.decode('latin1').split('\r\n')

        request_line = lines[0]
        method, target, version = request_line.split(' ')

        if '?' in target:
            path, query = target.split('?', 1)
        else:
            path = target
            query = ''

        # .. every header exactly as it was sent, an empty value included ..
        headers:'header_list' = []

        for line in lines[1:]:
            name, value = line.split(':', 1)
            value = value.strip(' \t')
            headers.append((name, value))

        request = RecordedRequest()
        request.method = method
        request.target = target
        request.path = path
        request.query = query
        request.version = version
        request.headers = headers

        # .. and the body, by its length or in chunks.
        content_length = request.get_header('Content-Length')
        transfer_encoding = request.get_header('Transfer-Encoding')

        if content_length is not None:
            length = int(content_length)
            while len(buffer) < length:
                buffer = self._receive(sock, buffer)
            request.body = buffer[:length]
            buffer = buffer[length:]

        elif transfer_encoding == 'chunked':
            request.body, buffer = self._read_chunked_body(sock, buffer)

        out = request, buffer
        return out

# ################################################################################################################################

    def _read_chunked_body(self, sock:'any_', buffer:'bytes') -> 'tuple[bytes, bytes]':
        """ Reads a body sent with chunked transfer encoding, returning it with whatever followed it.
        """
        body = b''

        while True:

            # The size of the next chunk ..
            while b'\r\n' not in buffer:
                buffer = self._receive(sock, buffer)

            size_line, buffer = buffer.split(b'\r\n', 1)
            size = int(size_line.split(b';')[0], 16)

            # .. the chunk itself followed by its line end ..
            while len(buffer) < size + 2:
                buffer = self._receive(sock, buffer)

            body += buffer[:size]
            buffer = buffer[size + 2:]

            # .. and the last chunk is the empty one.
            if size == 0:
                break

        out = body, buffer
        return out

# ################################################################################################################################

    def _reset(self, sock:'any_') -> 'None':
        """ Closes a connection with a reset rather than with an orderly shutdown.
        """
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, _linger_reset)
        sock.close()

# ################################################################################################################################

    def _send_response(self, sock:'any_', request:'RecordedRequest', response:'EndpointResponse') -> 'bool':
        """ Sends one response and returns whether the connection stays open for another request.
        """
        if response.delay:
            gevent_sleep(response.delay)

        # A connection that ends before a response ends here ..
        if response.close_mode == CloseMode.Reset_Before_Response:
            self._reset(sock)
            return False

        if response.close_mode == CloseMode.Close_Before_Response:
            sock.close()
            return False

        body = response.body

        if response.is_gzip:
            body = gzip.compress(body)

        # .. otherwise, the head is built ..
        head_lines = [f'HTTP/1.1 {response.status} {response.reason}']

        for name, value in response.headers:
            head_lines.append(f'{name}: {value}')

        if response.is_gzip:
            head_lines.append('Content-Encoding: gzip')

        if response.is_chunked:
            head_lines.append('Transfer-Encoding: chunked')

        elif not response.has_no_length:
            head_lines.append(f'Content-Length: {len(body)}')

        client_closes = request.get_header('Connection') == 'close'
        needs_close = response.needs_close or response.has_no_length or client_closes

        if response.needs_close:
            head_lines.append('Connection: close')

        head = '\r\n'.join(head_lines) + '\r\n\r\n'
        head = head.encode('latin1')

        # .. a connection cut during the response sends part of the body, as one complete chunk if the body is chunked, and a reset ..
        if response.close_mode == CloseMode.Reset_During_Response:
            partial_body = body[:_partial_body_size]
            if response.is_chunked:
                partial_body = f'{len(partial_body):x}\r\n'.encode('ascii') + partial_body + b'\r\n'
            sock.sendall(head + partial_body)
            gevent_sleep(0.05)
            self._reset(sock)
            return False

        # .. a chunked body goes in two chunks and the terminating one ..
        if response.is_chunked:
            middle = len(body) // 2
            payload = head
            for chunk in (body[:middle], body[middle:]):
                if chunk:
                    payload += f'{len(chunk):x}\r\n'.encode('ascii') + chunk + b'\r\n'
            payload += b'0\r\n\r\n'

        # .. and any other body goes as it is.
        else:
            payload = head + body

        sock.sendall(payload)

        if response.close_mode == CloseMode.Close_After_Response:
            return False

        out = not needs_close
        return out

# ################################################################################################################################
# ################################################################################################################################

class UnresponsiveListener:
    """ A listener whose accept queue is full and which never accepts anything, so a connection attempt to it
    does not complete until the client gives up.
    """

    def __init__(self) -> 'None':
        self.port = 0
        self._listener:'socket.socket | None' = None
        self._fillers:'list[socket.socket]' = []

# ################################################################################################################################

    def start(self) -> 'None':
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind((Host, 0))
        listener.listen(0)

        self.port = listener.getsockname()[1]
        self._listener = listener

        # The accept queue holds a backlog's worth of connections plus one, after which the kernel drops further attempts.
        for _ in range(4):
            filler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            filler.setblocking(False)
            _ = filler.connect_ex((Host, self.port))
            self._fillers.append(filler)

        gevent_sleep(0.1)

# ################################################################################################################################

    def stop(self) -> 'None':
        for filler in self._fillers:
            filler.close()

        if self._listener:
            self._listener.close()

# ################################################################################################################################

    @property
    def base(self) -> 'str':
        out = f'http://{Host}:{self.port}'
        return out

# ################################################################################################################################
# ################################################################################################################################
