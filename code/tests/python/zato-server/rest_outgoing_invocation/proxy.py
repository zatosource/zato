# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The HTTP proxy the outgoing REST invocation tests send their requests through. It records the head of every request
# it receives, answers a request in absolute form itself, opens a tunnel to the requested endpoint for CONNECT,
# and refuses a request without the expected credentials when it requires them.

# stdlib
import socket

# gevent
from gevent import spawn
from gevent.server import StreamServer

# Test support
from endpoint import Host, RecordedRequest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

# The body the proxy answers a request in absolute form with
Proxy_Response_Body = b'Proxy response'

# How much one receive call reads
_read_size = 65536

# What the proxy answers a CONNECT request it accepts with
_tunnel_established = b'HTTP/1.1 200 Connection established\r\n\r\n'

# What the proxy answers a request without the expected credentials with
_authentication_required = b'HTTP/1.1 407 Proxy Authentication Required\r\nContent-Length: 0\r\nConnection: close\r\n\r\n'

# ################################################################################################################################
# ################################################################################################################################

recorded_request_list = list[RecordedRequest]

class TestProxy:
    """ A local HTTP proxy that records the requests it receives.
    """

    def __init__(self, authorization:'strnone'=None) -> 'None':

        # The value of the Proxy-Authorization header the proxy requires, if any
        self.authorization = authorization

        self.port = 0
        self.requests:'recorded_request_list' = []

        self._server:'StreamServer | None' = None

# ################################################################################################################################

    def start(self) -> 'None':
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((Host, 0))
        listener.listen(1024)

        self._server = StreamServer(listener, self._handle_connection)
        self._server.start()

        self.port = listener.getsockname()[1]

# ################################################################################################################################

    def stop(self) -> 'None':
        if self._server:
            self._server.stop()

# ################################################################################################################################

    def url(self, credentials:'str'='') -> 'str':
        """ The address of the proxy, with the given credentials in it if there are any.
        """
        if credentials:
            out = f'http://{credentials}@{Host}:{self.port}'
        else:
            out = f'http://{Host}:{self.port}'

        return out

# ################################################################################################################################

    def _handle_connection(self, sock:'any_', address:'any_') -> 'None':
        """ Serves the requests of one connection until either side ends it or the connection becomes a tunnel.
        """
        buffer = b''

        try:
            while True:
                request, buffer = self._read_request(sock, buffer)
                if request is None:
                    return

                self.requests.append(request)

                if self.authorization is not None:
                    if request.get_header('Proxy-Authorization') != self.authorization:
                        sock.sendall(_authentication_required)
                        return

                if request.method == 'CONNECT':
                    self._tunnel(sock, request.target)
                    return

                response = b'HTTP/1.1 200 OK\r\nContent-Length: %d\r\n\r\n' % len(Proxy_Response_Body)
                sock.sendall(response + Proxy_Response_Body)

        except OSError:
            pass

        finally:
            sock.close()

# ################################################################################################################################

    def _read_request(self, sock:'any_', buffer:'bytes') -> 'tuple[RecordedRequest | None, bytes]':
        """ Reads one request, returning it with whatever followed it, or None when the client closed the connection.
        """
        while b'\r\n\r\n' not in buffer:
            data = sock.recv(_read_size)
            if not data:
                return None, b''
            buffer += data

        head, buffer = buffer.split(b'\r\n\r\n', 1)
        lines = head.decode('latin1').split('\r\n')

        method, target, version = lines[0].split(' ')

        request = RecordedRequest()
        request.method = method
        request.target = target
        request.path = target
        request.query = ''
        request.version = version
        request.headers = []

        for line in lines[1:]:
            name, value = line.split(':', 1)
            request.headers.append((name, value.strip(' \t')))

        if content_length := request.get_header('Content-Length'):
            length = int(content_length)
            while len(buffer) < length:
                data = sock.recv(_read_size)
                if not data:
                    return None, b''
                buffer += data

            request.body = buffer[:length]
            buffer = buffer[length:]

        out = request, buffer
        return out

# ################################################################################################################################

    def _tunnel(self, sock:'any_', target:'str') -> 'None':
        """ Opens a tunnel to the endpoint a CONNECT request names and relays the bytes of both sides until one of them closes.
        """
        host, port = target.rsplit(':', 1)
        upstream = socket.create_connection((host.strip('[]'), int(port)))

        sock.sendall(_tunnel_established)

        relay = spawn(self._relay, upstream, sock)
        self._relay(sock, upstream)

        _ = relay.join()
        upstream.close()

# ################################################################################################################################

    def _relay(self, source:'any_', destination:'any_') -> 'None':
        """ Copies bytes from one side of a tunnel to the other until the source closes.
        """
        try:
            while data := source.recv(_read_size):
                destination.sendall(data)
        except OSError:
            pass

        try:
            destination.shutdown(socket.SHUT_WR)
        except OSError:
            pass

# ################################################################################################################################
# ################################################################################################################################
