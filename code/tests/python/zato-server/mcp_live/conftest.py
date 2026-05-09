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

# Zato
from zato.common.util.config import get_config_object, update_config_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import NamedTuple
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class _CoverageConfig(NamedTuple): # type: ignore
    coveragerc_path: str
    coverage_data_directory: str

# ################################################################################################################################
# ################################################################################################################################

_zato_base = '/home/dsuch/projects/zatosource-zato/4.1'
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')
_zato_py   = os.path.join(_zato_base, 'code', 'bin', 'python')

_password = 'test.invoke.' + os.urandom(8).hex()

_reports_directory = os.path.join(_zato_base, 'code', 'tests', 'python', 'zato-server', 'mcp_live', 'reports')

_coverage_source = os.path.join(
    _zato_base, 'code', 'zato-server', 'src', 'zato', 'server', 'connection', 'mcp')

_process_kill_timeout     = 5
_server_wait_timeout      = 120
_coverage_combine_timeout = 30
_coverage_html_timeout    = 60
_quickstart_timeout       = 180
_hot_deploy_settle_seconds = 3
_coverage_teardown_wait   = 2
_error_text_max_length    = 80
_ping_poll_interval       = 0.5

_server_process = None
_temp_directory  = None

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Returns a free TCP port on localhost.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))

        out = tcp_socket.getsockname()[1]
        return out

# ################################################################################################################################
# ################################################################################################################################

def _kill_server() -> 'None':
    """ Terminates the server subprocess if it is still running.
    """
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
    """ Kills the server and removes the temporary directory.
    """

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
    """ Polls the server's /zato/ping endpoint until it returns 200 or the timeout expires.
    """

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

def _setup_coverage(temp_directory:'str') -> '_CoverageConfig':
    """ Creates a .coveragerc file for subprocess coverage instrumentation.
    """

    coverage_data_directory = os.path.join(temp_directory, 'coverage')
    os.makedirs(coverage_data_directory, exist_ok=True)

    coveragerc_path = os.path.join(coverage_data_directory, '.coveragerc')

    with open(coveragerc_path, 'w') as coverage_file:
        _ = coverage_file.write(f"""\
[run]
source = {_coverage_source}
data_file = {coverage_data_directory}/.coverage
parallel = true
sigterm = true

[report]
omit =
    */test_*
    *conftest*

[html]
directory = {_reports_directory}
title = MCP Live Test Coverage
""")

    out = _CoverageConfig(coveragerc_path, coverage_data_directory)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _generate_coverage_report(coverage_data_directory:'str', coveragerc_path:'str') -> 'None':
    """ Combines coverage data and generates the HTML report.
    """

    os.makedirs(_reports_directory, exist_ok=True)

    # Combine all coverage data files ..
    _ = subprocess.run(
        [_zato_py, '-m', 'coverage', 'combine', '--rcfile', coveragerc_path, coverage_data_directory],
        capture_output=True,
        check=False,
        timeout=_coverage_combine_timeout,
    )

    # .. and generate the HTML report.
    result = subprocess.run(
        [_zato_py, '-m', 'coverage', 'html', '--rcfile', coveragerc_path],
        capture_output=True,
        text=True,
        check=False,
        timeout=_coverage_html_timeout,
    )

    if result.returncode == 0:
        print(f'\n=== Coverage HTML report: file://{_reports_directory}/index.html ===\n')
    else:
        print(f'\n=== Coverage report generation failed: {result.stderr} ===\n')

# ################################################################################################################################
# ################################################################################################################################

def pytest_addoption(parser:'any_') -> 'None':
    """ Registers the --with-coverage command-line option.
    """
    parser.addoption('--with-coverage', action='store_true', default=False,
                     help='Enable coverage collection on the Zato server subprocess')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server(request:'any_') -> 'any_':
    """ Session-scoped fixture that spins up a Zato quickstart environment,
    starts the server in foreground mode, waits for it to become ready,
    and yields connection details for the MCP tests.
    """

    global _server_process, _temp_directory

    use_coverage = request.config.getoption('--with-coverage')

    start_time = time.monotonic()

    port = _find_free_port()
    _temp_directory = tempfile.mkdtemp(prefix='zato_mcp_live_test_')

    # Create a quickstart environment with a clean env,
    # removing stale COVERAGE_PROCESS_START interference ..
    quickstart_env = os.environ.copy()
    _ = quickstart_env.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', _temp_directory,
        '--servers', '1',
        '--password', _password,
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

    # .. patch server.conf to use our dynamically allocated port ..
    server_directory = os.path.join(_temp_directory, 'server1')
    repo_location = os.path.join(server_directory, 'config', 'repo')
    config = get_config_object(repo_location, 'server.conf')
    config['main']['port'] = str(port) # pyright: ignore[reportIndexIssue, reportCallIssue, reportArgumentType]
    update_config_file(config, repo_location, 'server.conf') # pyright: ignore[reportArgumentType]

    config_time = time.monotonic()
    print(f'[TIMING] config patch: {config_time - quickstart_time:.1f}s')

    # .. optionally set up coverage instrumentation ..
    coveragerc_path = None
    coverage_data_directory = None

    if use_coverage:
        coverage_config = _setup_coverage(_temp_directory)
        coveragerc_path = coverage_config.coveragerc_path
        coverage_data_directory = coverage_config.coverage_data_directory

    # .. start the server in foreground mode ..
    broker_port = _find_free_port()

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    _ = server_env.pop('COVERAGE_PROCESS_START', None)

    if use_coverage:
        server_env['COVERAGE_PROCESS_START'] = coveragerc_path # pyright: ignore[reportArgumentType]

    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    popen_time = time.monotonic()
    print(f'[TIMING] Popen started: {popen_time - config_time:.1f}s')

    # .. stream server stdout in a background thread so we can see startup logs ..
    def _stream_server_output() -> 'None':
        """ Reads server stdout line by line and prints each with a timestamp prefix.
        """
        for line in iter(_server_process.stdout.readline, b''):  # type: ignore
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
        print(f'[TIMING] total setup: {ready_time - start_time:.1f}s')

    except (ConnectionRefusedError, OSError, RuntimeError):
        print('\n--- Server did not become ready, stdout was streamed above ---\n')
        _kill_server()
        raise

    # .. the default MCP channel auto-creates on /mcp/demo during server startup,
    # but demo.echo is hot-deployed a moment later, so we give it a few seconds
    # to ensure the tool registry is built with the deployed service ..
    time.sleep(_hot_deploy_settle_seconds)

    mcp_url = f'http://{host}:{port}/mcp/demo'

    # .. yield connection details to the tests.
    yield {
        'host': host,
        'port': port,
        'password': _password,
        'mcp_url': mcp_url,
        'server_directory': server_directory,
        'temp_directory': _temp_directory,
    }

    # Teardown: stop the server, optionally generate coverage report ..
    _kill_server()

    if use_coverage:
        if coverage_data_directory:
            if coveragerc_path:
                time.sleep(_coverage_teardown_wait)
                _generate_coverage_report(coverage_data_directory, coveragerc_path)

    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

# ################################################################################################################################
# ################################################################################################################################
