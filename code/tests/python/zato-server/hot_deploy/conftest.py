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

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.pickup_listener import PickupListener
from zato.common.test.process_util import kill_process_tree, kill_processes_in_directories

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import generator_

    listenergen = generator_[PickupListener, None, None]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.hot_deploy.conftest')

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_ping_poll_interval   = 0.5

# The prefixes of the temporary directories of the environment, which no process other than those of this suite refers to
_quickstart_prefix = 'zato_hot_deploy_qs_'
_project_prefix    = 'zato_hot_deploy_proj_'

# The directories of the project that exist before the listener starts, because it watches only those it finds then
_project_subdirectories = ('services', 'user-conf', 'common')

# The environment variable with the root directory of a project, which the server adds to sys.path and deploys from
_project_root_variable = 'Zato_Project_Root'

# ################################################################################################################################
# ################################################################################################################################

class _SessionState:

    def __init__(self) -> 'None':
        self.server_process:'subprocess.Popen[bytes] | None' = None
        self.listener:'PickupListener | None' = None
        self.quickstart_directory:'str | None' = None
        self.project_directory:'str | None' = None

# ################################################################################################################################

    def kill_server(self) -> 'None':
        if self.server_process:
            kill_process_tree(self.server_process)
            logger.info('Stopped server process')

        self.server_process = None

# ################################################################################################################################

    def kill_listener(self) -> 'None':
        if self.listener:
            self.listener.stop()
            logger.info('Stopped listener process')

        self.listener = None

# ################################################################################################################################

    def cleanup(self) -> 'None':

        if self.quickstart_directory:
            server_log_path = os.path.join(self.quickstart_directory, 'server1', 'logs', 'server.log')
            if os.path.exists(server_log_path):
                _ = shutil.copy(server_log_path, '/tmp/hot-deploy-test-server.log')
                logger.info('Copied server logs to /tmp/hot-deploy-test-server.log')

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
def zato_server() -> 'listenergen':
    """ Spins up a quickstart environment, starts its server and a file listener of a project, yields the listener.
    """
    from zato.common.test.config_hot_deploy import TestConfig

    # A server or a listener that an interrupted run of this suite left behind is stopped, and no other process is
    temp_directory = tempfile.gettempdir()
    quickstart_prefix = os.path.join(temp_directory, _quickstart_prefix)
    project_prefix = os.path.join(temp_directory, _project_prefix)

    kill_processes_in_directories([quickstart_prefix, project_prefix])

    start_time = time.monotonic()

    random_suffix = CryptoManager.generate_hex_string()
    invoke_password = 'test.hotdeploy.' + random_suffix

    # Create quickstart
    _state.quickstart_directory = tempfile.mkdtemp(prefix=_quickstart_prefix)

    quickstart_environment = os.environ.copy()
    _ = quickstart_environment.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', _state.quickstart_directory,
        '--force',
        '--password', invoke_password,
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
    _state.project_directory = tempfile.mkdtemp(prefix=_project_prefix)
    project_dir = _state.project_directory

    for subdirectory in _project_subdirectories:
        os.makedirs(os.path.join(project_dir, 'src', subdirectory), exist_ok=True)

    # Start the server
    server_port = _find_free_port()
    broker_port = _find_free_port()

    server_environment = os.environ.copy()
    server_environment['Zato_Config_Bind_Port'] = str(server_port)
    server_environment['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_environment[_project_root_variable] = project_dir
    _ = server_environment.pop('COVERAGE_PROCESS_START', None)

    # The server runs in a session of its own, so that stopping it reaches each of its processes and no other server
    _state.server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
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
    web_admin_repo_dir = os.path.join(_state.quickstart_directory, 'web-admin', 'config', 'repo')

    _state.listener = PickupListener('hot-deploy', server_directory, web_admin_repo_dir, server_port, project_dir)
    _state.listener.start()

    setup_time = time.monotonic()
    total_elapsed = setup_time - start_time
    logger.info('Total setup: %.1fs', total_elapsed)

    TestConfig.base_url = f'http://{host}:{server_port}'
    TestConfig.password = invoke_password
    TestConfig.server_directory = server_directory
    TestConfig.server_port = server_port
    TestConfig.project_directory = project_dir

    yield _state.listener

    _state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
