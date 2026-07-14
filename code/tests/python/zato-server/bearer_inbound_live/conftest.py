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

_this_directory = os.path.dirname(__file__)
_keycloak_directory = os.path.join(_this_directory, '..', '..', 'zato-common', 'test')

sys.path.insert(0, _this_directory)
sys.path.insert(0, _keycloak_directory)

# pytest
import pytest  # noqa: E402

# Zato
from zato.common.crypto.api import CryptoManager  # noqa: E402
from zato.common.test import kill_server_process  # noqa: E402
from zato.common.util.config import get_config_object, update_config_file  # noqa: E402

# Zato - test helpers
import keycloak_  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, tupnone

# ################################################################################################################################
# ################################################################################################################################

def pytest_report_teststatus(report:'any_', config:'any_') -> 'tupnone':
    if report.when == 'call':
        outcome = report.outcome.upper()
        return report.outcome, f' {outcome} ', f'{outcome} {report.nodeid}'
    return None

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_password = 'test.invoke.' + CryptoManager.generate_hex_string()

# Names of the definitions and channels the tests use
Static_Sec_Def_Name = 'test.bearer.inbound.static'
JWT_Sec_Def_Name    = 'test.bearer.inbound.jwt'

Static_Channel_Path = '/test/bearer/static'
JWT_Channel_Path    = '/test/bearer/jwt'

# The exact token static-mode callers must present
Static_Token = 'test.static.' + CryptoManager.generate_hex_string()

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_enmasse_timeout      = 60
_ping_poll_interval   = 0.5

_server_process = None
_temp_directory = None

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Returns a free TCP port on localhost.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))

        socket_address = tcp_socket.getsockname()

        out = socket_address[1]
        return out

# ################################################################################################################################
# ################################################################################################################################

def _kill_server() -> 'None':
    """ Terminates the server subprocess if it is still running.
    """
    global _server_process

    kill_server_process(_server_process, _process_kill_timeout, server_directory=_temp_directory or '')
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
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        try:
            request = Request(ping_url, method='GET')

            with urlopen(request, timeout=_process_kill_timeout) as response:
                if response.status == OK:
                    return

        except (ConnectionRefusedError, OSError, URLError):
            pass

        time.sleep(_ping_poll_interval)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def run_enmasse(server_directory:'str', enmasse_yaml:'str') -> 'None':
    """ Imports the given enmasse YAML into a running server.
    """
    tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-bearer-inbound-live-{os.getpid()}.yaml')

    try:
        with open(tmp_yaml, 'w') as yaml_file:
            _ = yaml_file.write(enmasse_yaml)

        result = subprocess.run(
            [_zato_bin, 'enmasse', server_directory, '--verbose', '--import', '--input', tmp_yaml],
            capture_output=True, text=True, timeout=_enmasse_timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(f'enmasse --import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    finally:
        if os.path.isfile(tmp_yaml):
            os.unlink(tmp_yaml)

# ################################################################################################################################
# ################################################################################################################################

def build_config_yaml(department:'str'=keycloak_.Department_Accounting) -> 'str':
    """ Returns the enmasse YAML with both bearer token definitions and their REST channels.
    The department parameter lets tests redeploy the JWT definition with a different claim filter.
    """
    token_url = keycloak_.get_token_url()
    issuer = keycloak_.get_issuer()

    out = f'''\
security:
  - name: {Static_Sec_Def_Name}
    type: bearer_token
    static_token: "{Static_Token}"

  - name: {JWT_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_Accounting}
    password: "{keycloak_.Secret_Accounting}"
    auth_endpoint: {token_url}
    issuer: {issuer}
    audience: {keycloak_.Audience_Main}
    claims:
      - {keycloak_.Claim_Department}={department}

channel_rest:
  - name: test.bearer.inbound.static.channel
    service: demo.ping
    url_path: {Static_Channel_Path}
    security: {Static_Sec_Def_Name}

  - name: test.bearer.inbound.jwt.channel
    service: demo.ping
    url_path: {JWT_Channel_Path}
    security: {JWT_Sec_Def_Name}
'''
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - brings up Keycloak, spins up a Zato quickstart environment,
    deploys bearer token definitions and REST channels, and yields connection details.
    """
    global _server_process, _temp_directory

    # Keycloak must be up before the definitions pointing to it are deployed
    keycloak_.ensure_keycloak()

    port = _find_free_port()
    _temp_directory = tempfile.mkdtemp(prefix='zato_bearer_inbound_live_test_')

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', _temp_directory,
        '--servers', '1',
        '--password', _password,
        '--server-api-client-for-scheduler-password', _password,
        '--no-scheduler',
    ]

    result = subprocess.run(
        quickstart_command, capture_output=True, text=True, check=False, timeout=_quickstart_timeout)

    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    # Patch server.conf to use our dynamically allocated port ..
    server_directory = os.path.join(_temp_directory, 'server1')
    repo_location = os.path.join(server_directory, 'config', 'repo')
    config = get_config_object(repo_location, 'server.conf')
    config['main']['port'] = str(port) # pyright: ignore[reportIndexIssue, reportCallIssue, reportArgumentType]
    config['main']['bind'] = f'127.0.0.1:{port}' # pyright: ignore[reportIndexIssue, reportCallIssue, reportArgumentType]
    update_config_file(config, repo_location, 'server.conf') # pyright: ignore[reportArgumentType]

    # .. start the server in foreground mode ..
    broker_port = _find_free_port()

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)

    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # .. persist the server output to a file so startup problems are diagnosable ..
    server_log_path = os.path.join(tempfile.gettempdir(), 'zato_bearer_inbound_live_server.log')
    server_log_file = open(server_log_path, 'w')

    def _stream_server_output() -> 'None':
        """ Reads server stdout line by line and writes it to the persistent log file.
        """
        server_process = _server_process
        assert server_process is not None
        assert server_process.stdout is not None
        stdout = server_process.stdout
        for line in iter(stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            _ = server_log_file.write(text + '\n')
            server_log_file.flush()

    stdout_thread = threading.Thread(target=_stream_server_output, daemon=True)
    stdout_thread.start()

    # .. wait for the server to come up ..
    host = '127.0.0.1'

    try:
        _wait_for_server(host, port)

    except (ConnectionRefusedError, OSError, RuntimeError):

        # .. give the streaming thread a moment to flush any final lines ..
        time.sleep(1)

        print('\n--- Server did not become ready, full server output follows ---\n')

        if os.path.isfile(server_log_path):
            with open(server_log_path) as captured_log:
                print(captured_log.read())

        _kill_server()
        raise

    # .. deploy the bearer token definitions and channels ..
    config_yaml = build_config_yaml()
    run_enmasse(server_directory, config_yaml)

    # .. and yield connection details to the tests.
    yield {
        'host': host,
        'port': port,
        'base_url': f'http://{host}:{port}',
        'static_url': f'http://{host}:{port}{Static_Channel_Path}',
        'jwt_url': f'http://{host}:{port}{JWT_Channel_Path}',
        'static_token': Static_Token,
        'server_directory': server_directory,
    }

    # Teardown - stop the server and remove the temporary directory
    _kill_server()

    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

# ################################################################################################################################
# ################################################################################################################################
