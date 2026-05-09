# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

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
from collections.abc import Generator
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# Zato
from zato.common.util.config import get_config_object, update_config_file

# Local
from _client import ZatoClient
from _services import echo_service_source, error_service_source, forward_service_source, inspect_service_source

# ################################################################################################################################
# ################################################################################################################################

_ZATO_BASE = '/home/dsuch/projects/zatosource-zato/4.1'
_ZATO_BIN = os.path.join(_ZATO_BASE, 'code', 'bin', 'zato')
_ZATO_PYTHON = os.path.join(_ZATO_BASE, 'code', 'bin', 'python')

_MLLP_TEST_SERVER_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'zato-common', 'mllp', 'mllp_test_server.py'
)

_PASSWORD = 'test.invoke.' + os.urandom(8).hex()

_SERVER_READY_TIMEOUT = 60
_BACKEND_READY_TIMEOUT = 10
_HOT_DEPLOY_WAIT_SECONDS = 5
_LISTENER_BIND_WAIT_SECONDS = 2

_server_process = None
_temp_directory = None

# Type aliases for generator-based fixtures
strobj_dict     = dict[str, object]
strobj_dict_gen = Generator[strobj_dict, None, None]
backend_gen     = Generator['BackendHandle', None, None]
none_gen        = Generator[None, None, None]

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to port 0 to get an OS-assigned free port, then releases it.
    """
    temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temporary_socket.bind(('127.0.0.1', 0))

    _, port = temporary_socket.getsockname()

    temporary_socket.close()

    return port

# ################################################################################################################################
# ################################################################################################################################

def _kill_server() -> 'None':
    global _server_process

    if _server_process:
        if _server_process.poll() is None:
            _server_process.terminate()
            try:
                _server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _server_process.kill()
                _server_process.wait(timeout=5)

    _server_process = None

# ################################################################################################################################
# ################################################################################################################################

def _cleanup() -> 'None':
    _kill_server()

    global _temp_directory

    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'str', port:'int', timeout:'int'=_SERVER_READY_TIMEOUT) -> 'None':
    """ Polls GET /zato/ping until the server responds with 200.
    """

    url = f'http://{host}:{port}/zato/ping'
    start_time = time.monotonic()
    deadline = start_time + timeout
    attempt = 0

    while time.monotonic() < deadline:

        attempt += 1
        elapsed = time.monotonic() - start_time

        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=5) as response:
                if response.status == 200:
                    print(f'[TIMING] ping OK after {elapsed:.1f}s (attempt {attempt})')
                    return
        except Exception as exception:
            error_text = str(exception)[:80]
            print(f'[TIMING] ping attempt {attempt} at {elapsed:.1f}s: {error_text}')

        time.sleep(0.5)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'strobj_dict_gen':
    """ Starts a Zato server in a temporary directory and waits for it to become ready.
    """
    global _server_process, _temp_directory

    start_time = time.monotonic()

    port = _find_free_port()
    _temp_directory = tempfile.mkdtemp(prefix='zato_mllp_test_')

    # Create the quickstart environment ..
    quickstart_environment = os.environ.copy()
    quickstart_environment.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _ZATO_BIN, 'quickstart', 'create', _temp_directory,
        '--servers', '1',
        '--password', _PASSWORD,
        '--server-api-client-for-scheduler-password', _PASSWORD,
        '--no-scheduler',
    ]

    result = subprocess.run(quickstart_command, capture_output=True, text=True, timeout=120, env=quickstart_environment)

    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    after_quickstart = time.monotonic()
    print(f'\n[TIMING] quickstart create: {after_quickstart - start_time:.1f}s')

    # .. patch server.conf to use our port ..
    server_directory = os.path.join(_temp_directory, 'server1')
    repository_location = os.path.join(server_directory, 'config', 'repo')

    config = get_config_object(repository_location, 'server.conf')
    config['main']['port'] = str(port) # type: ignore[index]
    update_config_file(config, repository_location, 'server.conf') # type: ignore[arg-type]

    after_patch = time.monotonic()
    print(f'[TIMING] config patch: {after_patch - after_quickstart:.1f}s')

    # .. start the server in foreground mode ..
    broker_port = _find_free_port()

    server_environment = os.environ.copy()
    server_environment['Zato_Config_Bind_Port'] = str(port)
    server_environment['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_environment.pop('COVERAGE_PROCESS_START', None)

    _server_process = subprocess.Popen(
        [_ZATO_BIN, 'start', server_directory, '--fg'],
        env=server_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    after_popen = time.monotonic()
    print(f'[TIMING] Popen started: {after_popen - after_patch:.1f}s')

    # .. stream server stdout in a background thread ..
    def _stream_server_output() -> 'None':
        for line in iter(_server_process.stdout.readline, b''): # type: ignore[union-attr]
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - after_popen
            print(f'[SERVER {elapsed:6.1f}s] {text}')

    output_thread = threading.Thread(target=_stream_server_output, daemon=True)
    output_thread.start()

    # .. wait for the server to come up ..
    host = '127.0.0.1'

    try:
        _wait_for_server(host, port)
        after_ready = time.monotonic()
        print(f'[TIMING] server ready: {after_ready - after_popen:.1f}s')
        print(f'[TIMING] total setup: {after_ready - start_time:.1f}s')
    except Exception:
        print('\n--- Server did not become ready, stdout was streamed above ---\n')
        _kill_server()
        raise

    yield {
        'host': host,
        'port': port,
        'password': _PASSWORD,
        'server_directory': server_directory,
        'temp_directory': _temp_directory,
    }

    # .. teardown ..
    _kill_server()

    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_client(zato_server:'dict[str, object]') -> 'object':
    """ Creates a ZatoClient connected to the test server.
    """

    host = str(zato_server['host'])
    port = int(zato_server['port']) # type: ignore[arg-type]
    password = str(zato_server['password'])

    out = ZatoClient(host, port, password)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def channel_port() -> 'int':
    """ Returns a free port for the MLLP channel to listen on.
    """
    out = _find_free_port()
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def forward_channel_port() -> 'int':
    """ Returns a free port for the forward MLLP channel to listen on.
    """
    out = _find_free_port()
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def error_channel_port() -> 'int':
    """ Returns a free port for the error MLLP channel to listen on.
    """
    out = _find_free_port()
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def backend_port() -> 'int':
    """ Returns a free port for the standalone MLLP backend to listen on.
    """
    out = _find_free_port()
    return out

# ################################################################################################################################
# ################################################################################################################################

class BackendHandle:
    """ Holds the subprocess and captured stdout lines from the standalone MLLP backend.
    """
    def __init__(self) -> 'None':
        self.process:'subprocess.Popen[bytes] | None' = None
        self.received_lines:'list[str]' = []

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mllp_backend(backend_port:'int') -> 'backend_gen':
    """ Starts the standalone mllp_test_server.py in echo mode and captures its stdout.
    """

    handle = BackendHandle()

    server_script = os.path.normpath(_MLLP_TEST_SERVER_PATH)

    command = [
        _ZATO_PYTHON, server_script,
        '--host', '127.0.0.1',
        '--port', str(backend_port),
        '--callback-mode', 'echo',
        '--log-messages',
    ]

    handle.process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # .. capture stdout lines in a background thread ..
    def _capture_output() -> 'None':
        for line in iter(handle.process.stdout.readline, b''): # type: ignore[union-attr]
            text = line.decode('utf-8', errors='replace').rstrip()
            handle.received_lines.append(text)
            print(f'[BACKEND] {text}')

    capture_thread = threading.Thread(target=_capture_output, daemon=True)
    capture_thread.start()

    # .. wait for the READY signal ..
    deadline = time.monotonic() + _BACKEND_READY_TIMEOUT

    while time.monotonic() < deadline:

        for line in handle.received_lines:
            if line.startswith('READY:'):
                yield handle

                # .. teardown ..
                if handle.process:
                    if handle.process.poll() is None:
                        handle.process.terminate()
                        try:
                            handle.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            handle.process.kill()
                            handle.process.wait(timeout=5)
                return

        time.sleep(0.2)

    # .. backend did not become ready ..
    if handle.process:
        handle.process.kill()

    raise RuntimeError(f'MLLP backend did not produce READY signal within {_BACKEND_READY_TIMEOUT}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def hot_deploy_services(zato_server:'dict[str, object]', zato_client:'object') -> 'none_gen':
    """ Writes the test service files into the pickup directory and waits for Zato to register them.
    """

    server_directory = str(zato_server['server_directory'])
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    os.makedirs(pickup_directory, exist_ok=True)

    service_files = {
        '_test_hl7_mllp_echo.py':    echo_service_source,
        '_test_hl7_mllp_error.py':   error_service_source,
        '_test_hl7_mllp_forward.py': forward_service_source,
        '_test_hl7_mllp_inspect.py': inspect_service_source,
    }

    deployed_paths = []

    for filename, source in service_files.items():
        file_path = os.path.join(pickup_directory, filename)
        with open(file_path, 'w') as file_handle:
            file_handle.write(source)
        deployed_paths.append(file_path)
        print(f'[DEPLOY] Wrote {file_path}')

    # .. wait for Zato to pick up the services ..
    print(f'[DEPLOY] Waiting {_HOT_DEPLOY_WAIT_SECONDS}s for pickup ...')
    time.sleep(_HOT_DEPLOY_WAIT_SECONDS)

    yield None

    # .. teardown: remove the deployed files ..
    for file_path in deployed_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################
