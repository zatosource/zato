# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the test endpoint runs on gevent in this process while the server invokes it, so the patching runs
# before anything else is imported and every wait of this process yields to the endpoint.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import atexit
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.client import OK
from json import dumps
from urllib.error import URLError
from urllib.request import Request, urlopen

_this_directory = os.path.dirname(__file__)
_endpoint_directory = os.path.join(_this_directory, '..', 'rest_outgoing_invocation')

sys.path.insert(0, _this_directory)
sys.path.insert(0, _endpoint_directory)

# pytest
import pytest  # noqa: E402

# Zato
from zato.common.crypto.api import CryptoManager  # noqa: E402
from zato.common.test import kill_server_process  # noqa: E402
from zato.common.util.config import get_config_object, update_config_file  # noqa: E402

# Test support
from endpoint import EndpointResponse, TestEndpoint  # noqa: E402
from live_config import Basic_Password, build_config_yaml, Client_Secret, InvokeClient, OAuth_Token, OAuth_Token_Path, \
    run_enmasse, Zato_Bin  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_

    endpointgen = Iterator[TestEndpoint]

# ################################################################################################################################
# ################################################################################################################################

_invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

_services_path = os.path.join(_this_directory, '_services.py')

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_ping_poll_interval   = 0.5

# How long the token endpoint says its tokens are valid for, in seconds
_token_expires_in = 3600

# ################################################################################################################################
# ################################################################################################################################

class _SessionState:
    """ The server process and the directory of its environment.
    """

    def __init__(self) -> 'None':
        self.server_process:'any_' = None
        self.temp_directory = ''

    def cleanup(self) -> 'None':
        kill_server_process(self.server_process, _process_kill_timeout, server_directory=self.temp_directory)
        self.server_process = None

        if self.temp_directory:
            shutil.rmtree(self.temp_directory, ignore_errors=True)

        self.temp_directory = ''

_state = _SessionState()
_ = atexit.register(_state.cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Returns a free TCP port on localhost.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))

        socket_address = tcp_socket.getsockname()

        out = socket_address[1]
        return out

# ################################################################################################################################

def _wait_for_server(host:'str', port:'int') -> 'None':
    """ Polls the server's /zato/ping endpoint until it returns 200 or the timeout expires.
    """
    ping_url = f'http://{host}:{port}/zato/ping'
    deadline = time.monotonic() + _server_wait_timeout

    while time.monotonic() < deadline:

        try:
            request = Request(ping_url, method='GET')

            with urlopen(request, timeout=_process_kill_timeout) as response:
                if response.status == OK:
                    return

        except (ConnectionRefusedError, OSError, URLError):
            pass

        time.sleep(_ping_poll_interval)

    raise Exception(f'Server at {host}:{port} did not respond within {_server_wait_timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def endpoint() -> 'endpointgen':
    """ The local endpoint the server's outgoing connections invoke, with the token endpoint of the OAuth definition.
    """
    directory = tempfile.mkdtemp(prefix='zato-rest-outgoing-live-')
    certificates_directory = os.path.join(directory, 'certificates')

    out = TestEndpoint(certificates_directory)
    out.start()

    token_body = dumps({'access_token': OAuth_Token, 'token_type': 'Bearer', 'expires_in': _token_expires_in})
    out.set_response(OAuth_Token_Path, EndpointResponse(body=token_body, headers=[('Content-Type', 'application/json')]))

    yield out

    out.stop()
    os.rmdir(directory)

# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server(endpoint:'TestEndpoint') -> 'any_':
    """ A quickstart environment with the invocation service deployed from pickup and the outgoing connections
    imported through enmasse.
    """
    port = _find_free_port()
    _state.temp_directory = tempfile.mkdtemp(prefix='zato_rest_outgoing_live_test_')

    quickstart_command = [
        Zato_Bin, 'quickstart', 'create', _state.temp_directory,
        '--password', _invoke_password,
        '--server-api-client-for-scheduler-password', _invoke_password,
        '--no-scheduler',
    ]

    result = subprocess.run(quickstart_command, capture_output=True, text=True, check=False, timeout=_quickstart_timeout)

    if result.returncode != 0:
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    # The server listens on a port of its own ..
    server_directory = os.path.join(_state.temp_directory, 'server1')
    repo_location = os.path.join(server_directory, 'config', 'repo')

    config = get_config_object(repo_location, 'server.conf')
    config['main']['port'] = str(port) # pyright: ignore[reportIndexIssue, reportCallIssue, reportArgumentType]
    config['main']['bind'] = f'127.0.0.1:{port}' # pyright: ignore[reportIndexIssue, reportCallIssue, reportArgumentType]
    update_config_file(config, repo_location, 'server.conf') # pyright: ignore[reportArgumentType]

    # .. the invocation service deploys from pickup during boot ..
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    os.makedirs(pickup_directory, exist_ok=True)
    _ = shutil.copy2(_services_path, os.path.join(pickup_directory, 'rest_outgoing_live_services.py'))

    # .. the server starts in the foreground ..
    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(port)
    server_env['Zato_Broker_HTTP_Port'] = str(_find_free_port())

    _state.server_process = subprocess.Popen(
        [Zato_Bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # .. its output goes to a file, so a failed start can be diagnosed ..
    server_log_path = os.path.join(tempfile.gettempdir(), 'zato_rest_outgoing_live_server.log')
    server_log_file = open(server_log_path, 'w')

    def _stream_server_output() -> 'None':
        stdout = _state.server_process.stdout
        for line in iter(stdout.readline, b''):
            text = line.decode('utf8', errors='replace').rstrip()
            _ = server_log_file.write(text + '\n')
            server_log_file.flush()

    stdout_thread = threading.Thread(target=_stream_server_output, daemon=True)
    stdout_thread.start()

    host = '127.0.0.1'

    try:
        _wait_for_server(host, port)

    except Exception:
        print(f'\nThe server did not become ready, its output is in {server_log_path}\n')
        _state.cleanup()
        raise

    # .. and the connections are imported once it runs.
    config_yaml = build_config_yaml(endpoint.http_base, Basic_Password, Client_Secret)
    run_enmasse(server_directory, config_yaml)

    yield {
        'base_url': f'http://{host}:{port}',
        'server_directory': server_directory,
    }

    _state.cleanup()

# ################################################################################################################################

@pytest.fixture(scope='session')
def invoke_client(zato_server:'any_') -> 'InvokeClient':
    """ The client the tests invoke the server's services with.
    """
    out = InvokeClient(zato_server['base_url'], _invoke_password)
    return out

# ################################################################################################################################
# ################################################################################################################################
