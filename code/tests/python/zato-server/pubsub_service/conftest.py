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
from http.client import OK
from urllib.error import URLError
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_zato_base = '/home/dsuch/projects/zatosource-zato/4.1'
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_password = 'test.invoke.' + os.urandom(8).hex()

_services_source = os.path.join(os.path.dirname(__file__), '_services.py')

_process_kill_timeout      = 5
_server_wait_timeout       = 120
_quickstart_timeout        = 180
_hot_deploy_settle_seconds = 10
_ping_poll_interval        = 0.5

_server_process  = None
_temp_directory   = None

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))

        out = tcp_socket.getsockname()[1]
        return out

# ################################################################################################################################
# ################################################################################################################################

def _kill_server() -> 'None':
    global _server_process

    if _server_process:
        if _server_process.poll() is None:

            # Try graceful termination first ..
            _server_process.terminate()

            try:
                _ = _server_process.wait(timeout=_process_kill_timeout)

            # .. if it does not stop in time, force kill it.
            except subprocess.TimeoutExpired:
                _server_process.kill()
                _ = _server_process.wait(timeout=_process_kill_timeout)

    _server_process = None

# ################################################################################################################################
# ################################################################################################################################

def _cleanup() -> 'None':

    # Stop the server process first ..
    _kill_server()

    global _temp_directory

    # .. then clean up the temporary directory.
    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

_ = atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'str', port:'int', timeout:'int'=_server_wait_timeout) -> 'None':

    ping_url = f'http://{host}:{port}/zato/ping'
    start_time = time.monotonic()
    deadline = start_time + timeout
    attempt_number = 0

    while time.monotonic() < deadline:

        attempt_number += 1
        elapsed = time.monotonic() - start_time

        try:
            request = Request(ping_url, method='GET')

            with urlopen(request, timeout=_process_kill_timeout) as response:
                if response.status == OK:
                    print(f'[TIMING] ping OK after {elapsed:.1f}s (attempt {attempt_number})')
                    return

        except (ConnectionRefusedError, OSError, URLError):
            elapsed_now = time.monotonic() - start_time
            print(f'[TIMING] ping attempt {attempt_number} at {elapsed_now:.1f}s: not ready')

        time.sleep(_ping_poll_interval)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'any_':

    global _server_process, _temp_directory

    from config import TestConfig

    start_time = time.monotonic()

    port = _find_free_port()
    _temp_directory = tempfile.mkdtemp(prefix='zato_pubsub_service_test_')

    # Create a quickstart environment ..
    quickstart_env = os.environ.copy()
    _ = quickstart_env.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', _temp_directory,
        '--force',
        '--password', _password,
        '--servers', '1',
        '--server-api-client-for-scheduler-password', _password,
        '--no-scheduler',
    ]

    result = subprocess.run(
        quickstart_command, capture_output=True, text=True, check=False,
        timeout=_quickstart_timeout, env=quickstart_env)

    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    quickstart_time = time.monotonic()
    print(f'\n[TIMING] quickstart create: {quickstart_time - start_time:.1f}s')

    server_directory = os.path.join(_temp_directory, 'server1')

    # .. copy test services into the pickup directory before starting the server
    # .. so they get deployed during startup ..
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    destination = os.path.join(pickup_directory, 'pubsub_test_services.py')
    shutil.copy2(_services_source, destination)

    print(f'[TIMING] copied test services to {destination}')

    # .. start the server in foreground mode ..
    broker_port = _find_free_port()

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    _ = server_env.pop('COVERAGE_PROCESS_START', None)

    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    popen_time = time.monotonic()
    print(f'[TIMING] Popen started: {popen_time - quickstart_time:.1f}s')

    # .. stream server stdout in a background thread ..
    def _stream_server_output() -> 'None':
        for line in iter(_server_process.stdout.readline, b''): # type: ignore
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - popen_time
            print(f'[SERVER {elapsed:6.1f}s] {text}')

    stdout_thread = threading.Thread(target=_stream_server_output, daemon=True)
    stdout_thread.start()

    # .. wait for the server to come up ..
    host = '127.0.0.1'

    try:
        _wait_for_server(host, port)
        ready_time = time.monotonic()
        print(f'[TIMING] server ready: {ready_time - popen_time:.1f}s')

    except (ConnectionRefusedError, OSError, RuntimeError):
        print('\n--- Server did not become ready, stdout was streamed above ---\n')
        _kill_server()
        raise

    setup_time = time.monotonic()
    print(f'[TIMING] total setup: {setup_time - start_time:.1f}s')

    # .. update the config so tests use the dynamically allocated port ..
    TestConfig.base_url = f'http://{host}:{port}'
    TestConfig.password = _password
    TestConfig.server_directory = server_directory

    yield

    _kill_server()

    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

# ################################################################################################################################
# ################################################################################################################################
