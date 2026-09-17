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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib')))

# PyPI
import pytest

# Zato
from _hr_data import Create_Procs, Create_Table, Insert_Row, Seed_Rows
from live_sql.containers import connect_mssql, start_mssql, stop_container

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from live_sql.containers import DatabaseServer
    from zato.common.typing_ import any_, anydict

    servergen = Iterator[DatabaseServer]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.mssql_db_live.conftest')

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

class ModuleCtx:

    # The host port and the name of the MS SQL container
    MSSQL_Port      = 21433
    MSSQL_Container = 'zato-test-mssql-db'

    # The database the HR data lives in
    DB_Name = 'zato_hr'

    # The name of the outgoing connection the enmasse template defines
    Connection_Name = 'test.mssql.db'

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
                _ = shutil.copy(server_log_path, '/tmp/server-logs-mssql-db-live.txt')

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

    raise Exception(f'Server at {host}:{port} did not respond within {timeout}s')

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

def _import_enmasse(server_directory:'str', placeholders:'anydict', needs_reload:'bool') -> 'None':
    """ Renders the enmasse template and imports it into the server's configuration,
    telling a running server to reload it when asked to.
    """
    rendered_yaml = _render_template(placeholders)
    rendered_path = os.path.join(server_directory, 'enmasse-mssql.yaml')

    with open(rendered_path, 'w') as rendered_file:
        _ = rendered_file.write(rendered_yaml)

    enmasse_env = os.environ.copy()
    enmasse_env['Zato_Needs_Config_Reload'] = str(needs_reload)

    enmasse_result = subprocess.run(
        [_zato_bin, 'enmasse', '--import', '--input', rendered_path, server_directory],
        capture_output=True, text=True, check=False,
        timeout=_quickstart_timeout, env=enmasse_env)

    if enmasse_result.returncode != 0:
        raise Exception(f'enmasse import failed:\nstdout: {enmasse_result.stdout}\nstderr: {enmasse_result.stderr}')

# ################################################################################################################################
# ################################################################################################################################

def _seed_hr_schema(port:'int', password:'str', db_name:'str') -> 'None':
    """ Creates the HR table, fills it with the known rows and creates the procedures the tests call.
    """
    connection = connect_mssql(port, password, db_name, True)

    with connection.cursor() as cursor:

        # Create the table ..
        cursor.execute(Create_Table)

        # .. fill it with the rows the tests expect ..
        for row in Seed_Rows:
            cursor.execute(Insert_Row, row)

        # .. and create the procedures that read them.
        for create_proc in Create_Procs:
            cursor.execute(create_proc)

    connection.close()

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
    server_stdout = _state.server_process.stdout

    def _stream_output() -> 'None':
        if not server_stdout:
            return
        for line in iter(server_stdout.readline, b''):
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

@pytest.fixture(scope='session')
def mssql_server() -> 'servergen':
    """ An MS SQL server started on demand in a container, with the HR data already in place.
    """

    # The password has to satisfy the server's complexity policy - upper and lower case letters, digits and a symbol
    password = 'Test.mssql.' + CryptoManager.generate_hex_string()

    server = start_mssql(
        container_name=ModuleCtx.MSSQL_Container,
        port=ModuleCtx.MSSQL_Port,
        password=password,
        db_name=ModuleCtx.DB_Name,
    )

    _seed_hr_schema(ModuleCtx.MSSQL_Port, password, ModuleCtx.DB_Name)

    yield server

    stop_container(server.container_name)

# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server(mssql_server:'DatabaseServer') -> 'any_':
    """ Session-scoped fixture that creates a Zato environment with an outgoing
    MS SQL connection pointing at the container, then starts its server.
    """

    # Kill any leftover Zato servers ..
    _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
    time.sleep(2)

    start_time = time.monotonic()

    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

    details = mssql_server.details

    placeholders = {
        'mssql_host':     details['host'],
        'mssql_port':     details['port'],
        'mssql_username': details['username'],
        'mssql_password': details['password'],
        'mssql_db_name':  details['name'],
    }

    # Create quickstart ..
    _state.quickstart_directory = tempfile.mkdtemp(prefix='zato_mssql_db_live_qs_')

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
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    quickstart_time = time.monotonic()
    logger.info('Quickstart create: %.1fs', quickstart_time - start_time)

    server_directory = os.path.join(_state.quickstart_directory, 'server1')

    # Import the enmasse-defined objects - the server is not running yet so nothing reloads ..
    _import_enmasse(server_directory, placeholders, needs_reload=False)

    enmasse_time = time.monotonic()
    logger.info('Enmasse import: %.1fs', enmasse_time - quickstart_time)

    # Hot-deploy the test services ..
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    _ = shutil.copy2(_services_path, os.path.join(pickup_directory, 'mssql_db_test_services.py'))

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
    _start_server(server_directory, server_port, broker_port)

    logger.info('Total setup: %.1fs', time.monotonic() - start_time)

    host = '127.0.0.1'

    yield {
        'host': host,
        'port': server_port,
        'invoke_password': invoke_password,
        'base_url': f'http://{host}:{server_port}',
        'server_directory': server_directory,
        'placeholders': placeholders,
        'import_enmasse': _import_enmasse,
    }

    _state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
