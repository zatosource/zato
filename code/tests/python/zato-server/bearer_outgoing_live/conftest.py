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
from zato.common.test.private_key_jwt import generate_ec_private_key_pem, generate_rsa_private_key_pem  # noqa: E402
from zato.common.util.config import get_config_object, update_config_file  # noqa: E402

# Zato - test helpers
import keycloak_  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict, tupnone

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

_services_path = os.path.join(_this_directory, '_services.py')

# The services deployed from pickup that call outgoing connections on behalf of the tests
Call_Service_Name      = 'test.bearer.outgoing.call'
FHIR_Read_Service_Name = 'test.bearer.outgoing.fhir.read'

# The FHIR side - a fake FHIR server whose token endpoint takes client assertions, the client it knows
# and the one resource the tests read through it
FHIR_Sec_Def_Name  = 'test.bearer.outgoing.fhir'
FHIR_Outconn_Name  = 'test.bearer.outgoing.fhir.conn'
FHIR_Client_ID     = 'zato-test-fhir-client'
FHIR_Client_Secret = 'test.fhir.' + CryptoManager.generate_hex_string()
FHIR_Patient_ID    = 'bearer-outgoing-1'

# The definition the channel uses to verify tokens Keycloak issued to the JWT clients
Channel_Sec_Def_Name = 'test.bearer.outgoing.channel'
Channel_Path = '/test/bearer/outgoing'

# Outgoing definitions and connections, one per key family plus one whose key Keycloak does not know
RSA_Sec_Def_Name     = 'test.bearer.outgoing.rsa'
EC_Sec_Def_Name      = 'test.bearer.outgoing.ec'
Unknown_Sec_Def_Name = 'test.bearer.outgoing.unknown'

RSA_Outconn_Name     = 'test.bearer.outgoing.rsa.conn'
EC_Outconn_Name      = 'test.bearer.outgoing.ec.conn'
Unknown_Outconn_Name = 'test.bearer.outgoing.unknown.conn'

# Key IDs registered with Keycloak - the RSA client knows both of its keys from the start,
# so rotating the definition from one to the other needs no change on the Keycloak side
Key_ID_RSA_Primary = 'zato-test-rsa-key-1'
Key_ID_RSA_Rotated = 'zato-test-rsa-key-2'
Key_ID_EC          = 'zato-test-ec-key-1'
Key_ID_Unknown     = 'zato-test-unknown-key'

# Environment variables the enmasse YAML reads the private keys from
Env_RSA_Primary = 'Zato_Test_Bearer_RSA_Primary'
Env_RSA_Rotated = 'Zato_Test_Bearer_RSA_Rotated'
Env_EC          = 'Zato_Test_Bearer_EC'
Env_Unknown     = 'Zato_Test_Bearer_Unknown'

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_enmasse_timeout      = 60
_ping_poll_interval   = 0.5

_server_process = None
_temp_directory = None

# ################################################################################################################################
# ################################################################################################################################

class Keys:
    """ The private keys a test run signs with, generated once per session.
    """
    def __init__(self) -> 'None':
        self.rsa_primary = generate_rsa_private_key_pem()
        self.rsa_rotated = generate_rsa_private_key_pem()
        self.ec = generate_ec_private_key_pem()
        self.unknown = generate_rsa_private_key_pem()

    def as_environ(self) -> 'strdict':
        """ Returns the keys under the names the enmasse YAML reads them from.
        """
        out = {
            Env_RSA_Primary: self.rsa_primary,
            Env_RSA_Rotated: self.rsa_rotated,
            Env_EC: self.ec,
            Env_Unknown: self.unknown,
        }
        return out

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

def run_enmasse(server_directory:'str', enmasse_yaml:'str', keys:'Keys') -> 'None':
    """ Imports the given enmasse YAML into a running server, with the private keys passed through the environment
    rather than written into the YAML.
    """
    tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-bearer-outgoing-live-{os.getpid()}.yaml')

    enmasse_env = os.environ.copy()
    enmasse_env.update(keys.as_environ())

    try:
        with open(tmp_yaml, 'w') as yaml_file:
            _ = yaml_file.write(enmasse_yaml)

        result = subprocess.run(
            [_zato_bin, 'enmasse', server_directory, '--verbose', '--import', '--input', tmp_yaml],
            capture_output=True, text=True, timeout=_enmasse_timeout, env=enmasse_env,
        )

        if result.returncode != 0:
            raise RuntimeError(f'enmasse --import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    finally:
        if os.path.isfile(tmp_yaml):
            os.unlink(tmp_yaml)

# ################################################################################################################################

def run_enmasse_export(server_directory:'str') -> 'str':
    """ Exports the server's configuration through enmasse and returns the YAML.
    """
    export_path = os.path.join(tempfile.gettempdir(), f'zato-bearer-outgoing-live-export-{os.getpid()}.yaml')

    try:
        result = subprocess.run(
            [_zato_bin, 'enmasse', server_directory, '--export', '--output', export_path],
            capture_output=True, text=True, timeout=_enmasse_timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(f'enmasse --export failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

        with open(export_path) as export_file:
            out = export_file.read()

        return out

    finally:
        if os.path.isfile(export_path):
            os.unlink(export_path)

# ################################################################################################################################
# ################################################################################################################################

def build_config_yaml(
    server_port:'int',
    fhir_server:'FHIRTestServer',
    rsa_env:'str'=Env_RSA_Primary,
    rsa_key_id:'str'=Key_ID_RSA_Primary,
    ) -> 'str':
    """ Returns the enmasse YAML with the channel that verifies Keycloak tokens, the private key JWT definitions,
    the outgoing connections that call the channel through them and the FHIR connection that logs in to the fake
    FHIR server with an assertion. The RSA parameters let tests redeploy the RSA definition with its rotated key.
    """
    token_url = keycloak_.get_token_url()
    issuer = keycloak_.get_issuer()
    host = f'http://127.0.0.1:{server_port}'

    out = f'''\
security:
  - name: {Channel_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_JWT_RSA}
    auth_endpoint: {token_url}
    issuer: {issuer}
    audience: {keycloak_.Audience_Main}

  - name: {RSA_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_JWT_RSA}
    auth_endpoint: {token_url}
    client_auth_method: {OAuth.Client_Auth_Method.Private_Key_JWT}
    jwt_algorithm: {OAuth.JWT_Algorithm.RS384}
    key_id: {rsa_key_id}
    private_key: Zato_Enmasse_Env.{rsa_env}

  - name: {EC_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_JWT_EC}
    auth_endpoint: {token_url}
    client_auth_method: {OAuth.Client_Auth_Method.Private_Key_JWT}
    jwt_algorithm: {OAuth.JWT_Algorithm.ES384}
    key_id: {Key_ID_EC}
    private_key: Zato_Enmasse_Env.{Env_EC}

  - name: {Unknown_Sec_Def_Name}
    type: bearer_token
    username: {keycloak_.Client_JWT_RSA}
    auth_endpoint: {token_url}
    client_auth_method: {OAuth.Client_Auth_Method.Private_Key_JWT}
    jwt_algorithm: {OAuth.JWT_Algorithm.RS384}
    key_id: {Key_ID_Unknown}
    private_key: Zato_Enmasse_Env.{Env_Unknown}

  - name: {FHIR_Sec_Def_Name}
    type: bearer_token
    username: {FHIR_Client_ID}
    auth_endpoint: {fhir_server.token_endpoint}
    client_auth_method: {OAuth.Client_Auth_Method.Private_Key_JWT}
    jwt_algorithm: {OAuth.JWT_Algorithm.RS384}
    key_id: {Key_ID_RSA_Primary}
    private_key: Zato_Enmasse_Env.{Env_RSA_Primary}
    scopes: system/Patient.read

channel_rest:
  - name: test.bearer.outgoing.channel
    service: demo.ping
    url_path: {Channel_Path}
    security: {Channel_Sec_Def_Name}

outgoing_rest:
  - name: {RSA_Outconn_Name}
    host: {host}
    url_path: {Channel_Path}
    security: {RSA_Sec_Def_Name}

  - name: {EC_Outconn_Name}
    host: {host}
    url_path: {Channel_Path}
    security: {EC_Sec_Def_Name}

  - name: {Unknown_Outconn_Name}
    host: {host}
    url_path: {Channel_Path}
    security: {Unknown_Sec_Def_Name}

outgoing_fhir:
  - name: {FHIR_Outconn_Name}
    address: {fhir_server.address}
    security: {FHIR_Sec_Def_Name}
'''
    return out

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

    # .. and the EC client has a single P-384 key.
    ec_jwks = {
        'keys': [
            get_public_jwk(ec, OAuth.JWT_Algorithm.ES384, Key_ID_EC),
        ]
    }

    keycloak_.provision_jwt_client(keycloak_.Client_JWT_EC, ec_jwks, OAuth.JWT_Algorithm.ES384)

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
        [_zato_bin, 'start', server_directory, '--fg'],
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
