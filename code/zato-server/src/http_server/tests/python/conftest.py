# -*- coding: utf-8 -*-

import socket
import struct
import pytest


def _send_http_request(sock, method, path, headers=None, body=b''):
    headers = headers or {}
    lines = [f'{method} {path} HTTP/1.1']
    if body:
        headers.setdefault('Content-Length', str(len(body)))
    for k, v in headers.items():
        lines.append(f'{k}: {v}')
    lines.append('')
    lines.append('')
    raw = '\r\n'.join(lines).encode('utf-8')
    sock.sendall(raw + body)


def _read_http_response(sock, timeout=5.0):
    sock.settimeout(timeout)
    chunks = []
    headers_done = False
    content_length = 0
    header_data = b''
    body_data = b''

    while True:
        try:
            data = sock.recv(65536)
        except socket.timeout:
            break
        if not data:
            break
        chunks.append(data)
        combined = b''.join(chunks)

        if not headers_done:
            sep = combined.find(b'\r\n\r\n')
            if sep >= 0:
                headers_done = True
                header_data = combined[:sep]
                body_data = combined[sep + 4:]

                for line in header_data.split(b'\r\n'):
                    lower = line.lower()
                    if lower.startswith(b'content-length:'):
                        content_length = int(line.split(b':', 1)[1].strip())

                if len(body_data) >= content_length:
                    break
        else:
            body_data = combined[len(header_data) + 4:]
            if len(body_data) >= content_length:
                break

    status_line = header_data.split(b'\r\n')[0].decode('utf-8') if header_data else ''
    return {
        'status_line': status_line,
        'headers_raw': header_data.decode('utf-8', errors='replace') if header_data else '',
        'body': body_data[:content_length] if headers_done else b''.join(chunks),
    }


@pytest.fixture
def send_http_request():
    return _send_http_request


@pytest.fixture
def read_http_response():
    return _read_http_response


@pytest.fixture
def echo_callback():
    def _callback(http_environ):
        body = http_environ.get('zato.http.raw_request', b'')
        if isinstance(body, str):
            body = body.encode('utf-8')
        return ('200 OK', {'Content-Type': 'text/plain'}, body)
    return _callback


@pytest.fixture
def error_callback():
    def _callback(http_environ):
        raise RuntimeError('intentional error')
    return _callback


@pytest.fixture
def recording_callback():
    recorded = []
    def _callback(http_environ):
        recorded.append(dict(http_environ))
        body = http_environ.get('zato.http.raw_request', b'')
        if isinstance(body, str):
            body = body.encode('utf-8')
        return ('200 OK', {'Content-Type': 'text/plain'}, body)
    _callback.recorded = recorded
    return _callback


@pytest.fixture
def socketpair_with_handler():
    from zato_server_core import ConnectionHandler

    def _make(callback, server_software='Zato/test'):
        handler = ConnectionHandler(callback, server_software)
        client_sock, server_sock = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        return client_sock, server_sock, handler

    return _make
