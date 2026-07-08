# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import glob
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
from json import dumps
from urllib.request import Request, urlopen

# The live SOAP test server lives in the zato-common SOAP suite so all suites share one implementation.
_soap_lib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'soap', 'lib'))
if _soap_lib_dir not in sys.path:
    sys.path.insert(0, _soap_lib_dir)

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.soap_billing')

_Zato_Base = os.environ['ZATO_TEST_BASE_DIR']
_Zato_Bin  = os.path.join(_Zato_Base, 'code', 'bin', 'zato')

_Password = 'test.soap.billing.' + CryptoManager.generate_hex_string()

# The basic-auth passwords the enmasse YAML resolves from the environment,
# the same way the real configuration files do.
_Gateway_Password_Env_Name   = 'Billing_ERP_Gateway_Password'
_Submitter_Password_Env_Name = 'Billing_ERP_Submitter_Password'

_Process_Kill_Timeout = 5
_Server_Wait_Timeout  = 60
_Quickstart_Timeout   = 120
_Enmasse_Timeout      = 120
_Ping_Poll_Interval   = 0.5

# How long to wait for the imported channels to answer their first invocation
_Readiness_Timeout = 60

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to an ephemeral port and returns its number.
    """

    # Open a TCP socket ..
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))

        # .. extract the assigned port ..
        address = tcp_socket.getsockname()
        out = address[1]

    return out

# ################################################################################################################################
# ################################################################################################################################

def _kill_process(process:'subprocess.Popen | None') -> 'None':
    """ Terminates a subprocess, escalating to kill if it does not exit in time.
    """
    if process:
        if process.poll() is None:

            # Try graceful termination first ..
            process.terminate()

            try:
                process.wait(timeout=_Process_Kill_Timeout)

            # .. escalate to kill if it did not exit.
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=_Process_Kill_Timeout)

# ################################################################################################################################
# ################################################################################################################################

# Shared references for the atexit cleanup below
_cleanup_refs:'anydict' = {
    'server_process': None,
    'temporary_dir': None,
    'has_failures': False,
}

def _cleanup() -> 'None':
    """ Cleans up the server process and the temporary directory.
    """
    _kill_process(_cleanup_refs['server_process'])
    _cleanup_refs['server_process'] = None

    tmp = _cleanup_refs['temporary_dir']
    if tmp and os.path.isdir(tmp) and not _cleanup_refs['has_failures']:
        shutil.rmtree(tmp, ignore_errors=True)
    _cleanup_refs['temporary_dir'] = None

atexit.register(_cleanup)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item:'any_', call:'any_') -> 'any_':
    """ Track test failures so we can skip temp dir cleanup for debugging.
    """
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        _cleanup_refs['has_failures'] = True

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_http(host:'str', port:'int', path:'str', timeout:'int' = _Server_Wait_Timeout) -> 'None':
    """ Polls an HTTP endpoint until it returns 200, or raises after timeout.
    """

    url = f'http://{host}:{port}{path}'
    time_start = time.monotonic()
    deadline = time_start + timeout
    attempt = 0

    while time.monotonic() < deadline:
        attempt += 1
        elapsed = time.monotonic() - time_start

        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=_Process_Kill_Timeout) as response:

                if response.status == OK:
                    logger.info(f'[TIMING] {url} OK after {elapsed:.1f}s (attempt {attempt})')
                    return

        except Exception as exception:
            error_text = str(exception)[:80]
            logger.info(f'[TIMING] {url} attempt {attempt} at {elapsed:.1f}s: {error_text}')

        time.sleep(_Ping_Poll_Interval)

    raise RuntimeError(f'{url} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _stream_output(process:'subprocess.Popen', label:'str', time_reference:'float') -> 'None':
    """ Streams subprocess stdout to the test console with timing information.
    """

    for line in iter(process.stdout.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()
        elapsed = time.monotonic() - time_reference
        logger.info(f'[{label} {elapsed:6.1f}s] {text}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture that creates a quickstart environment and starts its server,
    with this suite's fixture services deploying from pickup during boot.
    """
    time_start = time.monotonic()

    # Allocate dynamic ports ..
    server_port = _find_free_port()
    broker_port = _find_free_port()

    temporary_dir = tempfile.mkdtemp(prefix='zato_soap_billing_test_')
    _cleanup_refs['temporary_dir'] = temporary_dir

    # .. 1) create a quickstart environment ..

    quickstart_env = os.environ.copy()
    quickstart_env.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _Zato_Bin, 'quickstart', 'create', temporary_dir,
        '--servers', '1',
        '--password', _Password,
        '--server-api-client-for-scheduler-password', _Password,
        '--no-scheduler',
    ]

    result = subprocess.run(quickstart_command, capture_output=True, text=True,
        timeout=_Quickstart_Timeout, env=quickstart_env)

    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    time_after_quickstart = time.monotonic()
    logger.info(f'[TIMING] quickstart create: {time_after_quickstart - time_start:.1f}s')

    # .. 2) patch server.conf to bind on our dynamic port ..

    server_dir = os.path.join(temporary_dir, 'server1')
    server_config_path = os.path.join(server_dir, 'config', 'repo', 'server.conf')

    with open(server_config_path, 'r') as server_config_file:
        server_config_content = server_config_file.read()

    server_config_content = re.sub(
        r'^(bind\s*=\s*)\S+',
        f'\\g<1>0.0.0.0:{server_port}',
        server_config_content,
        flags=re.MULTILINE,
    )

    with open(server_config_path, 'w') as server_config_file:
        _ = server_config_file.write(server_config_content)

    # .. 3) copy fixture services into the pickup directory so they deploy during
    # server boot, with no hot-deployment wait ..

    fixtures_services_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'services')
    pickup_services_dir = os.path.join(server_dir, 'pickup', 'incoming', 'services')

    os.makedirs(pickup_services_dir, exist_ok=True)
    for file_name in os.listdir(fixtures_services_dir):
        if file_name.endswith('.py'):
            source_path = os.path.join(fixtures_services_dir, file_name)
            _ = shutil.copy(source_path, pickup_services_dir)
            logger.info('[FIXTURES] copied %s to %s', file_name, pickup_services_dir)

    # .. 4) start the server ..

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(server_port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env.pop('COVERAGE_PROCESS_START', None)

    server_process = subprocess.Popen(
        [_Zato_Bin, 'start', server_dir, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    _cleanup_refs['server_process'] = server_process

    time_after_server_start = time.monotonic()

    server_thread = threading.Thread(
        target=_stream_output, args=(server_process, 'SERVER', time_after_server_start), daemon=True)
    server_thread.start()

    # .. 5) and wait until it is ready.

    host = '127.0.0.1'

    try:
        _wait_for_http(host, server_port, '/zato/ping')
        time_server_ready = time.monotonic()
        logger.info(f'[TIMING] server ready: {time_server_ready - time_after_server_start:.1f}s')
        logger.info(f'[TIMING] total setup: {time_server_ready - time_start:.1f}s')

    except Exception:
        logger.error('Server did not become ready, stdout was streamed above')
        _kill_process(server_process)
        raise

    yield {
        'host': host,
        'server_port': server_port,
        'server_dir': server_dir,
        'temporary_dir': temporary_dir,
        'server_process': server_process,
    }

    # .. teardown: stop the server ..
    _kill_process(server_process)
    _cleanup_refs['server_process'] = None

    # .. and remove the temporary directory only if all tests passed.
    if _cleanup_refs['has_failures']:
        logger.info('[TEARDOWN] Keeping temporary directory for debugging: %s', temporary_dir)
    elif os.path.isdir(temporary_dir):
        shutil.rmtree(temporary_dir, ignore_errors=True)
    _cleanup_refs['temporary_dir'] = None

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def soap_test_server() -> 'any_':
    """ A session-scoped live SOAP server over plain HTTP - the ERP the connections point at.
    """
    from soap_test_server import SOAPTestServer

    server = SOAPTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def soap_test_server_tls() -> 'any_':
    """ A session-scoped live SOAP server over HTTPS with a self-signed certificate.
    """
    from soap_test_server import SOAPTestServer

    server = SOAPTestServer(tls=True)
    server.start()

    yield server

    server.stop()

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_channels(server_port:'int') -> 'None':
    """ Posts a complete invoice to the main channel until the whole path - the channel,
    the connection behind it and the ERP test server - answers with an OK, confirming
    the imported configuration is live.
    """

    url = f'http://127.0.0.1:{server_port}/billing/invoice-header/main'

    body = dumps({
        'invoiceNo': 'INV-READY',
        'customerNo': 'CUST-0001',
        'notes': 'Readiness probe',
        'paymentTerms': '30D',
        'documentDate': '2026-01-15',
        'dueDate': '2026-02-14',
        'currencyCode': 'EUR',
        'contactEmail': 'billing@example.com',
        'yourReference': 'REF-READY',
    }).encode('utf-8')

    deadline = time.monotonic() + _Readiness_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            request = Request(url, data=body, headers={'Content-Type': 'application/json'}, method='POST')
            with urlopen(request, timeout=10) as response:
                if response.status == OK:
                    logger.info('[READINESS] channels are live')
                    return

        except Exception as probe_error:
            last_error = probe_error
            logger.info('[READINESS] not ready yet: %s', str(probe_error)[:120])

        time.sleep(_Ping_Poll_Interval)

    raise RuntimeError(f'Channels did not become ready within {_Readiness_Timeout}s, last error: {last_error!r}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def billing_config(zato_server:'anydict', soap_test_server:'any_', soap_test_server_tls:'any_') -> 'any_':
    """ Renders the enmasse YAML with the test servers' addresses and imports it,
    the same way the real configuration is deployed.
    """

    server_dir = zato_server['server_dir']
    temporary_dir = zato_server['temporary_dir']

    # The passwords the YAML resolves through its Zato_Enmasse_Env references
    gateway_password   = 'gateway.'   + CryptoManager.generate_hex_string()
    submitter_password = 'submitter.' + CryptoManager.generate_hex_string()

    # Render the template with the live addresses ..
    template_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'enmasse.yaml')

    with open(template_path, 'r') as template_file:
        yaml_content = template_file.read()

    yaml_content = yaml_content.replace('{{plain_host}}', soap_test_server.address)
    yaml_content = yaml_content.replace('{{tls_host}}', soap_test_server_tls.address)

    yaml_path = os.path.join(temporary_dir, 'billing-enmasse.yaml')

    with open(yaml_path, 'w') as yaml_file:
        _ = yaml_file.write(yaml_content)

    # .. build the import command and its environment ..
    enmasse_command = [_Zato_Bin, 'enmasse', server_dir, '--import', '--input', yaml_path, '--verbose']

    enmasse_env = os.environ.copy()
    enmasse_env[_Gateway_Password_Env_Name]   = gateway_password
    enmasse_env[_Submitter_Password_Env_Name] = submitter_password
    enmasse_env.pop('COVERAGE_PROCESS_START', None)

    # .. run the import ..
    result = subprocess.run(enmasse_command, capture_output=True, text=True,
        timeout=_Enmasse_Timeout, env=enmasse_env)

    logger.info('[ENMASSE] stdout: %s', result.stdout)
    logger.info('[ENMASSE] stderr: %s', result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    if 'Enmasse OK' not in result.stdout + result.stderr:
        raise RuntimeError(f'enmasse import did not confirm success:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    # .. wait until the imported configuration is live ..
    _wait_for_channels(zato_server['server_port'])

    # .. and hand everything the tests need over to them.
    yield {
        'yaml_path': yaml_path,
        'enmasse_command': enmasse_command,
        'enmasse_env': enmasse_env,
        'gateway_username': 'gateway-user',
        'gateway_password': gateway_password,
        'submitter_username': 'erp-submitter',
        'submitter_password': submitter_password,
    }

# ################################################################################################################################
# ################################################################################################################################

# Patterns that are known noise and should not cause test failures.
_Log_Noise_Patterns = [
    'check_latest_version',
    'favicon.ico',
    'Could not determine version',
    'Invalid Basic Auth credentials (groups)',
    'URL not found',
    'is not active, raising NotFound',

    # The quickstart environment runs without a broker or scheduler,
    # so their connection listeners keep retrying in the background.
    'listener loop exception',
    'queue bridge recv listener',
    'scheduler request listener',
]

@pytest.fixture(autouse=True)
def check_no_log_errors(zato_server:'anydict', billing_config:'anydict', request:'any_') -> 'any_':
    """ Checks server log files for ERROR or WARNING lines after each test. Depends
    on billing_config so its offsets are recorded only after the import completed,
    keeping the import-time and readiness-time noise out of every test's window.
    """

    server_dir = zato_server['server_dir']

    # Record the current size of each log file before the test runs ..
    log_dir = os.path.join(server_dir, 'logs')
    offsets = {} # type: dict

    log_files = glob.glob(os.path.join(log_dir, '*.log'))
    for log_file in log_files:
        if os.path.isfile(log_file):
            offsets[log_file] = os.path.getsize(log_file)

    yield

    # .. after the test, scan for new ERROR or WARNING lines ..
    problems = [] # type: list

    for log_file, offset in offsets.items():

        current_size = os.path.getsize(log_file)

        # .. skip if no new content ..
        if current_size <= offset:
            continue

        with open(log_file, 'r', encoding='utf-8', errors='replace') as log_handle:
            _ = log_handle.seek(offset)
            new_content = log_handle.read()

        for line in new_content.splitlines():

            # .. only care about ERROR and WARNING ..
            if ' - ERROR - ' not in line and ' - WARNING - ' not in line:
                continue

            # .. skip known noise ..
            is_expected = False
            for noise_pattern in _Log_Noise_Patterns:
                if noise_pattern in line:
                    is_expected = True
                    break

            # .. skip patterns declared by the test via the expect_log_errors marker ..
            if not is_expected:
                marker = request.node.get_closest_marker('expect_log_errors')
                if marker:
                    for pattern in marker.args:
                        if pattern in line:
                            is_expected = True
                            break

            if is_expected:
                continue

            problems.append(line.strip())

    if problems:
        joined = '\n'.join(problems)
        pytest.fail(f'Log errors/warnings during {request.node.name}:\n{joined}')

# ################################################################################################################################
# ################################################################################################################################
