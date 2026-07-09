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

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'sql_cloud', 'lib'))

# PyPI
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.sql_cloud_live.conftest')

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')
_services_path = os.path.join(os.path.dirname(__file__), '_services.py')

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
        self.snowflake_server:'any_' = None
        self.redshift_server:'any_' = None

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
                shutil.copy(server_log_path, '/tmp/server-logs-sql-cloud-live.txt')

        self.kill_server()

        if self.snowflake_server:
            self.snowflake_server.stop()
            self.snowflake_server = None

        if self.redshift_server:
            self.redshift_server.stop()
            self.redshift_server = None

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

def _start_server(server_directory:'str', server_port:'int', broker_port:'int') -> 'float':
    """ Starts the Zato server and waits for it to be ready. Returns the popen timestamp.
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

    return popen_time

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'any_':
    """ Session-scoped fixture that spins up the Snowflake and Redshift simulators
    plus a Zato server with outgoing SQL connections pointing at them.
    """
    from redshift_test_server import RedshiftTestServer
    from snowflake_test_server import SnowflakeTestServer

    # Kill any leftover Zato servers ..
    _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
    time.sleep(2)

    start_time = time.monotonic()

    # Generate credentials ..
    snowflake_password = 'test.snowflake.' + CryptoManager.generate_hex_string()
    redshift_password  = 'test.redshift.' + CryptoManager.generate_hex_string()
    invoke_password    = 'test.invoke.' + CryptoManager.generate_hex_string()

    # Start the Snowflake simulator over plain HTTP ..
    snowflake_server = SnowflakeTestServer(tls=False)
    snowflake_server.start()
    snowflake_server.configure(password=snowflake_password)
    _state.snowflake_server = snowflake_server

    # .. and the Redshift simulator over a plain TCP socket.
    redshift_server = RedshiftTestServer(tls=False)
    redshift_server.start()
    redshift_server.configure(password=redshift_password)
    _state.redshift_server = redshift_server

    # Both simulators serve the same canned rows the tests query for.
    flight_rows = [[1, 'ZA-101'], [2, 'ZA-102'], [3, 'ZA-103']]

    snowflake_server.add_result(
        r'select id, flight_number from flights',
        columns=[('ID', 'fixed'), ('FLIGHT_NUMBER', 'text')],
        rows=flight_rows,
    )

    redshift_server.add_result(
        r'select id, flight_number from flights',
        columns=[('id', 'int'), ('flight_number', 'text')],
        rows=flight_rows,
    )

    logger.info('Simulators started - snowflake:%d redshift:%d', snowflake_server.port, redshift_server.port)

    # Render the enmasse template ..
    placeholders = {
        'snowflake_password': snowflake_password,
        'snowflake_port': snowflake_server.port,
        'redshift_password': redshift_password,
        'redshift_port': redshift_server.port,
    }

    # Create quickstart ..
    _state.quickstart_directory = tempfile.mkdtemp(prefix='zato_sql_cloud_live_qs_')

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

    # Hot-deploy the test services ..
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    shutil.copy2(_services_path, os.path.join(pickup_directory, 'sql_cloud_test_services.py'))

    # Patch server.conf so CLI commands use the dynamic port ..
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

    # Start the server ..
    broker_port = _find_free_port()
    _ = _start_server(server_directory, server_port, broker_port)

    logger.info('Total setup: %.1fs', time.monotonic() - start_time)

    host = '127.0.0.1'

    yield {
        'host': host,
        'port': server_port,
        'invoke_password': invoke_password,
        'base_url': f'http://{host}:{server_port}',
        'snowflake_server': snowflake_server,
        'redshift_server': redshift_server,
        'server_directory': server_directory,
    }

    _state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
