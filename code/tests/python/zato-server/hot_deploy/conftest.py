# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import logging
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
from http.client import OK
from urllib.error import URLError
from urllib.request import Request, urlopen


# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.hot_deploy.conftest')

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')
_listener_script = os.path.join(_zato_base, 'code', 'zato-common', 'src', 'zato', 'common', 'file_transfer', 'listener.py')
_python_bin = os.path.join(_zato_base, 'code', 'bin', 'py')

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_ping_poll_interval   = 0.5

# ################################################################################################################################
# ################################################################################################################################

class _SessionState:

    def __init__(self) -> 'None':
        self.server_process:'subprocess.Popen[bytes] | None' = None
        self.listener_process:'subprocess.Popen[bytes] | None' = None
        self.quickstart_directory:'str | None' = None
        self.project_directory:'str | None' = None

# ################################################################################################################################

    def kill_server(self) -> 'None':
        if self.server_process:
            if self.server_process.poll() is None:
                self.server_process.kill()
                _ = self.server_process.wait(timeout=_process_kill_timeout)
                logger.info('Killed server process')

        self.server_process = None
        _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)

# ################################################################################################################################

    def kill_listener(self) -> 'None':
        if self.listener_process:
            if self.listener_process.poll() is None:
                self.listener_process.kill()
                _ = self.listener_process.wait(timeout=_process_kill_timeout)
                logger.info('Killed listener process')

        self.listener_process = None

# ################################################################################################################################

    def cleanup(self) -> 'None':

        if self.quickstart_directory:
            server_log_path = os.path.join(self.quickstart_directory, 'server1', 'logs', 'server.log')
            if os.path.exists(server_log_path):
                shutil.copy(server_log_path, '/tmp/hot-deploy-test-server.log')
                logger.info('Copied server logs to /tmp/hot-deploy-test-server.log')

            listener_log_path = os.path.join(self.quickstart_directory, 'listener.log')
            if os.path.exists(listener_log_path):
                shutil.copy(listener_log_path, '/tmp/hot-deploy-test-listener.log')
                logger.info('Copied listener logs to /tmp/hot-deploy-test-listener.log')

        self.kill_listener()
        self.kill_server()

        if self.quickstart_directory:
            shutil.rmtree(self.quickstart_directory, ignore_errors=True)
            logger.info('Removed quickstart directory %s', self.quickstart_directory)

        if self.project_directory:
            shutil.rmtree(self.project_directory, ignore_errors=True)
            logger.info('Removed project directory %s', self.project_directory)

        self.quickstart_directory = None
        self.project_directory = None

# ################################################################################################################################
# ################################################################################################################################

_state = _SessionState()
_ = atexit.register(_state.cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        socket_name = tcp_socket.getsockname()
        out = socket_name[1]
        return out

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'str', port:'int', timeout:'int'=_server_wait_timeout) -> 'None':

    ping_url = f'http://{host}:{port}/zato/ping'
    start_time = time.monotonic()
    deadline = start_time + timeout
    attempt_number = 0

    while time.monotonic() < deadline:

        attempt_number += 1
        current_time = time.monotonic()
        elapsed = current_time - start_time

        try:
            request = Request(ping_url, method='GET')

            with urlopen(request, timeout=_process_kill_timeout) as response:
                if response.status == OK:
                    logger.info('Ping OK after %.1fs (attempt %d)', elapsed, attempt_number)
                    return

        except (ConnectionRefusedError, OSError, URLError):
            logger.debug('Ping attempt %d at %.1fs: not ready', attempt_number, elapsed)

        time.sleep(_ping_poll_interval)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'any_':
    """ Spins up a quickstart environment, starts server and file listener, yields config.
    """
    from zato.common.test.config_hot_deploy import TestConfig

    _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
    time.sleep(2)

    start_time = time.monotonic()

    random_bytes = os.urandom(8)
    random_suffix = random_bytes.hex()
    invoke_password = 'test.hotdeploy.' + random_suffix

    # Create quickstart
    _state.quickstart_directory = tempfile.mkdtemp(prefix='zato_hot_deploy_qs_')

    quickstart_environment = os.environ.copy()
    _ = quickstart_environment.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', _state.quickstart_directory,
        '--force',
        '--password', invoke_password,
        '--servers', '1',
        '--server-api-client-for-scheduler-password', invoke_password,
        '--no-scheduler',
    ]

    result = subprocess.run(
        quickstart_command, capture_output=True, text=True, check=False,
        timeout=_quickstart_timeout, env=quickstart_environment)

    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    quickstart_time = time.monotonic()
    quickstart_elapsed = quickstart_time - start_time
    logger.info('Quickstart create: %.1fs', quickstart_elapsed)

    server_directory = os.path.join(_state.quickstart_directory, 'server1')

    # Create the project directory that the listener will watch
    _state.project_directory = tempfile.mkdtemp(prefix='zato_hot_deploy_proj_')
    project_dir = _state.project_directory

    # Create the subdirectories the listener expects
    os.makedirs(os.path.join(project_dir, 'src', 'services'), exist_ok=True)
    os.makedirs(os.path.join(project_dir, 'src', 'user-conf'), exist_ok=True)

    # Start the server
    server_port = _find_free_port()
    broker_port = _find_free_port()

    server_environment = os.environ.copy()
    server_environment['Zato_Config_Bind_Port'] = str(server_port)
    server_environment['Zato_Broker_HTTP_Port'] = str(broker_port)
    _ = server_environment.pop('COVERAGE_PROCESS_START', None)

    _state.server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    popen_time = time.monotonic()

    def _stream_server_output() -> 'None':
        stdout = _state.server_process.stdout # type: ignore[union-attr]
        readline = stdout.readline # pyright: ignore[reportOptionalMemberAccess]
        for line in iter(readline, b''):
            decoded = line.decode('utf-8', errors='replace')
            text = decoded.rstrip()
            current_time = time.monotonic()
            elapsed = current_time - popen_time
            logger.debug('[SERVER %6.1fs] %s', elapsed, text)

    stdout_thread = threading.Thread(target=_stream_server_output, daemon=True)
    stdout_thread.start()

    host = '127.0.0.1'

    try:
        _wait_for_server(host, server_port)
        ready_time = time.monotonic()
        ready_elapsed = ready_time - popen_time
        logger.info('Server ready: %.1fs', ready_elapsed)
    except (ConnectionRefusedError, OSError, RuntimeError):
        logger.error('Server did not become ready')
        _state.kill_server()
        raise

    # Start the file listener pointed at the project directory
    listener_environment = os.environ.copy()
    _ = listener_environment.pop('COVERAGE_PROCESS_START', None)

    web_admin_repo_dir = os.path.join(_state.quickstart_directory, 'web-admin', 'config', 'repo')
    listener_environment['Zato_Web_Admin_Repo_Dir'] = web_admin_repo_dir
    listener_environment['Zato_Config_Bind_Port'] = str(server_port)

    listener_log_path = os.path.join(_state.quickstart_directory, 'listener.log')
    listener_log_file = open(listener_log_path, 'w')

    _state.listener_process = subprocess.Popen(
        [_python_bin, _listener_script, project_dir, '--observer', 'inotify'],
        env=listener_environment,
        stdout=listener_log_file,
        stderr=subprocess.STDOUT,
    )

    # Give the listener a moment to start
    time.sleep(3)

    # Check if the listener started successfully
    if _state.listener_process.poll() is not None:
        listener_log_file.close()
        with open(listener_log_path, 'r') as f:
            listener_output = f.read()
        raise RuntimeError(f'Listener process died immediately:\n{listener_output}')

    logger.info('Listener started (pid=%d)', _state.listener_process.pid)

    setup_time = time.monotonic()
    total_elapsed = setup_time - start_time
    logger.info('Total setup: %.1fs', total_elapsed)

    TestConfig.base_url = f'http://{host}:{server_port}'
    TestConfig.password = invoke_password
    TestConfig.server_directory = server_directory
    TestConfig.server_port = server_port
    TestConfig.project_directory = project_dir

    yield

    _state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
