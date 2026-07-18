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
from http.client import OK
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient as ZatoClient
from zato.common.typing_ import cast_
from zato.common.util.config import get_config_object, update_config_file

# Zato - test services deployed to the server under test
from _services import echo_service_source, error_service_source, forward_service_source, inspect_service_source

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strlist
    any_ = any_
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

_zato_base_dir = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin      = os.path.join(_zato_base_dir, 'code', 'bin', 'zato')
_zato_python   = os.path.join(_zato_base_dir, 'code', 'bin', 'python')

_current_dir = os.path.dirname(__file__)
_mllp_test_server_path = os.path.join(_current_dir, '..', '..', 'zato-common', 'mllp', 'mllp_test_server.py')

# The file-transfer listener that watches the pickup directory for runtime hot-deploy
_listener_path = os.path.join(
    _zato_base_dir, 'code', 'zato-common', 'src', 'zato', 'common', 'file_transfer', 'listener.py')

_password_suffix = CryptoManager.generate_hex_string()
_password = 'test.invoke.' + _password_suffix

_server_ready_timeout    = 60
_backend_ready_timeout   = 10
_hot_deploy_wait_seconds = 5
_listener_settle_seconds = 2
_port_wait_timeout       = 10

_server_process   = None
_listener_process = None
_temp_directory   = None

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

def is_port_open(port:'int') -> 'bool':
    """ Returns True if the port accepts TCP connections on localhost.
    """
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(2.0)

    try:
        test_socket.connect(('127.0.0.1', port))
        test_socket.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False

# ################################################################################################################################
# ################################################################################################################################

def wait_for_port_open(port:'int', timeout:'int'=_port_wait_timeout) -> 'None':
    """ Polls until the port accepts TCP connections.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        if is_port_open(port):
            return

        time.sleep(0.2)

    raise Exception(f'Port {port} was not open within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def wait_for_port_closed(port:'int', timeout:'int'=_port_wait_timeout) -> 'None':
    """ Polls until the port no longer accepts TCP connections.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        if not is_port_open(port):
            return

        time.sleep(0.2)

    raise Exception(f'Port {port} was not closed within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _kill_process(process:'subprocess.Popen[bytes] | None') -> 'None':

    if process:
        if process.poll() is None:
            process.terminate()
            try:
                _ = process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                _ = process.wait(timeout=5)

# ################################################################################################################################
# ################################################################################################################################

def _kill_server() -> 'None':
    global _server_process, _listener_process

    # Stop the file listener first so it does not race the server shutdown ..
    _kill_process(_listener_process)
    _listener_process = None

    # .. and now the server itself.
    _kill_process(_server_process)
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

_ = atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'str', port:'int', timeout:'int'=_server_ready_timeout) -> 'None':
    """ Polls GET /zato/ping until the server responds with 200 OK.
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
                if response.status == OK:
                    print(f'[TIMING] ping OK after {elapsed:.1f}s (attempt {attempt})')
                    return
        except Exception as exception:
            print(f'[TIMING] ping attempt {attempt} at {elapsed:.1f}s: {exception}')

        time.sleep(0.5)

    raise Exception(f'Server at {host}:{port} did not respond within {timeout}s')

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
    _ = quickstart_environment.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', _temp_directory,
        '--servers', '1',
        '--password', _password,
        '--server-api-client-for-scheduler-password', _password,
        '--no-scheduler',
    ]

    result = subprocess.run(quickstart_command, capture_output=True, text=True, timeout=120, env=quickstart_environment)

    if result.returncode != 0:
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    after_quickstart = time.monotonic()
    print(f'\n[TIMING] quickstart create: {after_quickstart - start_time:.1f}s')

    # .. patch server.conf to use our port ..
    server_directory = os.path.join(_temp_directory, 'server1')
    repository_location = os.path.join(server_directory, 'config', 'repo')

    config = get_config_object(repository_location, 'server.conf')
    config = cast_('any_', config)

    main_config = config['main']
    main_config['port'] = str(port)

    # The pre-start config check reads the bind address, not the port,
    # so the default 0.0.0.0:17010 must not linger in there - another
    # environment on this machine may hold that port.
    main_config['bind'] = f'0.0.0.0:{port}'

    update_config_file(config, repository_location, 'server.conf')

    after_patch = time.monotonic()
    print(f'[TIMING] config patch: {after_patch - after_quickstart:.1f}s')

    # .. start the server in foreground mode ..
    broker_port = _find_free_port()

    # Pick the port for the shared internal MLLP server upfront so tests know it in advance
    mllp_port = _find_free_port()

    # The file test services use to exchange received messages with the test process
    messages_file = os.path.join(_temp_directory, 'mllp_messages.txt')

    server_environment = os.environ.copy()
    server_environment['Zato_Config_Bind_Port'] = str(port)
    server_environment['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_environment['Zato_HL7_MLLP_Port'] = str(mllp_port)
    server_environment['Zato_Test_MLLP_Messages_File'] = messages_file
    _ = server_environment.pop('COVERAGE_PROCESS_START', None)

    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    after_popen = time.monotonic()
    print(f'[TIMING] Popen started: {after_popen - after_patch:.1f}s')

    # .. stream server stdout in a background thread ..
    server_process = cast_('any_', _server_process)

    def _stream_server_output() -> 'None':
        for line in iter(server_process.stdout.readline, b''):
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

    # .. start the file-transfer listener that watches the pickup directory, so that
    # files dropped at runtime trigger hot-deploy. The server's own boot scan only
    # covers files present at startup ..
    global _listener_process

    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    web_admin_repo = os.path.join(_temp_directory, 'web-admin', 'config', 'repo')

    listener_env = os.environ.copy()
    listener_env['Zato_Config_Bind_Port'] = str(port)
    listener_env['Zato_Web_Admin_Repo_Dir'] = web_admin_repo
    _ = listener_env.pop('COVERAGE_PROCESS_START', None)

    _listener_process = subprocess.Popen(
        [_zato_python, _listener_path, pickup_directory],
        env=listener_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # .. give the listener a moment to initialize its directory watch ..
    time.sleep(_listener_settle_seconds)

    yield {
        'host': host,
        'port': port,
        'mllp_port': mllp_port,
        'password': _password,
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
def zato_client(zato_server:'strobj_dict') -> 'ZatoClient':
    """ Creates a ZatoClient connected to the test server.
    """

    host     = cast_('str', zato_server['host'])
    port     = cast_('int', zato_server['port'])
    password = cast_('str', zato_server['password'])

    base_url = f'http://{host}:{port}'

    out = ZatoClient(base_url, password)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mllp_port(zato_server:'strobj_dict') -> 'int':
    """ Returns the port the shared internal MLLP server binds to, chosen upfront
    and exported to the server via the Zato_HL7_MLLP_Port environment variable.
    """
    out = cast_('int', zato_server['mllp_port'])
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

    server_script = os.path.normpath(_mllp_test_server_path)

    command = [
        _zato_python, server_script,
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
    process = cast_('any_', handle.process)

    def _capture_output() -> 'None':
        for line in iter(process.stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            handle.received_lines.append(text)
            print(f'[BACKEND] {text}')

    capture_thread = threading.Thread(target=_capture_output, daemon=True)
    capture_thread.start()

    # .. wait for the READY signal ..
    deadline = time.monotonic() + _backend_ready_timeout

    while time.monotonic() < deadline:

        for line in handle.received_lines:
            if line.startswith('READY:'):
                yield handle

                # .. teardown ..
                if process.poll() is None:
                    process.terminate()
                    try:
                        _ = process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        _ = process.wait(timeout=5)
                return

        time.sleep(0.2)

    # .. the backend did not become ready in time.
    process.kill()
    raise Exception(f'MLLP backend did not produce READY signal within {_backend_ready_timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def hot_deploy_services(zato_server:'strobj_dict', zato_client:'ZatoClient') -> 'none_gen':
    """ Writes the test service files into the pickup directory and waits for Zato to register them.
    """

    server_directory = cast_('str', zato_server['server_directory'])
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    os.makedirs(pickup_directory, exist_ok=True)

    service_files = {
        '_test_hl7_mllp_echo.py':    echo_service_source,
        '_test_hl7_mllp_error.py':   error_service_source,
        '_test_hl7_mllp_forward.py': forward_service_source,
        '_test_hl7_mllp_inspect.py': inspect_service_source,
    }

    deployed_paths:'strlist' = []

    for filename, source in service_files.items():
        file_path = os.path.join(pickup_directory, filename)
        with open(file_path, 'w') as file_handle:
            _ = file_handle.write(source)
        deployed_paths.append(file_path)
        print(f'[DEPLOY] Wrote {file_path}')

    # .. wait for Zato to pick up the services ..
    print(f'[DEPLOY] Waiting {_hot_deploy_wait_seconds}s for pickup ...')
    time.sleep(_hot_deploy_wait_seconds)

    yield None

    # .. teardown: remove the deployed files ..
    for file_path in deployed_paths:
        if os.path.exists(file_path):
            os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################
