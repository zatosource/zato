# -*- coding: utf-8 -*-

import socket
import threading
import pytest


class _FakeSocket:
    def __init__(self, sock):
        self._sock = sock
    def fileno(self):
        return self._sock.fileno()
    def close(self):
        self._sock.close()


def _run_handler(handler, server_sock, address):
    fake = _FakeSocket(server_sock)
    try:
        handler.handle(fake, address)
    except Exception:
        pass
    finally:
        server_sock.close()


class TestHttpEnviron:

    def _send_and_capture(self, socketpair_with_handler, recording_callback,
                          send_http_request, read_http_response,
                          method='GET', path='/', headers=None, body=b'',
                          remote_addr='10.0.0.1', remote_port=54321):
        headers = headers or {}
        headers.setdefault('Host', 'localhost')
        headers['Connection'] = 'close'

        client, server, handler = socketpair_with_handler(recording_callback)
        address = (remote_addr, remote_port)

        t = threading.Thread(target=_run_handler, args=(handler, server, address))
        t.start()

        send_http_request(client, method, path, headers=headers, body=body)
        read_http_response(client)
        client.close()
        t.join(timeout=5)

        assert len(recording_callback.recorded) == 1
        return recording_callback.recorded[0]

    def test_all_standard_cgi_keys_present(self, socketpair_with_handler, recording_callback,
                                           send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     method='POST', path='/test',
                                     headers={'Content-Type': 'application/json'},
                                     body=b'{}')

        required_keys = [
            'REQUEST_METHOD', 'PATH_INFO', 'QUERY_STRING', 'SERVER_PROTOCOL',
            'CONTENT_TYPE', 'CONTENT_LENGTH', 'REMOTE_ADDR', 'REMOTE_PORT',
        ]
        for key in required_keys:
            assert key in env, f'Missing key: {key}'

    def test_request_method(self, socketpair_with_handler, recording_callback,
                            send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     method='DELETE', path='/')
        assert env['REQUEST_METHOD'] == 'DELETE'

    def test_path_info(self, socketpair_with_handler, recording_callback,
                       send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     path='/my/api/endpoint')
        assert env['PATH_INFO'] == '/my/api/endpoint'

    def test_query_string(self, socketpair_with_handler, recording_callback,
                          send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     path='/search?q=hello&page=2')
        assert env['QUERY_STRING'] == 'q=hello&page=2'

    def test_raw_uri_includes_query(self, socketpair_with_handler, recording_callback,
                                    send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     path='/path?key=val')
        assert env['RAW_URI'] == '/path?key=val'

    def test_server_protocol(self, socketpair_with_handler, recording_callback,
                             send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response)
        assert env['SERVER_PROTOCOL'] == 'HTTP/1.1'

    def test_remote_addr_and_port(self, socketpair_with_handler, recording_callback,
                                  send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     remote_addr='192.168.1.100', remote_port=9876)
        assert env['REMOTE_ADDR'] == '192.168.1.100'
        assert env['REMOTE_PORT'] == '9876'

    def test_http_host_header(self, socketpair_with_handler, recording_callback,
                              send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     headers={'Host': 'example.com:8080'})
        assert env['HTTP_HOST'] == 'example.com:8080'

    def test_http_user_agent(self, socketpair_with_handler, recording_callback,
                             send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     headers={'User-Agent': 'MyApp/2.0'})
        assert env['HTTP_USER_AGENT'] == 'MyApp/2.0'

    def test_custom_header_normalization(self, socketpair_with_handler, recording_callback,
                                         send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     headers={'X-Zato-Foo': 'bar'})
        assert env['HTTP_X_ZATO_FOO'] == 'bar'

    def test_missing_content_type(self, socketpair_with_handler, recording_callback,
                                  send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response)
        assert env['CONTENT_TYPE'] == ''

    def test_empty_body(self, socketpair_with_handler, recording_callback,
                        send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response)
        assert env['zato.http.raw_request'] == b''

    def test_body_is_bytes(self, socketpair_with_handler, recording_callback,
                           send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     method='POST',
                                     headers={'Content-Type': 'text/plain'},
                                     body=b'payload data')
        assert isinstance(env['zato.http.raw_request'], bytes)
        assert env['zato.http.raw_request'] == b'payload data'

    def test_request_method_is_str(self, socketpair_with_handler, recording_callback,
                                   send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response)
        assert isinstance(env['REQUEST_METHOD'], str)

    def test_header_values_are_str(self, socketpair_with_handler, recording_callback,
                                   send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     headers={'Accept': 'text/html', 'Authorization': 'Basic abc'})
        assert isinstance(env['HTTP_ACCEPT'], str)
        assert isinstance(env['HTTP_AUTHORIZATION'], str)

    def test_content_type_with_body(self, socketpair_with_handler, recording_callback,
                                   send_http_request, read_http_response):
        env = self._send_and_capture(socketpair_with_handler, recording_callback,
                                     send_http_request, read_http_response,
                                     method='POST',
                                     headers={'Content-Type': 'application/json'},
                                     body=b'{"a":1}')
        assert env['CONTENT_TYPE'] == 'application/json'
