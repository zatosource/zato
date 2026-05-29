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
import sys
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
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_clear_queue_push.conftest')

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_ping_poll_interval   = 0.5

# ################################################################################################################################
# ################################################################################################################################

class _SessionState:
    """ Holds all mutable session state.
    """

    def __init__(self) -> 'None':
        self.server_process:'subprocess.Popen[bytes] | None' = None
        self.quickstart_directory:'str | None' = None

# ################################################################################################################################

    def kill_server(self) -> 'None':
        """ Terminates the server subprocess if it is still running.
        """
        if self.server_process:
            if self.server_process.poll() is None:
                self.server_process.kill()
                _ = self.server_process.wait(timeout=_process_kill_timeout)
                logger.info('Killed server process')

        self.server_process = None
        _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Full teardown.
        """
        if self.quickstart_directory:
            server_log_path = os.path.join(self.quickstart_directory, 'server1', 'logs', 'server.log')
            if os.path.exists(server_log_path):
                shutil.copy(server_log_path, '/tmp/server-logs-clear-queue-push.txt')

        self.kill_server()

        if self.quickstart_directory:
            shutil.rmtree(self.quickstart_directory, ignore_errors=True)

        self.quickstart_directory = None

# ################################################################################################################################
# ################################################################################################################################

_state = _SessionState()
_ = atexit.register(_state.cleanup)

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

def _wait_for_server(host:'str', port:'int', timeout:'int'=_server_wait_timeout) -> 'None':
    """ Polls /zato/ping until 200 or timeout.
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
                    logger.info('Ping OK after %.1fs (attempt %d)', elapsed, attempt_number)
                    return

        except (ConnectionRefusedError, OSError, URLError):
            logger.debug('Ping attempt %d at %.1fs: not ready', attempt_number, elapsed)

        time.sleep(_ping_poll_interval)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _render_template(placeholders:'anydict') -> 'str':
    """ Reads the enmasse YAML template and replaces all {{placeholder}} tokens.
    """
    with open(_template_path, 'r') as template_file:
        out = template_file.read()

    for key, value in placeholders.items():
        token = '{{' + key + '}}'
        out = out.replace(token, str(value))

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'any_':
    """ Session-scoped fixture that spins up a Zato server with push subscriptions.
    """
    from zato.common.test.config_pubsub_clear_queue_push import TestConfig

    # Kill any leftover Zato servers ..
    _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
    time.sleep(2)

    start_time = time.monotonic()

    # Generate passwords ..
    publisher_password = 'test.pub.' + os.urandom(8).hex()
    pusher_a_password  = 'test.push.a.' + os.urandom(8).hex()
    invoke_password    = 'test.invoke.' + os.urandom(8).hex()

    placeholders = {
        'publisher_password': publisher_password,
        'pusher_a_password': pusher_a_password,
    }

    # Create quickstart ..
    _state.quickstart_directory = tempfile.mkdtemp(prefix='zato_clear_queue_push_qs_')

    quickstart_env = os.environ.copy()
    _ = quickstart_env.pop('COVERAGE_PROCESS_START', None)

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
        timeout=_quickstart_timeout, env=quickstart_env)

    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    quickstart_time = time.monotonic()
    logger.info('Quickstart create: %.1fs', quickstart_time - start_time)

    server_directory = os.path.join(_state.quickstart_directory, 'server1')

    # Render and import enmasse ..
    rendered_yaml = _render_template(placeholders)
    rendered_path = os.path.join(_state.quickstart_directory, 'enmasse.yaml')

    with open(rendered_path, 'w') as rendered_file:
        _ = rendered_file.write(rendered_yaml)

    enmasse_env = os.environ.copy()
    enmasse_env['Zato_Needs_Config_Reload'] = 'False'

    enmasse_result = subprocess.run(
        [_zato_bin, 'enmasse', '--import', '--input', rendered_path, server_directory],
        capture_output=True, text=True, check=False,
        timeout=_quickstart_timeout, env=enmasse_env)

    if enmasse_result.returncode != 0:
        raise RuntimeError(f'enmasse import failed:\nstdout: {enmasse_result.stdout}\nstderr: {enmasse_result.stderr}')

    enmasse_time = time.monotonic()
    logger.info('Enmasse import: %.1fs', enmasse_time - quickstart_time)

    # Start the server ..
    server_port = _find_free_port()
    broker_port = _find_free_port()

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(server_port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env['Zato_Stream_Max_Len'] = '3'
    _ = server_env.pop('COVERAGE_PROCESS_START', None)

    _state.server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    popen_time = time.monotonic()
    logger.info('Popen started: %.1fs', popen_time - enmasse_time)

    # .. stream server stdout ..
    def _stream_output() -> 'None':
        stdout = _state.server_process.stdout # type: ignore[union-attr]
        readline = stdout.readline # pyright: ignore[reportOptionalMemberAccess]
        for line in iter(readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - popen_time
            logger.debug('[SERVER %6.1fs] %s', elapsed, text)

    stdout_thread = threading.Thread(target=_stream_output, daemon=True)
    stdout_thread.start()

    # .. wait for server ..
    host = '127.0.0.1'

    try:
        _wait_for_server(host, server_port)
        logger.info('Server ready: %.1fs', time.monotonic() - popen_time)
    except (ConnectionRefusedError, OSError, RuntimeError):
        _state.kill_server()
        raise

    logger.info('Total setup: %.1fs', time.monotonic() - start_time)

    # .. populate TestConfig ..
    TestConfig.base_url           = f'http://{host}:{server_port}'
    TestConfig.invoke_password    = invoke_password
    TestConfig.publisher_username = 'test.pubsub.publisher'
    TestConfig.publisher_password = publisher_password
    TestConfig.pusher_a_username  = 'test.pubsub.pusher.a'
    TestConfig.pusher_a_password  = pusher_a_password
    TestConfig.server_directory   = server_directory

    yield

    _state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
