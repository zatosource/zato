# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import time
import traceback
from http.client import HTTPConnection
from multiprocessing import get_context

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple

    anydict = anydict
    anytuple = anytuple

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    Host = '127.0.0.1'

    # MAX_REQUESTS_PER_CONNECTION of zato_server_core
    Max_Requests_Per_Connection = 1000

    # The largest request that the server of the test accepts, in bytes
    Max_Msg_Size = 1_000_000

    # How long the client waits for the server to listen and for each response, in seconds
    Connect_Timeout = 20.0
    Response_Timeout = 10.0
    Connect_Interval = 0.05

    # How long the test waits for the server process to exit, in seconds
    Join_Timeout = 20.0

# ################################################################################################################################
# ################################################################################################################################

def _get_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ModuleCtx.Host, 0))
        out = sock.getsockname()[1]

    return out

# ################################################################################################################################

def _serve(port:'int') -> 'None':
    """ Runs the HTTP server of zato_server_core in a process of its own, with a handler that answers every request.
    """
    exit_code = 1

    try:
        from zato_server_core.zato_server_core import HTTPServer

        def handle(request_ctx:'anydict') -> 'anytuple':
            out = ('200 OK', {'Content-Type': 'text/plain'}, b'OK')
            return out

        server = HTTPServer(ModuleCtx.Host, port, handle, 'zato-test', ModuleCtx.Max_Msg_Size)
        _ = server.serve_forever()
        exit_code = 0

    except BaseException:
        traceback.print_exc()

    finally:
        os._exit(exit_code)

# ################################################################################################################################

def _connect(port:'int') -> 'HTTPConnection':
    """ Returns a connection to the server, which may not be listening yet.
    """
    deadline = time.monotonic() + ModuleCtx.Connect_Timeout

    while True:
        connection = HTTPConnection(ModuleCtx.Host, port, timeout=ModuleCtx.Response_Timeout)

        try:
            connection.connect()
            return connection

        except ConnectionRefusedError:
            if time.monotonic() > deadline:
                raise
            time.sleep(ModuleCtx.Connect_Interval)

# ################################################################################################################################

def _get_local_address(connection:'HTTPConnection') -> 'anytuple':
    sock = connection.sock
    assert sock is not None

    out = sock.getsockname()
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_connection_closes_after_its_maximum_number_of_requests() -> 'None':
    port = _get_free_port()

    context = get_context('fork')
    process = context.Process(target=_serve, args=(port,))
    process.start()

    try:
        connection = _connect(port)
        local_address = _get_local_address(connection)

        # Every response but the last one keeps the connection open ..
        for _ in range(ModuleCtx.Max_Requests_Per_Connection - 1):
            connection.request('GET', '/')
            response = connection.getresponse()

            assert response.read() == b'OK'
            assert response.getheader('Connection') == 'keep-alive'

        # .. all of them on the same connection ..
        assert _get_local_address(connection) == local_address

        # .. and the last one closes it, after which the server sends nothing further on it.
        connection.request('GET', '/')
        response = connection.getresponse()

        assert response.read() == b'OK'
        assert response.getheader('Connection') == 'close'
        assert connection.sock is None

        connection.close()

    finally:
        process.terminate()
        process.join(ModuleCtx.Join_Timeout)

# ################################################################################################################################
# ################################################################################################################################
