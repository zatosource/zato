# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
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
from http.client import OK
from urllib.request import Request, urlopen

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# Make this directory importable so test modules can use the helpers defined below
_suite_dir = os.path.dirname(__file__)
if _suite_dir not in sys.path:
    sys.path.insert(0, _suite_dir)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.logging')

_Zato_Base = os.environ['ZATO_TEST_BASE_DIR']
_Zato_Bin  = os.path.join(_Zato_Base, 'code', 'bin', 'zato')

_Password = 'test.logging.' + CryptoManager.generate_hex_string()

# The creation-time variables under test - the generated logging.conf must carry these values
Log_Max_Size     = '5000000'
Log_Backup_Count = '7'

# The runtime variables under test - the server starts with these levels
Log_Level_Global = 'DEBUG'
Log_Level_Rest   = 'WARN'

_Process_Kill_Timeout = 5
_Server_Wait_Timeout  = 60
_Quickstart_Timeout   = 120
_Ping_Poll_Interval   = 0.5

# How long to wait for expected content to show up in a log file
Log_Content_Timeout = 30

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

def read_log_file(server_dir:'str', file_name:'str') -> 'str':
    """ Returns the full contents of a log file from the server's logs directory.
    """
    log_path = os.path.join(server_dir, 'logs', file_name)

    with open(log_path, 'r', encoding='utf-8', errors='replace') as log_file:
        out = log_file.read()

    return out

# ################################################################################################################################
# ################################################################################################################################

def wait_for_log_content(server_dir:'str', file_name:'str', needle:'str', timeout:'int'=Log_Content_Timeout) -> 'str':
    """ Polls a log file until the given text appears in it, returning the full contents,
    or raises after the timeout.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        contents = read_log_file(server_dir, file_name)

        if needle in contents:
            return contents

        time.sleep(_Ping_Poll_Interval)

    raise Exception(f'Text `{needle}` did not appear in {file_name} within {timeout}s')

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

# Shared references for the atexit cleanup below
_cleanup_refs:'anydict' = {
    'server_process': None,
    'temporary_dir': None,
    'has_failures': False,
}

def _cleanup() -> 'None':
    """ Cleans up the server process and the temporary directory.
    """
    _kill_process(_cleanup_refs['server_process'])
    _cleanup_refs['server_process'] = None

    tmp = _cleanup_refs['temporary_dir']
    if tmp and os.path.isdir(tmp) and not _cleanup_refs['has_failures']:
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

def _wait_for_http(host:'str', port:'int', path:'str', timeout:'int'=_Server_Wait_Timeout) -> 'None':
    """ Polls an HTTP endpoint until it returns 200, or raises after timeout.
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

                if response.status == OK:
                    logger.info(f'[TIMING] {url} OK after {elapsed:.1f}s (attempt {attempt})')
                    return

        except Exception as exception:
            logger.info(f'[TIMING] {url} attempt {attempt} at {elapsed:.1f}s: {exception}')

        time.sleep(_Ping_Poll_Interval)

    raise Exception(f'{url} did not respond within {timeout}s')

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
def zato_server() -> 'any_':
    """ Session-scoped fixture that creates a quickstart environment and starts its server.

    The environment is created with Zato_Server_Log_Max_Size and Zato_Server_Log_Backup_Count set
    so the generated logging.conf carries their values, and the server itself starts with
    Zato_Log_Level and Zato_Log_Level_Rest so the runtime overrides are exercised.
    """
    time_start = time.monotonic()

    # Allocate dynamic ports ..
    server_port = _find_free_port()
    broker_port = _find_free_port()

    temporary_dir = tempfile.mkdtemp(prefix='zato_logging_test_')
    _cleanup_refs['temporary_dir'] = temporary_dir

    # .. 1) create a quickstart environment with the creation-time variables under test ..

    quickstart_env = os.environ.copy()
    quickstart_env.pop('COVERAGE_PROCESS_START', None)
    quickstart_env['Zato_Server_Log_Max_Size']     = Log_Max_Size
    quickstart_env['Zato_Server_Log_Backup_Count'] = Log_Backup_Count

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
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

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

    # .. 3) copy fixture services into the pickup directory so they deploy during
    # server boot, with no hot-deployment wait ..

    fixtures_services_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'services')
    pickup_services_dir = os.path.join(server_dir, 'pickup', 'incoming', 'services')

    os.makedirs(pickup_services_dir, exist_ok=True)
    for file_name in os.listdir(fixtures_services_dir):
        if file_name.endswith('.py'):
            source_path = os.path.join(fixtures_services_dir, file_name)
            _ = shutil.copy(source_path, pickup_services_dir)
            logger.info('[FIXTURES] copied %s to %s', file_name, pickup_services_dir)

    # .. 4) start the server with the runtime log level overrides under test ..

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(server_port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env['Zato_Log_Level']        = Log_Level_Global
    server_env['Zato_Log_Level_Rest']   = Log_Level_Rest
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

    # .. 5) and wait until it is ready.

    host = '127.0.0.1'

    try:
        _wait_for_http(host, server_port, '/zato/ping')
        time_server_ready = time.monotonic()
        logger.info(f'[TIMING] server ready: {time_server_ready - time_after_server_start:.1f}s')
        logger.info(f'[TIMING] total setup: {time_server_ready - time_start:.1f}s')

    except Exception:
        logger.error('Server did not become ready, stdout was streamed above')
        _kill_process(server_process)
        raise

    yield {
        'host': host,
        'server_port': server_port,
        'server_dir': server_dir,
        'temporary_dir': temporary_dir,
        'server_process': server_process,
        'password': _Password,
    }

    # .. teardown: stop the server ..
    _kill_process(server_process)
    _cleanup_refs['server_process'] = None

    # .. and remove the temporary directory only if all tests passed.
    if _cleanup_refs['has_failures']:
        logger.info('[TEARDOWN] Keeping temporary directory for debugging: %s', temporary_dir)
    elif os.path.isdir(temporary_dir):
        shutil.rmtree(temporary_dir, ignore_errors=True)
    _cleanup_refs['temporary_dir'] = None

# ################################################################################################################################
# ################################################################################################################################
