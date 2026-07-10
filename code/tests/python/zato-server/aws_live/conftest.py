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
from urllib.error import URLError
from urllib.request import Request, urlopen

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.aws_live.conftest')

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_services_path = os.path.join(os.path.dirname(__file__), '_services.py')

_conn_name = 'test.cloud.aws'
_conn_region = 'us-east-1'
_conn_access_key_id = 'AKIATESTACCESSKEYLIVE'
_conn_secret_access_key = 'test.aws.secret.' + CryptoManager.generate_hex_string()

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_ping_poll_interval   = 0.5
_conn_ready_timeout   = 60

# ################################################################################################################################
# ################################################################################################################################

class _SessionState:
    """ Holds all mutable session state.
    """

    def __init__(self) -> 'None':
        self.server_process:'subprocess.Popen[bytes] | None' = None
        self.quickstart_directory:'str | None' = None
        self.moto_server:'any_' = None

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

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Full teardown.
        """
        if self.quickstart_directory:
            server_log_path = os.path.join(self.quickstart_directory, 'server1', 'logs', 'server.log')
            if os.path.exists(server_log_path):
                _ = shutil.copy(server_log_path, '/tmp/server-logs-aws-live.txt')

        self.kill_server()

        if self.moto_server:
            self.moto_server.stop()
            self.moto_server = None

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

def _start_server(server_directory:'str', server_port:'int', broker_port:'int') -> 'None':
    """ Starts the Zato server and waits for it to be ready.
    """
    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(server_port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    _ = server_env.pop('COVERAGE_PROCESS_START', None)

    _state.server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    popen_time = time.monotonic()

    def _stream_output() -> 'None':
        stdout = _state.server_process.stdout # type: ignore[union-attr]
        readline = stdout.readline # pyright: ignore[reportOptionalMemberAccess]
        for line in iter(readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - popen_time
            logger.debug('[SERVER %6.1fs] %s', elapsed, text)

    stdout_thread = threading.Thread(target=_stream_output, daemon=True)
    stdout_thread.start()

    host = '127.0.0.1'
    _wait_for_server(host, server_port)
    logger.info('Server ready: %.1fs', time.monotonic() - popen_time)

# ################################################################################################################################
# ################################################################################################################################

def _create_aws_connection(client:'AdminClient', endpoint_url:'str') -> 'None':
    """ Creates the cloud-aws connection that all the tests use, pointing it at the simulator.
    """
    resp = client.create('zato.generic.connection.create',
        cluster_id=1,
        name=_conn_name,
        type_='cloud-aws',
        is_active=True,
        is_internal=False,
        is_channel=False,
        is_outgoing=True,
        is_outconn=False,
        region=_conn_region,
        access_key_id=_conn_access_key_id,
        endpoint_url=endpoint_url,
        secret=_conn_secret_access_key,
        pool_size=1,
    )

    logger.info('Created AWS connection `%s` (id=%s)', _conn_name, resp['id'])

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_aws_connection(client:'AdminClient', timeout:'int'=_conn_ready_timeout) -> 'None':
    """ Polls the deployed ping service until both the service and the connection are usable.
    """
    start_time = time.monotonic()
    deadline = start_time + timeout
    last_error = ''

    while time.monotonic() < deadline:

        try:
            result = client.invoke('test.aws.ping', {'conn_name': _conn_name})
        except Exception as e:
            last_error = str(e)
        else:
            if result['account']:
                elapsed = time.monotonic() - start_time
                logger.info('AWS connection ready after %.1fs', elapsed)
                return

        time.sleep(_ping_poll_interval)

    raise RuntimeError(f'AWS connection `{_conn_name}` was not ready within {timeout}s, last error: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'any_':
    """ Session-scoped fixture that spins up a simulated AWS environment
    plus a Zato server with a cloud-aws connection pointing at it.
    """
    from moto.server import ThreadedMotoServer

    start_time = time.monotonic()

    # Generate the credentials used by the invoke API ..
    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

    # .. start the simulated AWS environment ..
    moto_server = ThreadedMotoServer(port=0)
    moto_server.start()
    moto_host, moto_port = moto_server.get_host_and_port()
    endpoint_url = f'http://{moto_host}:{moto_port}'
    _state.moto_server = moto_server

    logger.info('Simulated AWS environment started at %s', endpoint_url)

    # .. create a quickstart environment ..
    _state.quickstart_directory = tempfile.mkdtemp(prefix='zato_aws_live_qs_')

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

    # .. drop the test services into the pickup directory so the boot scan deploys them ..
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    _ = shutil.copy2(_services_path, os.path.join(pickup_directory, 'aws_test_services.py'))

    # .. patch server.conf so the server binds to a dynamically allocated port ..
    server_conf_path = os.path.join(server_directory, 'config', 'repo', 'server.conf')

    with open(server_conf_path, 'r') as server_conf_file:
        server_conf_content = server_conf_file.read()

    server_port = _find_free_port()

    server_conf_content = re.sub(
        r'^(bind\s*=\s*)\S+',
        f'\\g<1>0.0.0.0:{server_port}',
        server_conf_content,
        flags=re.MULTILINE,
    )

    with open(server_conf_path, 'w') as server_conf_file:
        _ = server_conf_file.write(server_conf_content)

    # .. start the server ..
    broker_port = _find_free_port()
    _start_server(server_directory, server_port, broker_port)

    host = '127.0.0.1'
    base_url = f'http://{host}:{server_port}'

    # .. create the AWS connection pointing at the simulator ..
    client = AdminClient(base_url, invoke_password)
    _create_aws_connection(client, endpoint_url)

    # .. and wait until the deployed services can use it.
    _wait_for_aws_connection(client)

    logger.info('Total setup: %.1fs', time.monotonic() - start_time)

    yield {
        'host': host,
        'port': server_port,
        'invoke_password': invoke_password,
        'base_url': base_url,
        'conn_name': _conn_name,
        'endpoint_url': endpoint_url,
        'server_directory': server_directory,
    }

    _state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
