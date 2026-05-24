# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.client import OK, FOUND
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

# pytest
import pytest
from playwright.sync_api import sync_playwright

# Zato
from zato.common.json_internal import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

from client import ZatoClient
from login import login as login_to_dashboard

_Zato_Base = os.environ['ZATO_TEST_BASE_DIR']
_Zato_Bin  = os.path.join(_Zato_Base, 'code', 'bin', 'zato')

_Password = 'test.dashboard.' + os.urandom(8).hex()

_Process_Kill_Timeout  = 5
_Server_Wait_Timeout   = 60
_Quickstart_Timeout    = 120
_Ping_Poll_Interval    = 0.5

_server_process    = None # type: ignore
_dashboard_process = None # type: ignore
_temporary_dir     = None # type: ignore

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to an ephemeral port and returns its number.
    """

    # Open a TCP socket ..
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))

        # .. extract the assigned port ..
        address = tcp_socket.getsockname()
        out = address[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

def _kill_process(process:'subprocess.Popen | None') -> 'None':
    """ Terminates a subprocess, escalating to kill if it does not exit in time.
    """
    if process:
        if process.poll() is None:

            # Try graceful termination first ..
            process.terminate()

            try:
                process.wait(timeout=_Process_Kill_Timeout)

            # .. escalate to kill if it did not exit.
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=_Process_Kill_Timeout)

# ################################################################################################################################
# ################################################################################################################################

def _cleanup() -> 'None':
    """ Cleans up all test processes and the temporary directory.
    """
    global _server_process, _dashboard_process, _temporary_dir

    # Kill the server ..
    _kill_process(_server_process)
    _server_process = None

    # .. kill the dashboard ..
    _kill_process(_dashboard_process)
    _dashboard_process = None

    # .. remove the temporary directory.
    if _temporary_dir:
        if os.path.isdir(_temporary_dir):
            shutil.rmtree(_temporary_dir, ignore_errors=True)
    _temporary_dir = None

atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_http(host:'str', port:'int', path:'str', timeout:'int' = _Server_Wait_Timeout) -> 'None':
    """ Polls an HTTP endpoint until it returns 200 or 302, or raises after timeout.
    """

    url = f'http://{host}:{port}{path}'
    time_start = time.monotonic()
    deadline = time_start + timeout
    attempt = 0

    while time.monotonic() < deadline:
        attempt += 1
        elapsed = time.monotonic() - time_start

        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=_Process_Kill_Timeout) as response:

                # Accept either OK or redirect as a sign of readiness ..
                if response.status in (OK, FOUND):
                    print(f'[TIMING] {url} OK after {elapsed:.1f}s (attempt {attempt})')
                    return

        except Exception as exception:
            error_text = str(exception)[:80]
            print(f'[TIMING] {url} attempt {attempt} at {elapsed:.1f}s: {error_text}')

        time.sleep(_Ping_Poll_Interval)

    raise RuntimeError(f'{url} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _stream_output(process:'subprocess.Popen', label:'str', time_reference:'float') -> 'None':
    """ Streams subprocess stdout to the test console with timing information.
    """

    for line in iter(process.stdout.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()
        elapsed = time.monotonic() - time_reference
        print(f'[{label} {elapsed:6.1f}s] {text}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_dashboard() -> 'any_':
    """ Session-scoped fixture that creates a quickstart environment with server and dashboard.
    """
    global _server_process, _dashboard_process, _temporary_dir

    time_start = time.monotonic()

    # Allocate dynamic ports ..
    server_port    = _find_free_port()
    dashboard_port = _find_free_port()
    broker_port    = _find_free_port()

    _temporary_dir = tempfile.mkdtemp(prefix='zato_pw_test_')

    # .. 1) create a quickstart environment with both server and dashboard ..

    quickstart_env = os.environ.copy()
    quickstart_env.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _Zato_Bin, 'quickstart', 'create', _temporary_dir,
        '--servers', '1',
        '--password', _Password,
        '--server-api-client-for-scheduler-password', _Password,
        '--no-scheduler',
    ]

    result = subprocess.run(quickstart_command, capture_output=True, text=True,
        timeout=_Quickstart_Timeout, env=quickstart_env)

    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    time_after_quickstart = time.monotonic()
    print(f'\n[TIMING] quickstart create: {time_after_quickstart - time_start:.1f}s')

    # .. 2) patch server.conf to bind on our dynamic port ..

    server_dir = os.path.join(_temporary_dir, 'server1')
    server_config_path = os.path.join(server_dir, 'config', 'repo', 'server.conf')

    with open(server_config_path, 'r') as server_config_file:
        server_config_content = server_config_file.read()

    server_config_content = re.sub(
        r'^(bind\s*=\s*)\S+',
        f'\\g<1>0.0.0.0:{server_port}',
        server_config_content,
        flags=re.MULTILINE,
    )

    with open(server_config_path, 'w') as server_config_file:
        _ = server_config_file.write(server_config_content)

    # .. 3) patch web-admin.conf to use our dashboard port ..

    dashboard_dir = os.path.join(_temporary_dir, 'web-admin')
    dashboard_config_path = os.path.join(dashboard_dir, 'config', 'repo', 'web-admin.conf')

    with open(dashboard_config_path, 'r') as config_file:
        dashboard_config = loads(config_file.read())

    dashboard_config['host'] = '127.0.0.1'
    dashboard_config['port'] = dashboard_port

    with open(dashboard_config_path, 'w') as config_file:
        _ = config_file.write(dumps(dashboard_config))

    time_after_config = time.monotonic()
    print(f'[TIMING] config patch: {time_after_config - time_after_quickstart:.1f}s')

    # .. 4) start the server ..

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(server_port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env.pop('COVERAGE_PROCESS_START', None)

    _server_process = subprocess.Popen(
        [_Zato_Bin, 'start', server_dir, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    time_after_server_start = time.monotonic()

    server_thread = threading.Thread(
        target=_stream_output, args=(_server_process, 'SERVER', time_after_server_start), daemon=True)
    server_thread.start()

    # .. 5) start the dashboard ..

    dashboard_env = os.environ.copy()
    dashboard_env.pop('COVERAGE_PROCESS_START', None)
    dashboard_env['Zato_Server_Address'] = f'http://127.0.0.1:{server_port}'

    _dashboard_process = subprocess.Popen(
        [_Zato_Bin, 'start', dashboard_dir, '--fg'],
        env=dashboard_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    dashboard_thread = threading.Thread(
        target=_stream_output, args=(_dashboard_process, 'DASHBOARD', time_after_server_start), daemon=True)
    dashboard_thread.start()

    # .. 6) wait for both to be ready ..

    host = '127.0.0.1'

    try:
        _wait_for_http(host, server_port, '/zato/ping')
        time_server_ready = time.monotonic()
        print(f'[TIMING] server ready: {time_server_ready - time_after_server_start:.1f}s')

        _wait_for_http(host, dashboard_port, '/accounts/login/')
        time_dashboard_ready = time.monotonic()
        print(f'[TIMING] dashboard ready: {time_dashboard_ready - time_after_server_start:.1f}s')
        print(f'[TIMING] total setup: {time_dashboard_ready - time_start:.1f}s')

    except Exception:
        print('\n--- Components did not become ready, stdout was streamed above ---\n')
        _kill_process(_server_process)
        _kill_process(_dashboard_process)
        raise

    yield {
        'host': host,
        'server_port': server_port,
        'dashboard_port': dashboard_port,
        'dashboard_url': f'http://{host}:{dashboard_port}',
        'password': _Password,
        'server_dir': server_dir,
        'dashboard_dir': dashboard_dir,
        'temporary_dir': _temporary_dir,
    }

    # .. teardown: stop server ..
    _kill_process(_server_process)
    _server_process = None

    # .. stop dashboard ..
    _kill_process(_dashboard_process)
    _dashboard_process = None

    # .. remove the temporary directory.
    if _temporary_dir:
        if os.path.isdir(_temporary_dir):
            shutil.rmtree(_temporary_dir, ignore_errors=True)
    _temporary_dir = None

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def playwright_browser() -> 'any_':
    """ Launches a Playwright Chromium browser for the entire test session.
    """

    # Start playwright, headed mode if ZATO_PLAYWRIGHT_HEADED is set ..
    use_headless = 'ZATO_PLAYWRIGHT_HEADED' not in os.environ

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=use_headless)

    yield browser

    # .. shut down browser and playwright.
    browser.close()
    playwright.stop()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def logged_in_page(zato_dashboard:'anydict', playwright_browser:'any_') -> 'any_':
    """ Provides a fresh, logged-in Playwright page for each test.
    """

    # Create a new browser context ..
    context = playwright_browser.new_context()

    # .. open a page ..
    page = context.new_page()

    # .. log into the dashboard ..
    dashboard_url = zato_dashboard['dashboard_url']
    password = zato_dashboard['password']
    login_to_dashboard(page, dashboard_url, password)

    yield page

    # .. clean up.
    page.close()
    context.close()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def api_client(zato_dashboard:'anydict') -> 'ZatoClient':
    """ Provides a ZatoClient for server-side API calls.
    """

    host = zato_dashboard['host']
    server_port = zato_dashboard['server_port']
    password = zato_dashboard['password']

    out = ZatoClient(host, server_port, password)
    return out

# ################################################################################################################################
# ################################################################################################################################
