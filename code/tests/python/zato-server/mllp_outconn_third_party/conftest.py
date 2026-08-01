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
from collections.abc import Generator
from http.client import OK
from urllib.request import Request, urlopen

# The suite's own modules come first, then the shared HL7 clients and listeners, and last the
# language suite, which is only here for the certificate material it already knows how to make.
# Every module of this suite is named apart from every module of that one, so nothing is shadowed
# whichever of the two a run collects first.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mllp_languages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib'))
sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.client import AdminClient
from zato.common.test.process_util import kill_process_tree
from zato.common.typing_ import cast_
from zato.common.util.config import get_config_object, update_config_file

# Zato - the certificate material, made the same way the language suite makes it
from _certs import generate_certificates, TestCertificates

# Zato - the suite's own parts
from _outconn_receivers import build_receiver, Receiver_Hapi, Receiver_Hl7apy, Receiver_Names
from _outconn_services import Service_File_Name, service_source

# Zato - the Java toolchain check, so a machine without one skips rather than fails
from hl7_client.java_build import is_java_available

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_zato_base_dir = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin      = os.path.join(_zato_base_dir, 'code', 'bin', 'zato')
_zato_python   = os.path.join(_zato_base_dir, 'code', 'bin', 'python')

# The file-transfer listener that watches the pickup directory, which is what deploys a service
# written after the server has already started
_listener_path = os.path.join(
    _zato_base_dir, 'code', 'zato-common', 'src', 'zato', 'common', 'file_transfer', 'listener.py')

# Setting this variable makes a missing toolchain a failure rather than a skip, which is what a run
# meant to cover the third-party receiving stacks sets so that a machine without one is not passed
# over silently.
Env_Third_Party_Required = 'Zato_Test_HL7_Outconn_Third_Party'

_password = 'test.mllp.outconn.' + CryptoManager.generate_hex_string()

_server_ready_timeout    = 60
_hot_deploy_timeout      = 30
_listener_settle_seconds = 2
_quickstart_timeout      = 120

# What one run leaves behind for the teardown to end, kept at module level because the atexit
# handler runs where no fixture is in scope any more
_server_process:'any_'   = None
_listener_process:'any_' = None
_temp_directory:'str'    = ''

# Every path the listener reported as deployed, filled by the thread draining its output
_listener_deployed_paths:'set[str]' = set()
_listener_deployed_condition = threading.Condition()

# ################################################################################################################################
# ################################################################################################################################

class OutconnEnvironment:
    """ Everything a test needs to know about the environment it operates on.
    """

    def __init__(self, client:'AdminClient', certificates:'TestCertificates', server_directory:'str') -> 'None':

        # How a test sends through the connections it created
        self.client = client

        # What a test of a connection over TLS points either end at
        self.certificates = certificates

        # Where the connections a test needs are imported into
        self.server_directory = server_directory

# ################################################################################################################################
# ################################################################################################################################

environment_gen = Generator['OutconnEnvironment', None, None]
receiver_gen    = Generator['any_', None, None]

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Asks the operating system for a port nothing is listening on.
    """
    temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temporary_socket.bind(('127.0.0.1', 0))

    _, port = temporary_socket.getsockname()
    temporary_socket.close()

    out = port
    return out

# ################################################################################################################################

def _kill_everything() -> 'None':
    """ Ends every process one run started, in the reverse of the order they were started in.
    """
    global _server_process, _listener_process

    # The listener goes before the server so that it does not race the server's shutdown
    kill_process_tree(_listener_process)
    _listener_process = None

    kill_process_tree(_server_process)
    _server_process = None

# ################################################################################################################################

def _cleanup() -> 'None':
    """ Ends everything and removes what one run wrote, whether it ended well or not.
    """
    global _temp_directory

    _kill_everything()

    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = ''

_ = atexit.register(_cleanup)

# ################################################################################################################################

def _wait_for_server(host:'str', port:'int') -> 'None':
    """ Polls the server's ping endpoint until it answers.
    """
    url = f'http://{host}:{port}/zato/ping'
    deadline = time.monotonic() + _server_ready_timeout

    while time.monotonic() < deadline:

        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=5) as response:
                if response.status == OK:
                    return
        except Exception:

            # A server that is still starting refuses the connection, which is not yet a failure
            pass

        time.sleep(0.5)

    raise Exception(f'The server at {host}:{port} did not answer within {_server_ready_timeout}s')

# ################################################################################################################################

def _create_quickstart(directory:'str') -> 'str':
    """ Creates the throwaway environment one run operates on and returns its server directory.
    """

    # The environment has to be laid down into a directory of its own, because quickstart refuses
    # to write into one that already holds anything
    os.makedirs(directory)

    command = [
        _zato_bin, 'quickstart', 'create', directory,
        '--servers', '1',
        '--password', _password,
        '--server-api-client-for-scheduler-password', _password,
        '--no-scheduler',
    ]

    # Coverage tracking of a subprocess would write into the run's own data file, which nothing reads
    environment = os.environ.copy()
    _ = environment.pop('COVERAGE_PROCESS_START', None)

    result = subprocess.run(command, capture_output=True, text=True, timeout=_quickstart_timeout, env=environment)

    if result.returncode != 0:
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    out = os.path.join(directory, 'server1')
    return out

# ################################################################################################################################

def _set_server_port(server_directory:'str', port:'int') -> 'None':
    """ Points the server at a port nothing else on this machine is listening on. The bind address
    is set along with it because the check that runs before the server starts reads that one.
    """
    repository_location = os.path.join(server_directory, 'config', 'repo')

    config = get_config_object(repository_location, 'server.conf')
    config = cast_('any_', config)

    main_config = config['main']
    main_config['port'] = str(port)
    main_config['bind'] = f'127.0.0.1:{port}'

    update_config_file(config, repository_location, 'server.conf')

# ################################################################################################################################

def _stream_output(process:'any_', label:'str') -> 'None':
    """ Drains what a process writes so a full pipe never blocks it, and puts every line where a
    failing run can be read back from.
    """
    for line in iter(process.stdout.readline, b''):
        text = line.decode('utf8', errors='replace').rstrip()
        print(f'[{label}] {text}')

        # The listener prints this once the server confirmed a file, which is what the deploy waits on
        if 'Deployed -> ' in text:
            deployed_path = text.split('Deployed -> ')[1]
            with _listener_deployed_condition:
                _listener_deployed_paths.add(deployed_path)
                _listener_deployed_condition.notify_all()

# ################################################################################################################################

def _start_server(server_directory:'str', port:'int') -> 'None':
    """ Starts the server in the foreground. Nothing here needs the server's own MLLP listener, the
    whole of what is under test being the outgoing side, so its port is only settled on because the
    server would otherwise pick one this machine may already be using.
    """
    global _server_process

    environment = os.environ.copy()
    environment['Zato_Config_Bind_Port'] = str(port)
    environment['Zato_Broker_HTTP_Port'] = str(_find_free_port())
    environment['Zato_HL7_MLLP_Port'] = str(_find_free_port())
    _ = environment.pop('COVERAGE_PROCESS_START', None)

    # A new session makes the launcher its own process group leader, so the teardown can end the
    # whole group - the shell wrapper and the server it launched included
    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    # A detached watchdog ends the group once this process is gone - a pytest run killed outright
    # never reaches the cleanup, and a server nothing is left to stop would go on running and logging
    watchdog_script = (
        f'while kill -0 {os.getpid()} 2>/dev/null; do sleep 5; done; '
        f'kill -- -{_server_process.pid} 2>/dev/null'
    )
    _ = subprocess.Popen(['/bin/sh', '-c', watchdog_script], start_new_session=True)

    output_thread = threading.Thread(target=_stream_output, args=(_server_process, 'SERVER'), daemon=True)
    output_thread.start()

# ################################################################################################################################

def _start_listener(server_directory:'str', port:'int', environment_directory:'str') -> 'str':
    """ Starts the file-transfer listener on the pickup directory and returns that directory. The
    server's own scan only covers what was there when it started, so a service written now needs it.
    """
    global _listener_process

    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    os.makedirs(pickup_directory, exist_ok=True)

    environment = os.environ.copy()
    environment['Zato_Config_Bind_Port'] = str(port)
    environment['Zato_Web_Admin_Repo_Dir'] = os.path.join(environment_directory, 'web-admin', 'config', 'repo')
    _ = environment.pop('COVERAGE_PROCESS_START', None)

    _listener_process = subprocess.Popen(
        [_zato_python, _listener_path, pickup_directory],
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    output_thread = threading.Thread(target=_stream_output, args=(_listener_process, 'LISTENER'), daemon=True)
    output_thread.start()

    # The listener needs a moment to set its directory watch up before a file written lands in it
    time.sleep(_listener_settle_seconds)

    out = pickup_directory
    return out

# ################################################################################################################################

def _deploy_service(pickup_directory:'str') -> 'None':
    """ Writes the service every test sends through and waits for the server to confirm it.
    """
    file_path = os.path.join(pickup_directory, Service_File_Name)

    with open(file_path, 'w') as file_handle:
        _ = file_handle.write(service_source)

    def _is_deployed() -> 'bool':
        out = file_path in _listener_deployed_paths
        return out

    with _listener_deployed_condition:
        is_deployed = _listener_deployed_condition.wait_for(_is_deployed, timeout=_hot_deploy_timeout)

    if not is_deployed:
        raise Exception(f'The listener did not deploy {file_path} within {_hot_deploy_timeout}s')

    print(f'[DEPLOY] Deployed {file_path}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def outconn_environment() -> 'environment_gen':
    """ Brings up everything one run of this suite operates on - a throwaway Zato environment, the
    service every test sends through, and the certificate material a test over TLS points both ends at.
    """
    global _temp_directory

    _temp_directory = tempfile.mkdtemp(prefix='zato_mllp_outconn_third_party_')

    certificates = generate_certificates(os.path.join(_temp_directory, 'certs'))

    environment_directory = os.path.join(_temp_directory, 'env')
    server_directory = _create_quickstart(environment_directory)

    server_port = _find_free_port()
    _set_server_port(server_directory, server_port)

    _start_server(server_directory, server_port)
    _wait_for_server('127.0.0.1', server_port)

    pickup_directory = _start_listener(server_directory, server_port, environment_directory)
    _deploy_service(pickup_directory)

    client = AdminClient(f'http://127.0.0.1:{server_port}', _password)

    yield OutconnEnvironment(client, certificates, server_directory)

    _cleanup()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(params=Receiver_Names)
def receiver(request:'any_') -> 'receiver_gen':
    """ One third-party receiving stack, a test using it being run once against each of them. Both
    of them acknowledge everything they are sent, which is the everyday case - a test that needs a
    listener to behave otherwise builds one of its own.
    """
    name = request.param

    _require_toolchain(name)

    out = build_receiver(name)
    out.start()

    yield out

    out.stop()

# ################################################################################################################################

@pytest.fixture
def hl7apy_receiver() -> 'receiver_gen':
    """ The hl7apy receiving stack on its own, for a test that only one of the two can be put
    through - one over mutual TLS, say, which is the Python listener's to terminate.
    """
    out = build_receiver(Receiver_Hl7apy)
    out.start()

    yield out

    out.stop()

# ################################################################################################################################

def _require_toolchain(name:'str') -> 'None':
    """ Skips a test whose receiving stack this machine cannot run, unless the run was asked for
    outright, in which case a silent skip would be the whole point of the run going missing.
    """
    if name != Receiver_Hapi:
        return

    if is_java_available():
        return

    message = 'No JDK on this machine, so HAPI can be neither built nor run'

    if os.environ.get(Env_Third_Party_Required) == '1':
        raise Exception(message)

    pytest.skip(message)

# ################################################################################################################################

def require_toolchain(name:'str') -> 'None':
    """ The same check, for a test that builds a listener of its own rather than taking the fixture.
    """
    _require_toolchain(name)

# ################################################################################################################################
# ################################################################################################################################
