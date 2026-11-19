# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Generator

# The shared MLLP helpers, e.g. rest_echo_server, live next to the standalone test server,
# after this directory itself so that nothing of the same name is shadowed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'mllp'))
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.test.client import AdminClient as ZatoClient
from zato.common.test.conftest_base_pubsub import create_zato_server_fixture

# Zato - test services deployed to the server under test
from _services import accept_service_source, alert_rule_service_source, audit_counts_service_source, \
    demo_import_service_source, destination_service_source, echo_service_source, error_service_source, \
    fhir_invoke_service_source, fhir_save_service_source, forward_service_source, inspect_service_source

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import logging
    from zato.common.test.conftest_base_pubsub import SessionState
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_zato_base_dir = os.environ['ZATO_TEST_BASE_DIR']
_zato_python   = os.path.join(_zato_base_dir, 'code', 'bin', 'python')

_current_dir = os.path.dirname(__file__)
_mllp_test_server_path = os.path.join(_current_dir, '..', '..', 'zato-common', 'mllp', 'mllp_test_server.py')

_logger_name = 'zato.test.mllp_integration.conftest'

_backend_ready_timeout = 10
_port_wait_timeout     = 10

# The services that the tests invoke, each deployed from the pickup directory when the server starts
_service_files = {
    '_test_hl7_mllp_echo.py':         echo_service_source,
    '_test_hl7_mllp_error.py':        error_service_source,
    '_test_hl7_mllp_forward.py':      forward_service_source,
    '_test_hl7_mllp_inspect.py':      inspect_service_source,
    '_test_hl7_mllp_accept.py':       accept_service_source,
    '_test_hl7_mllp_destinations.py': destination_service_source,
    '_test_hl7_fhir_invoke.py':       fhir_invoke_service_source,
    '_test_hl7_fhir_save.py':         fhir_save_service_source,
    '_test_alerting_rule.py':         alert_rule_service_source,
    '_test_demo_import.py':           demo_import_service_source,
    '_test_hl7_audit_counts.py':      audit_counts_service_source,
}

# The services and the file through which the test services exchange received messages with the test process,
# in a directory that the session removes when it ends
_data_dir = tempfile.mkdtemp(prefix='zato_mllp_test_')
_messages_file = os.path.join(_data_dir, 'mllp_messages.txt')

_extra_server_env = {
    'Zato_Test_MLLP_Messages_File': _messages_file,
}

# What the tests know of the server once it runs
_server_info:'anydict' = {}

# Type aliases for generator-based fixtures
strobj_dict = dict[str, object]
backend_gen = Generator['BackendHandle', None, None]

# ################################################################################################################################
# ################################################################################################################################

def is_port_open(port:'int') -> 'bool':
    """ Returns True if the port accepts TCP connections on localhost.
    """
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_socket.settimeout(2.0)

    try:
        test_socket.connect(('127.0.0.1', port))
        test_socket.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False

# ################################################################################################################################
# ################################################################################################################################

def wait_for_port_open(port:'int', timeout:'int'=_port_wait_timeout) -> 'None':
    """ Polls until the port accepts TCP connections.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        if is_port_open(port):
            return

        time.sleep(0.2)

    raise Exception(f'Port {port} was not open within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def wait_for_port_closed(port:'int', timeout:'int'=_port_wait_timeout) -> 'None':
    """ Polls until the port no longer accepts TCP connections.
    """
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:

        if not is_port_open(port):
            return

        time.sleep(0.2)

    raise Exception(f'Port {port} was not closed within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

def _build_config(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_port:'int',
    invoke_password:'str',
    ) -> 'anydict':
    """ Writes the sources of the test services for the server to deploy when it starts, and returns
    what the tests need once it runs.
    """
    state.test_data_directory = _data_dir

    hot_deploy_sources:'list[str]' = []

    for file_name, source in _service_files.items():
        source_path = os.path.join(_data_dir, file_name)

        with open(source_path, 'w') as source_file:
            _ = source_file.write(source)

        hot_deploy_sources.append(source_path)

    def _populate(
        host:'str',
        server_port:'int',
        invoke_password:'str',
        server_directory:'str',
        zato_bin:'str',
        ) -> 'None':

        # The audit database is the Zato database of the server, which the session selected for both processes
        _server_info['host'] = host
        _server_info['port'] = server_port
        _server_info['mllp_port'] = state.mllp_port
        _server_info['password'] = invoke_password
        _server_info['server_directory'] = server_directory
        _server_info['temp_directory'] = _data_dir
        _server_info['audit_db_path'] = os.environ['Zato_Database_Path']
        _server_info['database'] = state.pubsub_database

    out:'anydict' = {
        'placeholders': {},
        'populate_callback': _populate,
        'hot_deploy_sources': hot_deploy_sources,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

zato_server_process = create_zato_server_fixture(
    logger_name=_logger_name,
    server_log_copy_name='server-logs-mllp-integration.txt',
    template_path='',
    quickstart_prefix='zato_mllp_test_qs_',
    extra_server_env=_extra_server_env,
    patch_server_conf_bind=True,
    build_config_callback=_build_config,
    log_to_files=False,
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server(zato_server_process:'None') -> 'strobj_dict':
    """ Returns the address, the ports, the password and the directories of the server of the session.
    """
    out = dict(_server_info)
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_client(zato_server:'strobj_dict') -> 'ZatoClient':
    """ Creates a ZatoClient connected to the test server.
    """
    base_url = f'http://{zato_server["host"]}:{zato_server["port"]}'

    out = ZatoClient(base_url, str(zato_server['password']))
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mllp_port(zato_server:'strobj_dict') -> 'int':
    """ Returns the port of the internal MLLP server of the server, chosen by the session before the server started.
    """
    out = _server_info['mllp_port']
    return out

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to port 0 to get an OS-assigned free port, then releases it.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temporary_socket:
        temporary_socket.bind(('127.0.0.1', 0))
        _, out = temporary_socket.getsockname()

    return out

@pytest.fixture(scope='session')
def backend_port() -> 'int':
    """ Returns a free port for the standalone MLLP backend to listen on.
    """
    out = _find_free_port()
    return out

# ################################################################################################################################
# ################################################################################################################################

class BackendHandle:
    """ Holds the subprocess and captured stdout lines from the standalone MLLP backend.
    """
    def __init__(self) -> 'None':
        self.process:'subprocess.Popen[bytes] | None' = None
        self.received_lines:'list[str]' = []

# ################################################################################################################################
# ################################################################################################################################

def _run_backend(port:'int', callback_mode:'str', log_prefix:'str') -> 'backend_gen':
    """ Runs the standalone mllp_test_server.py in the callback mode given, captures its stdout
    and stops it once whoever asked for it is done with it.
    """

    handle = BackendHandle()

    server_script = os.path.normpath(_mllp_test_server_path)

    command = [
        _zato_python, server_script,
        '--host', '127.0.0.1',
        '--port', str(port),
        '--callback-mode', callback_mode,
        '--log-messages',
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    handle.process = process

    # .. capture stdout lines in a background thread ..
    stdout = process.stdout
    assert stdout is not None

    def _capture_output() -> 'None':
        for line in iter(stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            handle.received_lines.append(text)
            print(f'[{log_prefix}] {text}')

    capture_thread = threading.Thread(target=_capture_output, daemon=True)
    capture_thread.start()

    # .. wait for the READY signal ..
    deadline = time.monotonic() + _backend_ready_timeout

    while time.monotonic() < deadline:

        for line in handle.received_lines:
            if line.startswith('READY:'):
                yield handle

                # .. teardown ..
                if process.poll() is None:
                    process.terminate()
                    try:
                        _ = process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        _ = process.wait(timeout=5)
                return

        time.sleep(0.2)

    # .. the backend did not become ready in time.
    process.kill()
    raise Exception(f'MLLP backend did not produce READY signal within {_backend_ready_timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def mllp_backend(backend_port:'int') -> 'backend_gen':
    """ Starts the standalone mllp_test_server.py in echo mode and captures its stdout.
    """
    yield from _run_backend(backend_port, 'echo', 'BACKEND')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def reply_backend_port() -> 'int':
    """ Returns a free port for the backend that answers with an acknowledgment of its own.
    """
    out = _find_free_port()
    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def reply_backend(reply_backend_port:'int') -> 'backend_gen':
    """ Starts a second backend that answers with an acknowledgment naming itself, which is what
    shows a channel relaying the answer of the destination it replies from.
    """
    yield from _run_backend(reply_backend_port, 'reply', 'REPLY BACKEND')

# ################################################################################################################################
# ################################################################################################################################
