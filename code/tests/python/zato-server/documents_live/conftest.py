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
from importlib.util import module_from_spec, spec_from_file_location
from urllib.error import URLError
from urllib.request import Request, urlopen

_this_directory = os.path.dirname(__file__)
sys.path.insert(0, _this_directory)

# pytest
import pytest  # noqa: E402

# Zato
from zato.common.api import EMAIL  # noqa: E402
from zato.common.crypto.api import CryptoManager  # noqa: E402
from zato.common.test import kill_server_process  # noqa: E402
from zato.common.util.config import get_config_object, update_config_file  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

def _load_imap_test_server() -> 'any_':
    """ The demo IMAP server is the IMAP scheduler suite's own - it is loaded from its file so that suite's conftest
    does not get in the way of ours.
    """
    path = os.path.abspath(os.path.join(_this_directory, '..', 'email_imap_scheduler', '_imap_test_server.py'))

    spec = spec_from_file_location('_imap_test_server', path)
    assert spec is not None
    assert spec.loader is not None

    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    out = module.IMAPTestServer
    return out

IMAPTestServer = _load_imap_test_server()

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

_scheduler = EMAIL.IMAP.Scheduler

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_password = 'test.invoke.' + CryptoManager.generate_hex_string()

_services_path = os.path.join(_this_directory, '_services.py')

# The services deployed from pickup - one invoked per attachment, one per message
Attachment_Service_Name = 'test.documents.attachment'
Message_Service_Name = 'test.documents.message'

# The IMAP connections enmasse creates, both reading the same demo mailbox
Attachment_Conn_Name = 'test.documents.each-attachment'
Message_Conn_Name = 'test.documents.message'

Mailbox_User = 'referrals@direct.example.com'
Mailbox_Password = 'test-password'

# Far enough ahead for the connections' jobs never to fire during a test run even if a scheduler were running
Start_Date = '2099-01-01 08:00:00'

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_enmasse_timeout      = 90
_enmasse_missing_wait = 15
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
    _kill_server()

    global _temp_directory

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
    tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-documents-live-{os.getpid()}.yaml')

    try:
        with open(tmp_yaml, 'w') as yaml_file:
            _ = yaml_file.write(enmasse_yaml)

        result = subprocess.run(
            [_zato_bin, 'enmasse', server_directory, '--verbose', '--import', '--input', tmp_yaml,
                '--missing-wait-time', str(_enmasse_missing_wait)],
            capture_output=True, text=True, timeout=_enmasse_timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(f'enmasse --import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    finally:
        if os.path.isfile(tmp_yaml):
            os.unlink(tmp_yaml)

# ################################################################################################################################
# ################################################################################################################################

def build_config_yaml(imap_host:'str', imap_port:'int') -> 'str':
    """ Returns the enmasse YAML with the two IMAP connections pointing to the demo IMAP server, one invoking
    its service per attachment and the other per message.
    """
    out = f'''\
email_imap:
  - name: {Attachment_Conn_Name}
    host: {imap_host}
    port: {imap_port}
    username: {Mailbox_User}
    password: {Mailbox_Password}
    mode: {EMAIL.IMAP.MODE.PLAIN}
    get_criteria: UNSEEN
    timeout: 5
    scheduler_service: {Attachment_Service_Name}
    scheduler_run_every: 1
    scheduler_run_unit: {_scheduler.Unit.Minutes}
    scheduler_start_date: '{Start_Date}'
    scheduler_invoke_with: {_scheduler.InvokeWith.EachAttachment}

  - name: {Message_Conn_Name}
    host: {imap_host}
    port: {imap_port}
    username: {Mailbox_User}
    password: {Mailbox_Password}
    mode: {EMAIL.IMAP.MODE.PLAIN}
    get_criteria: UNSEEN
    timeout: 5
    scheduler_service: {Message_Service_Name}
    scheduler_run_every: 1
    scheduler_run_unit: {_scheduler.Unit.Minutes}
    scheduler_start_date: '{Start_Date}'
    scheduler_invoke_with: {_scheduler.InvokeWith.Message}
'''
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def imap_test_server() -> 'any_':
    server = IMAPTestServer()
    server.required_password = Mailbox_Password
    server.start()
    yield server
    server.stop()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server(imap_test_server:'any_') -> 'any_':
    """ Session-scoped fixture - spins up a Zato quickstart environment with the test services deployed from pickup,
    creates the IMAP connections through enmasse and yields connection details.
    """
    global _server_process, _temp_directory

    port = _find_free_port()
    _temp_directory = tempfile.mkdtemp(prefix='zato_documents_live_test_')

    evidence_file = os.path.join(_temp_directory, 'documents.jsonl')

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
    _ = shutil.copy2(_services_path, os.path.join(pickup_directory, 'documents_test_services.py'))

    # .. start the server in foreground mode, telling the services where to record what they receive ..
    broker_port = _find_free_port()

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env['Zato_Test_Documents_Evidence'] = evidence_file

    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # .. persist the server output to a file so startup problems are diagnosable ..
    server_log_path = os.path.join(tempfile.gettempdir(), 'zato_documents_live_server.log')
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

    # .. create the IMAP connections ..
    run_enmasse(server_directory, build_config_yaml(imap_test_server.host, imap_test_server.port))

    # .. and yield connection details to the tests.
    yield {
        'host': host,
        'port': port,
        'base_url': f'http://{host}:{port}',
        'invoke_password': _password,
        'server_directory': server_directory,
        'evidence_file': evidence_file,
        'server_log_path': server_log_path,
    }

    # Teardown - stop the server and remove the temporary directory
    _kill_server()

    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

# ################################################################################################################################
# ################################################################################################################################
