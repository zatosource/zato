# -*- coding: utf-8 -*-

import socket
import threading
import pytest


class _FakeSocket:
    """Wraps a real socket to provide fileno() as expected by ConnectionHandler."""
    def __init__(self, sock):
        self._sock = sock

    def fileno(self):
        return self._sock.fileno()

    def close(self):
        self._sock.close()


def _run_handler_in_thread(handler, server_sock, address):
    fake = _FakeSocket(server_sock)
    try:
        handler.handle(fake, address)
    except Exception:
        pass
    finally:
        server_sock.close()


class TestConnectionHandler:

    def test_basic_get(self, socketpair_with_handler, echo_callback, send_http_request, read_http_response):
        client, server, handler = socketpair_with_handler(echo_callback)
        address = ('127.0.0.1', 12345)

        t = threading.Thread(target=_run_handler_in_thread, args=(handler, server, address))
        t.start()

        send_http_request(client, 'GET', '/', headers={'Host': 'localhost', 'Connection': 'close'})
        resp = read_http_response(client)
        client.close()
        t.join(timeout=5)

        assert '200 OK' in resp['status_line']

    def test_post_body(self, socketpair_with_handler, echo_callback, send_http_request, read_http_response):
        client, server, handler = socketpair_with_handler(echo_callback)
        address = ('127.0.0.1', 12345)

        t = threading.Thread(target=_run_handler_in_thread, args=(handler, server, address))
        t.start()

        body = b'hello world'
        send_http_request(client, 'POST', '/api', headers={
            'Host': 'localhost',
            'Content-Type': 'application/json',
            'Connection': 'close',
        }, body=body)

        resp = read_http_response(client)
        client.close()
        t.join(timeout=5)

        assert '200 OK' in resp['status_line']
        assert resp['body'] == body

    def test_callback_receives_correct_environ(self, socketpair_with_handler, recording_callback, send_http_request, read_http_response):
        client, server, handler = socketpair_with_handler(recording_callback)
        address = ('127.0.0.1', 55555)

        t = threading.Thread(target=_run_handler_in_thread, args=(handler, server, address))
        t.start()

        send_http_request(client, 'GET', '/test?q=1', headers={
            'Host': 'example.com',
            'User-Agent': 'pytest',
            'Connection': 'close',
        })
        resp = read_http_response(client)
        client.close()
        t.join(timeout=5)

        assert len(recording_callback.recorded) == 1
        env = recording_callback.recorded[0]
        assert env['REQUEST_METHOD'] == 'GET'
        assert env['PATH_INFO'] == '/test'
        assert env['QUERY_STRING'] == 'q=1'
        assert env['HTTP_HOST'] == 'example.com'
        assert env['HTTP_USER_AGENT'] == 'pytest'
        assert env['REMOTE_ADDR'] == '127.0.0.1'
        assert env['REMOTE_PORT'] == '55555'

    def test_keepalive_two_requests(self, socketpair_with_handler, recording_callback, send_http_request, read_http_response):
        client, server, handler = socketpair_with_handler(recording_callback)
        address = ('127.0.0.1', 9999)

        t = threading.Thread(target=_run_handler_in_thread, args=(handler, server, address))
        t.start()

        send_http_request(client, 'GET', '/first', headers={'Host': 'localhost'})
        resp1 = read_http_response(client)
        assert '200 OK' in resp1['status_line']

        send_http_request(client, 'GET', '/second', headers={'Host': 'localhost', 'Connection': 'close'})
        resp2 = read_http_response(client)
        client.close()
        t.join(timeout=5)

        assert '200 OK' in resp2['status_line']
        assert len(recording_callback.recorded) == 2
        assert recording_callback.recorded[0]['PATH_INFO'] == '/first'
        assert recording_callback.recorded[1]['PATH_INFO'] == '/second'

    def test_callback_exception_returns_500(self, socketpair_with_handler, error_callback, send_http_request, read_http_response):
        client, server, handler = socketpair_with_handler(error_callback)
        address = ('127.0.0.1', 12345)

        t = threading.Thread(target=_run_handler_in_thread, args=(handler, server, address))
        t.start()

        send_http_request(client, 'GET', '/', headers={'Host': 'localhost', 'Connection': 'close'})
        resp = read_http_response(client)
        client.close()
        t.join(timeout=5)

        assert '500' in resp['status_line']

    def test_callback_wrong_return_type(self, socketpair_with_handler, send_http_request, read_http_response):
        def bad_callback(http_environ):
            return 'not a tuple'

        client, server, handler = socketpair_with_handler(bad_callback)
        address = ('127.0.0.1', 12345)

        t = threading.Thread(target=_run_handler_in_thread, args=(handler, server, address))
        t.start()

        send_http_request(client, 'GET', '/', headers={'Host': 'localhost', 'Connection': 'close'})
        resp = read_http_response(client)
        client.close()
        t.join(timeout=5)

        assert '500' in resp['status_line']

    def test_large_body(self, socketpair_with_handler, echo_callback, send_http_request, read_http_response):
        client, server, handler = socketpair_with_handler(echo_callback)
        address = ('127.0.0.1', 12345)

        t = threading.Thread(target=_run_handler_in_thread, args=(handler, server, address))
        t.start()

        body = b'X' * 65536
        send_http_request(client, 'POST', '/big', headers={
            'Host': 'localhost',
            'Connection': 'close',
        }, body=body)

        resp = read_http_response(client)
        client.close()
        t.join(timeout=5)

        assert '200 OK' in resp['status_line']
        assert resp['body'] == body

    def test_server_software_attribute(self, socketpair_with_handler, echo_callback):
        from zato_server_core import ConnectionHandler
        handler = ConnectionHandler(echo_callback, 'Zato/4.1')
        assert handler.server_software == 'Zato/4.1'

    def test_headers_case_normalization(self, socketpair_with_handler, recording_callback, send_http_request, read_http_response):
        client, server, handler = socketpair_with_handler(recording_callback)
        address = ('127.0.0.1', 12345)

        t = threading.Thread(target=_run_handler_in_thread, args=(handler, server, address))
        t.start()

        send_http_request(client, 'GET', '/', headers={
            'accept-encoding': 'gzip',
            'x-custom-header': 'value',
            'Connection': 'close',
        })
        resp = read_http_response(client)
        client.close()
        t.join(timeout=5)

        env = recording_callback.recorded[0]
        assert env['HTTP_ACCEPT_ENCODING'] == 'gzip'
        assert env['HTTP_X_CUSTOM_HEADER'] == 'value'
