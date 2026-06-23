# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import glob
import logging
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

logger = logging.getLogger('zato.test.playwright')

_Zato_Base = os.environ['ZATO_TEST_BASE_DIR']
_Zato_Bin  = os.path.join(_Zato_Base, 'code', 'bin', 'zato')

_Password = 'test.dashboard.' + os.urandom(8).hex()

_Process_Kill_Timeout  = 5
_Server_Wait_Timeout   = 60
_Quickstart_Timeout    = 120
_Ping_Poll_Interval    = 0.5

_cleanup_refs = {
    'server_process': None,
    'dashboard_process': None,
    'listener_process': None,
    'temporary_dir': None,
}

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
    for key in ('listener_process', 'server_process', 'dashboard_process'):
        _kill_process(_cleanup_refs[key])
        _cleanup_refs[key] = None

    tmp = _cleanup_refs['temporary_dir']
    if tmp and os.path.isdir(tmp) and not _cleanup_refs.get('has_failures'):
        shutil.rmtree(tmp, ignore_errors=True)
    _cleanup_refs['temporary_dir'] = None

atexit.register(_cleanup)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item:'any_', call:'any_') -> 'any_':
    """ Track test failures so we can skip temp dir cleanup for debugging.
    """
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        _cleanup_refs['has_failures'] = True

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
                    logger.info(f'[TIMING] {url} OK after {elapsed:.1f}s (attempt {attempt})')
                    return

        except Exception as exception:
            error_text = str(exception)[:80]
            logger.info(f'[TIMING] {url} attempt {attempt} at {elapsed:.1f}s: {error_text}')

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
        logger.info(f'[{label} {elapsed:6.1f}s] {text}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_dashboard() -> 'any_':
    """ Session-scoped fixture that creates a quickstart environment with server and dashboard.
    """
    time_start = time.monotonic()

    # Allocate dynamic ports ..
    server_port    = _find_free_port()
    dashboard_port = _find_free_port()
    broker_port    = _find_free_port()

    temporary_dir = tempfile.mkdtemp(prefix='zato_pw_test_')
    _cleanup_refs['temporary_dir'] = temporary_dir

    # .. 1) create a quickstart environment with both server and dashboard ..

    quickstart_env = os.environ.copy()
    quickstart_env.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _Zato_Bin, 'quickstart', 'create', temporary_dir,
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
    logger.info(f'[TIMING] quickstart create: {time_after_quickstart - time_start:.1f}s')

    # .. 2) patch server.conf to bind on our dynamic port ..

    server_dir = os.path.join(temporary_dir, 'server1')
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

    dashboard_dir = os.path.join(temporary_dir, 'web-admin')
    dashboard_config_path = os.path.join(dashboard_dir, 'config', 'repo', 'web-admin.conf')

    with open(dashboard_config_path, 'r') as config_file:
        dashboard_config = loads(config_file.read())

    dashboard_config['host'] = '127.0.0.1'
    dashboard_config['port'] = dashboard_port

    with open(dashboard_config_path, 'w') as config_file:
        _ = config_file.write(dumps(dashboard_config))

    time_after_config = time.monotonic()
    logger.info(f'[TIMING] config patch: {time_after_config - time_after_quickstart:.1f}s')

    # .. 4) start the server ..

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(server_port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env.pop('COVERAGE_PROCESS_START', None)

    server_process = subprocess.Popen(
        [_Zato_Bin, 'start', server_dir, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    _cleanup_refs['server_process'] = server_process

    time_after_server_start = time.monotonic()

    server_thread = threading.Thread(
        target=_stream_output, args=(server_process, 'SERVER', time_after_server_start), daemon=True)
    server_thread.start()

    # .. 5) start the dashboard ..

    dashboard_env = os.environ.copy()
    dashboard_env.pop('COVERAGE_PROCESS_START', None)
    dashboard_env['Zato_Server_Address'] = f'http://127.0.0.1:{server_port}'

    dashboard_process = subprocess.Popen(
        [_Zato_Bin, 'start', dashboard_dir, '--fg'],
        env=dashboard_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    _cleanup_refs['dashboard_process'] = dashboard_process

    dashboard_thread = threading.Thread(
        target=_stream_output, args=(dashboard_process, 'DASHBOARD', time_after_server_start), daemon=True)
    dashboard_thread.start()

    # .. 6) wait for both to be ready ..

    host = '127.0.0.1'

    try:
        _wait_for_http(host, server_port, '/zato/ping')
        time_server_ready = time.monotonic()
        logger.info(f'[TIMING] server ready: {time_server_ready - time_after_server_start:.1f}s')

        _wait_for_http(host, dashboard_port, '/accounts/login/')
        time_dashboard_ready = time.monotonic()
        logger.info(f'[TIMING] dashboard ready: {time_dashboard_ready - time_after_server_start:.1f}s')
        logger.info(f'[TIMING] total setup: {time_dashboard_ready - time_start:.1f}s')

    except Exception:
        logger.error('Components did not become ready, stdout was streamed above')
        _kill_process(server_process)
        _kill_process(dashboard_process)
        raise

    # .. 7) start the file pickup listener so hot-deploy works for enmasse imports ..

    listener_env = os.environ.copy()
    listener_env['Zato_Config_Bind_Port'] = str(server_port)
    listener_env['Zato_Web_Admin_Repo_Dir'] = os.path.join(dashboard_dir, 'config', 'repo')
    listener_env['Zato_Server_Dir'] = server_dir
    listener_env.pop('COVERAGE_PROCESS_START', None)

    listener_process = subprocess.Popen(
        ['make', 'listener'],
        cwd=_Zato_Base,
        env=listener_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    _cleanup_refs['listener_process'] = listener_process

    listener_thread = threading.Thread(
        target=_stream_output, args=(listener_process, 'LISTENER', time_after_server_start), daemon=True)
    listener_thread.start()

    logger.info('[TIMING] file pickup listener started, pid=%s', listener_process.pid)

    yield {
        'host': host,
        'server_port': server_port,
        'dashboard_port': dashboard_port,
        'dashboard_url': f'http://{host}:{dashboard_port}',
        'password': _Password,
        'server_dir': server_dir,
        'dashboard_dir': dashboard_dir,
        'temporary_dir': temporary_dir,
        'server_process': server_process,
        'dashboard_process': dashboard_process,
        'listener_process': listener_process,
    }

    # .. teardown: stop listener ..
    _kill_process(listener_process)
    _cleanup_refs['listener_process'] = None

    # .. stop server ..
    _kill_process(server_process)
    _cleanup_refs['server_process'] = None

    # .. stop dashboard ..
    _kill_process(dashboard_process)
    _cleanup_refs['dashboard_process'] = None

    # .. remove the temporary directory only if all tests passed.
    if _cleanup_refs.get('has_failures'):
        logger.info('[TEARDOWN] Keeping temporary directory for debugging: %s', temporary_dir)
    elif os.path.isdir(temporary_dir):
        shutil.rmtree(temporary_dir, ignore_errors=True)
    _cleanup_refs['temporary_dir'] = None

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def playwright_browser() -> 'any_':
    """ Launches a Playwright Chromium browser for the entire test session.
    """

    # Show the browser window when a display server is available ..
    has_display = bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))
    use_headless = not has_display

    # .. start playwright ..
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=use_headless)

    yield browser

    # .. shut down browser and playwright.
    browser.close()
    playwright.stop()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def logged_in_page(zato_dashboard:'anydict', playwright_browser:'any_', request:'any_') -> 'any_':
    """ Provides a fresh, logged-in Playwright page for each test.
    """

    test_name = request.node.name

    # Capture process and browser state before doing anything ..
    dashboard_process = zato_dashboard['dashboard_process']
    server_process = zato_dashboard['server_process']

    dashboard_poll = dashboard_process.poll() if dashboard_process else 'no-process'
    server_poll = server_process.poll() if server_process else 'no-process'
    browser_connected = playwright_browser.is_connected()
    browser_contexts = len(playwright_browser.contexts)

    logger.info(
        f'[FIXTURE-SETUP] {test_name}: '
        f'dashboard_pid={getattr(dashboard_process, "pid", None)} poll={dashboard_poll}, '
        f'server_pid={getattr(server_process, "pid", None)} poll={server_poll}, '
        f'browser_connected={browser_connected} contexts={browser_contexts}'
    )

    # Probe dashboard HTTP before creating the page ..
    dashboard_url = zato_dashboard['dashboard_url']
    try:
        probe_request = Request(f'{dashboard_url}/accounts/login/', method='GET')
        with urlopen(probe_request, timeout=5) as probe_response:
            logger.info(f'[FIXTURE-SETUP] {test_name}: HTTP probe status={probe_response.status}')
    except Exception as probe_exc:
        logger.error(f'[FIXTURE-SETUP] {test_name}: HTTP probe FAILED: {probe_exc}')

    # Create a new browser context ..
    context = playwright_browser.new_context()

    # .. open a page ..
    page = context.new_page()

    # .. listen for page crashes and unexpected closes ..
    _close_reasons = [] # type: list

    def _on_page_crash() -> 'None':
        _close_reasons.append('PAGE_CRASH')
        logger.debug(f'[PAGE-EVENT] {test_name}: page renderer stopped')

    def _on_page_close(_p:'any_') -> 'None':
        _close_reasons.append('PAGE_CLOSE')
        import traceback
        stack = ''.join(traceback.format_stack())
        logger.debug(f'[PAGE-EVENT] {test_name}: PAGE CLOSED, stack:\n{stack}')

    def _on_context_close(_c:'any_') -> 'None':
        _close_reasons.append('CONTEXT_CLOSE')
        import traceback
        stack = ''.join(traceback.format_stack())
        logger.debug(f'[PAGE-EVENT] {test_name}: CONTEXT CLOSED, stack:\n{stack}')

    page.on('crash', _on_page_crash)
    page.on('close', _on_page_close)
    context.on('close', _on_context_close)

    # .. capture browser console messages tagged with DIAG ..
    def _on_console(msg:'any_') -> 'None':
        text = msg.text
        if 'DIAG' in text:
            logger.info(f'[BROWSER] {test_name}: {text}')

    page.on('console', _on_console)

    # .. also capture all response errors from the dashboard ..
    def _on_response(response:'any_') -> 'None':
        if response.status >= 400:
            logger.warning(f'[HTTP] {test_name}: {response.status} {response.url}')

    page.on('response', _on_response)

    # .. log into the dashboard ..
    password = zato_dashboard['password']

    try:
        login_to_dashboard(page, dashboard_url, password)
    except Exception as login_exc:
        # Dump full diagnostic state on login failure
        logger.error(
            f'[FIXTURE-SETUP] {test_name}: LOGIN FAILED: {login_exc}, '
            f'page.is_closed={page.is_closed()}, '
            f'close_reasons={_close_reasons}, '
            f'dashboard_poll={dashboard_process.poll() if dashboard_process else "no-process"}, '
            f'server_poll={server_process.poll() if server_process else "no-process"}, '
            f'browser_connected={playwright_browser.is_connected()}'
        )
        raise

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

# Patterns that are known noise and should not cause test failures.
_Log_Noise_Patterns = [
    'check_latest_version',
    'favicon.ico',
    'Could not determine version',
    'Invalid Basic Auth credentials (groups)',
]

@pytest.fixture(autouse=True)
def check_no_log_errors(zato_dashboard:'anydict', request:'any_') -> 'any_':
    """ Checks server and dashboard log files for ERROR or WARNING lines after each test.
    """

    server_dir = zato_dashboard['server_dir']
    dashboard_dir = zato_dashboard['dashboard_dir']

    # Collect all log files from both server and dashboard ..
    log_dirs = [
        ('server', os.path.join(server_dir, 'logs')),
        ('dashboard', os.path.join(dashboard_dir, 'logs')),
    ]

    # .. record the current size of each log file before the test runs ..
    offsets = {} # type: dict

    for label, log_dir in log_dirs:
        log_files = glob.glob(os.path.join(log_dir, '*.log'))
        for log_file in log_files:
            if os.path.isfile(log_file):
                offsets[(label, log_file)] = os.path.getsize(log_file)

    yield

    # .. after the test, scan for new ERROR or WARNING lines ..
    problems = [] # type: list

    for (label, log_file), offset in offsets.items():

        current_size = os.path.getsize(log_file)

        # .. skip if no new content ..
        if current_size <= offset:
            continue

        with open(log_file, 'r', encoding='utf-8', errors='replace') as log_handle:
            _ = log_handle.seek(offset)
            new_content = log_handle.read()

        for line in new_content.splitlines():

            # .. only care about ERROR and WARNING ..
            if ' - ERROR - ' not in line and ' - WARNING - ' not in line:
                continue

            # .. skip known noise ..
            is_expected = False
            for noise_pattern in _Log_Noise_Patterns:
                if noise_pattern in line:
                    is_expected = True
                    break

            # .. skip patterns declared by the test via the expect_log_errors marker ..
            if not is_expected:
                marker = request.node.get_closest_marker('expect_log_errors')
                if marker:
                    for pattern in marker.args:
                        if pattern in line:
                            is_expected = True
                            break

            if is_expected:
                continue

            problems.append(f'[{label}] {line.strip()}')

    if problems:
        joined = '\n'.join(problems)
        pytest.fail(f'Log errors/warnings during {request.node.name}:\n{joined}')

# ################################################################################################################################
# ################################################################################################################################
