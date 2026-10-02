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
sys.path.insert(0, _this_directory)

# pytest
import pytest  # noqa: E402

# Zato
from zato.common.api import HL7  # noqa: E402
from zato.common.crypto.api import CryptoManager  # noqa: E402
from zato.common.test import kill_server_process  # noqa: E402
from zato.common.test.fhir import FHIRTestServer  # noqa: E402
from zato.common.test.fhir.common import auth_type_oauth  # noqa: E402
from zato.common.util.config import get_config_object, update_config_file  # noqa: E402

from _services import Receiver_Path_Env  # noqa: E402

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

_bulk = HL7.BulkExport

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_password = 'test.invoke.' + CryptoManager.generate_hex_string()

_services_path = os.path.join(_this_directory, '_services.py')

# The services deployed from pickup - the destination the exports land at and the one starting an export from code
Receiver_Service_Name = 'test.fhir.bulk.export.receiver'
Start_Service_Name    = 'test.fhir.bulk.export.start'

# The FHIR side - a fake FHIR server with a token endpoint, the client it knows and the resources it holds
FHIR_Sec_Def_Name  = 'test.fhir.bulk.export.bearer'
FHIR_Outconn_Name  = 'test.fhir.bulk.export.conn'
FHIR_Client_ID     = 'zato-test-bulk-export-client'
FHIR_Client_Secret = 'test.bulk.' + CryptoManager.generate_hex_string()

Patient_ID_1   = 'bulk-live-p1'
Patient_ID_2   = 'bulk-live-p2'
Observation_ID = 'bulk-live-o1'
Group_ID       = 'bulk-live-group'

Resources = [
    {'resourceType': 'Patient', 'id': Patient_ID_1, 'active': True},
    {'resourceType': 'Patient', 'id': Patient_ID_2, 'active': True},
    {'resourceType': 'Observation', 'id': Observation_ID, 'subject': {'reference': f'Patient/{Patient_ID_1}'}},
]

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
    tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-fhir-bulk-export-live-{os.getpid()}.yaml')

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

def run_enmasse_export(server_directory:'str') -> 'str':
    """ Exports the server's configuration through enmasse and returns the YAML.
    """
    export_path = os.path.join(tempfile.gettempdir(), f'zato-fhir-bulk-export-live-export-{os.getpid()}.yaml')

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

def build_config_yaml(fhir_server:'FHIRTestServer') -> 'str':
    """ Returns the enmasse YAML with the bearer token definition the connection logs in to the fake FHIR server with
    and the connection itself, its Bulk export tab exporting the whole server to the receiver service on a schedule
    far enough away never to fire during the run - the files stay on disk so the tests can read the job's state.
    """
    out = f'''\
security:
  - name: {FHIR_Sec_Def_Name}
    type: bearer_token
    username: {FHIR_Client_ID}
    password: {FHIR_Client_Secret}
    auth_endpoint: {fhir_server.token_endpoint}

outgoing_fhir:
  - name: {FHIR_Outconn_Name}
    address: {fhir_server.address}
    security: {FHIR_Sec_Def_Name}
    bulk_export:
      is_active: true
      level: system
      run_every: 1
      run_unit: days
      start_date: "2036-01-01T00:00:00"
      delete_files: false
      destinations:
        - name: {Receiver_Service_Name}
          type: service
          connection: {Receiver_Service_Name}
'''
    return out

# ################################################################################################################################
# ################################################################################################################################

def _start_fhir_server() -> 'FHIRTestServer':
    """ Starts the fake FHIR server with the resources the exports carry.
    """
    out = FHIRTestServer(FHIR_Client_ID, FHIR_Client_Secret, auth_type_oauth)
    out.start()

    for resource in Resources:
        _ = out.import_resource(resource)

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture - starts the fake FHIR server, spins up a Zato quickstart environment with the exports
    directory and the receiver's path under the temporary directory, deploys the connection and yields connection details.
    """
    global _server_process, _temp_directory

    fhir_server = _start_fhir_server()

    port = _find_free_port()
    _temp_directory = tempfile.mkdtemp(prefix='zato_fhir_bulk_export_live_test_')

    download_dir = os.path.join(_temp_directory, 'exports')
    receiver_path = os.path.join(_temp_directory, 'received.jsonl')

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

    # .. the services the tests use deploy from pickup during boot ..
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    os.makedirs(pickup_directory, exist_ok=True)
    _ = shutil.copy2(_services_path, os.path.join(pickup_directory, 'fhir_bulk_export_test_services.py'))

    # .. start the server in foreground mode, with the exports and the receiver's file under our directory ..
    broker_port = _find_free_port()

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env[_bulk.Env_Dir] = download_dir
    server_env[Receiver_Path_Env] = receiver_path

    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # .. persist the server output to a file so startup problems are diagnosable ..
    server_log_path = os.path.join(tempfile.gettempdir(), 'zato_fhir_bulk_export_live_server.log')
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

    # .. deploy the definition and the connection ..
    config_yaml = build_config_yaml(fhir_server)
    run_enmasse(server_directory, config_yaml)

    # .. and yield connection details to the tests.
    yield {
        'host': host,
        'port': port,
        'base_url': f'http://{host}:{port}',
        'invoke_password': _password,
        'server_directory': server_directory,
        'download_dir': download_dir,
        'receiver_path': receiver_path,
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
