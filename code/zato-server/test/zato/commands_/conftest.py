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
import tempfile
import threading
import time
from http.client import OK
from logging import getLogger
from urllib.error import URLError
from urllib.request import Request, urlopen

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.config import TestConfig
from zato.common.test.process_util import kill_process_tree
from zato.common.typing_ import cast_
from zato.common.util.config import get_config_object, update_config_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato.test.commands.conftest')

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_password = 'test.commands.' + CryptoManager.generate_hex_string()

_ping_request_timeout = 5
_ping_poll_interval   = 0.5
_server_wait_timeout  = 120
_quickstart_timeout   = 180

_server_process = None
_temp_directory = None

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

    kill_process_tree(_server_process)
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
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        try:
            request = Request(ping_url, method='GET')

            with urlopen(request, timeout=_ping_request_timeout) as response:
                if response.status == OK:
                    return

        except (ConnectionRefusedError, OSError, URLError):
            logger.debug('Server at %s:%s is not ready yet', host, port)

        time.sleep(_ping_poll_interval)

    raise Exception(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'any_':
    """ Spins up a quickstart environment of its own so that the CLI has a server to invoke services on.
    """
    global _server_process, _temp_directory

    host = '127.0.0.1'
    port = _find_free_port()

    _temp_directory = tempfile.mkdtemp(prefix='zato_commands_test_')

    # A partially instrumented parent process must not have the new environment collect coverage on its behalf
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
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    server_directory = os.path.join(_temp_directory, 'server1')
    repo_location = os.path.join(server_directory, 'config', 'repo')

    # The CLI reads the server's address from its own configuration, which is why the port
    # goes to server.conf rather than to an environment variable that only the server would see.
    config = cast_('any_', get_config_object(repo_location, 'server.conf'))
    config['main']['bind'] = f'{host}:{port}'
    update_config_file(config, repo_location, 'server.conf')

    server_env = os.environ.copy()
    server_env['Zato_Broker_HTTP_Port'] = str(_find_free_port())
    _ = server_env.pop('COVERAGE_PROCESS_START', None)

    # The new session makes the process the leader of its own group, which is what lets
    # the teardown reach the launcher wrapper and the server that it starts in turn
    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    # The server's output would fill its stdout buffer and stall the process if nothing consumed it
    def _consume_server_output() -> 'None':
        stdout = cast_('any_', _server_process).stdout
        for line in iter(stdout.readline, b''):
            logger.debug('[SERVER] %s', line.decode('utf-8', errors='replace').rstrip())

    stdout_thread = threading.Thread(target=_consume_server_output, daemon=True)
    stdout_thread.start()

    try:
        _wait_for_server(host, port)
    except Exception:
        _kill_server()
        raise

    # This is the server that the CLI invoker will be pointed at
    TestConfig.server_location = server_directory

    yield

    _cleanup()

# ################################################################################################################################
# ################################################################################################################################
