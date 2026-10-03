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
from zato.common.api import OAuth  # noqa: E402
from zato.common.crypto.api import CryptoManager  # noqa: E402
from zato.common.private_key_jwt import get_public_jwk, get_public_key_pem, load_private_key  # noqa: E402
from zato.common.test import kill_server_process  # noqa: E402
from zato.common.test.fhir import FHIRTestServer  # noqa: E402
from zato.common.test.fhir.common import auth_type_oauth  # noqa: E402
from zato.common.util.config import get_config_object, update_config_file  # noqa: E402

# Zato - test helpers
import keycloak_  # noqa: E402
from bearer_outgoing_config import build_config_yaml, FHIR_Client_ID, FHIR_Patient_ID, Key_ID_EC, Key_ID_RSA_Primary, \
    Key_ID_RSA_Rotated, Keys, run_enmasse, Zato_Bin  # noqa: E402

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

_password = 'test.invoke.' + CryptoManager.generate_hex_string()

_services_path = os.path.join(_this_directory, '_services.py')

# The FHIR server's client secret - the tests log in with an assertion, so only the fake server needs it
FHIR_Client_Secret = 'test.fhir.' + CryptoManager.generate_hex_string()

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
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

def _start_fhir_server(keys:'Keys') -> 'FHIRTestServer':
    """ Starts the fake FHIR server with the public half of the primary RSA key registered for client assertions,
    and one patient for the tests to read.
    """
    rsa_primary = load_private_key(keys.rsa_primary)
    public_key_pem = get_public_key_pem(rsa_primary)

    out = FHIRTestServer(FHIR_Client_ID, FHIR_Client_Secret, auth_type_oauth, public_key_pem=public_key_pem)
    out.start()

    _ = out.import_resource({'resourceType': 'Patient', 'id': FHIR_Patient_ID, 'active': True})

    return out

# ################################################################################################################################
# ################################################################################################################################

def _provision_keycloak(keys:'Keys') -> 'None':
    """ Registers the JWT clients with the public halves of this run's keys.
    """
    rsa_primary = load_private_key(keys.rsa_primary)
    rsa_rotated = load_private_key(keys.rsa_rotated)
    ec = load_private_key(keys.ec)

    # The RSA client accepts both RSA keys so that a rotation is a Zato-only change ..
    rsa_jwks = {
        'keys': [
            get_public_jwk(rsa_primary, OAuth.JWT_Algorithm.RS384, Key_ID_RSA_Primary),
            get_public_jwk(rsa_rotated, OAuth.JWT_Algorithm.RS384, Key_ID_RSA_Rotated),
        ]
    }

    keycloak_.provision_jwt_client(keycloak_.Client_JWT_RSA, rsa_jwks, OAuth.JWT_Algorithm.RS384)

    # .. the EC client has a single P-384 key ..
    ec_jwks = {
        'keys': [
            get_public_jwk(ec, OAuth.JWT_Algorithm.ES384, Key_ID_EC),
        ]
    }

    keycloak_.provision_jwt_client(keycloak_.Client_JWT_EC, ec_jwks, OAuth.JWT_Algorithm.ES384)

    # .. and the unknown-key client knows only the primary RSA key, never the one its definition signs with.
    unknown_key_jwks = {
        'keys': [
            get_public_jwk(rsa_primary, OAuth.JWT_Algorithm.RS384, Key_ID_RSA_Primary),
        ]
    }

    keycloak_.provision_jwt_client(keycloak_.Client_JWT_Unknown_Key, unknown_key_jwks, OAuth.JWT_Algorithm.RS384)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - brings up Keycloak with signed JWT clients, spins up a Zato quickstart environment,
    deploys the private key JWT definitions with their outgoing connections and yields connection details.
    """
    global _server_process, _temp_directory

    # Each run signs with keys of its own ..
    keys = Keys()

    # .. and Keycloak must know their public halves before any token is requested ..
    keycloak_.ensure_keycloak()
    _provision_keycloak(keys)

    # .. as must the fake FHIR server.
    fhir_server = _start_fhir_server(keys)

    port = _find_free_port()
    _temp_directory = tempfile.mkdtemp(prefix='zato_bearer_outgoing_live_test_')

    quickstart_command = [
        Zato_Bin, 'quickstart', 'create', _temp_directory,
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

    # .. the service the tests call deploys from pickup during boot ..
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    os.makedirs(pickup_directory, exist_ok=True)
    _ = shutil.copy2(_services_path, os.path.join(pickup_directory, 'bearer_outgoing_test_services.py'))

    # .. start the server in foreground mode ..
    broker_port = _find_free_port()

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)

    _server_process = subprocess.Popen(
        [Zato_Bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # .. persist the server output to a file so startup problems are diagnosable ..
    server_log_path = os.path.join(tempfile.gettempdir(), 'zato_bearer_outgoing_live_server.log')
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

    # .. deploy the definitions, the channel and the outgoing connections ..
    config_yaml = build_config_yaml(port, fhir_server)
    run_enmasse(server_directory, config_yaml, keys)

    # .. and yield connection details to the tests.
    yield {
        'host': host,
        'port': port,
        'base_url': f'http://{host}:{port}',
        'invoke_password': _password,
        'server_directory': server_directory,
        'keys': keys,
        'fhir_server': fhir_server,
    }

    # Teardown - stop both servers and remove the temporary directory
    _kill_server()
    fhir_server.stop()

    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

# ################################################################################################################################
# ################################################################################################################################
