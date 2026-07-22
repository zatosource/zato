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
import signal
import socket
import socketserver
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

# PyPI
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.sdk_live.conftest')

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_connector_source_path = os.path.join(os.path.dirname(__file__), 'crm_connector.py')
_mainframe_source_path = os.path.join(os.path.dirname(__file__), 'mainframe_connector.py')
_services_source_path  = os.path.join(os.path.dirname(__file__), '_services.py')

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_ping_poll_interval   = 0.5

# How long the handshake gateway sleeps over a slow command, which is what lets concurrent
# service invocations overlap and prove that each of them borrowed a distinct pooled connection.
_slow_command_delay = 1.0

# ################################################################################################################################
# ################################################################################################################################

class _EchoHandler(socketserver.StreamRequestHandler):
    """ Answers each line it receives with the very same line - it stands in for the CRM gateway
    the example connector talks to.
    """
    def handle(self) -> 'None':
        for line in self.rfile:
            _ = self.wfile.write(line)
            self.wfile.flush()

# ################################################################################################################################
# ################################################################################################################################

class _EchoServer(socketserver.ThreadingTCPServer):
    """ A TCP server that echoes lines back to whoever connects.
    """
    allow_reuse_address = True
    daemon_threads = True

# ################################################################################################################################
# ################################################################################################################################

# Each logon gets the next session number, letting tests tell pooled connections apart.
_session_lock = threading.Lock()
_next_session_number = [1]

# ################################################################################################################################
# ################################################################################################################################

class _HandshakeHandler(socketserver.StreamRequestHandler):
    """ The handshake mode of the suite's target server - it stands in for a mainframe gateway.
    A client must log on first, gets a unique session ID back and each subsequent line is answered
    with the session ID prepended, which is how tests tell pooled connections apart.
    A line starting with 'slow' is answered only after a delay, keeping the connection busy.
    """
    def handle(self) -> 'None':

        # The very first line must be the logon ..
        first_line = self.rfile.readline().decode('utf8').strip()

        if not first_line.startswith('logon '):
            _ = self.wfile.write(b'error logon-required\n')
            return

        # .. each logon gets a unique session ..
        with _session_lock:
            session_id = f'session-{_next_session_number[0]}'
            _next_session_number[0] += 1

        _ = self.wfile.write(f'ok {session_id}\n'.encode('utf8'))
        self.wfile.flush()

        # .. and from now on, each line is answered with the session ID prepended.
        for line in self.rfile:
            text = line.decode('utf8').strip()

            # A slow command keeps the connection busy so concurrent callers need other connections
            if text.startswith('slow'):
                time.sleep(_slow_command_delay)

            _ = self.wfile.write(f'{session_id} {text}\n'.encode('utf8'))
            self.wfile.flush()

# ################################################################################################################################
# ################################################################################################################################

class _SessionState:
    """ Holds all mutable session state.
    """

    def __init__(self) -> 'None':
        self.server_process:'subprocess.Popen[bytes] | None' = None
        self.quickstart_directory:'str | None' = None
        self.echo_server:'_EchoServer | None' = None
        self.handshake_server:'_EchoServer | None' = None

# ################################################################################################################################

    def kill_server(self) -> 'None':
        """ Terminates the server's whole process group - the subprocess itself is a wrapper shell,
        so killing it alone would leave the actual server running and holding its port.
        """
        if self.server_process:
            if self.server_process.poll() is None:
                process_group = os.getpgid(self.server_process.pid)
                os.killpg(process_group, signal.SIGKILL)
                _ = self.server_process.wait(timeout=_process_kill_timeout)
                logger.info('Killed server process group')

        self.server_process = None

        # A safety net in case any process serving this suite's own environment survived -
        # the match is scoped to our private temp directory.
        if self.quickstart_directory:
            _ = subprocess.run(['pkill', '-f', f'zato.server.main {self.quickstart_directory}'], capture_output=True)
            time.sleep(1)

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Full teardown.
        """
        if self.quickstart_directory:
            server_log_path = os.path.join(self.quickstart_directory, 'server1', 'logs', 'server.log')
            if os.path.exists(server_log_path):
                _ = shutil.copy(server_log_path, '/tmp/server-logs-sdk-live.txt')

        self.kill_server()

        if self.echo_server:
            self.echo_server.shutdown()
            self.echo_server.server_close()
            self.echo_server = None

        if self.handshake_server:
            self.handshake_server.shutdown()
            self.handshake_server.server_close()
            self.handshake_server = None

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

def _start_echo_server() -> 'int':
    """ Starts the echo server that stands in for the CRM gateway and returns its port.
    """
    echo_server = _EchoServer(('127.0.0.1', 0), _EchoHandler)
    _state.echo_server = echo_server

    echo_thread = threading.Thread(target=echo_server.serve_forever, daemon=True)
    echo_thread.start()

    out = echo_server.server_address[1]
    logger.info('Echo server started on port %s', out)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _start_handshake_server() -> 'int':
    """ Starts the handshake server that stands in for the mainframe gateway and returns its port.
    """
    handshake_server = _EchoServer(('127.0.0.1', 0), _HandshakeHandler)
    _state.handshake_server = handshake_server

    handshake_thread = threading.Thread(target=handshake_server.serve_forever, daemon=True)
    handshake_thread.start()

    out = handshake_server.server_address[1]
    logger.info('Handshake server started on port %s', out)
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

def _start_server(server_directory:'str', server_port:'int', broker_port:'int') -> 'None':
    """ Starts the Zato server and waits for it to be ready.
    """
    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(server_port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    _ = server_env.pop('COVERAGE_PROCESS_START', None)

    # The server runs in its own process group so that teardown can terminate the whole tree.
    _state.server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
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

# ################################################################################################################################
# ################################################################################################################################

def restart_zato_server(zato_server:'any_') -> 'None':
    """ Stops the running server and starts it again on the same port, e.g. for tests
    that assert on what happens with stored definitions across a restart.
    """
    _state.kill_server()

    broker_port = _find_free_port()
    _start_server(zato_server['server_directory'], zato_server['port'], broker_port)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'any_':
    """ Session-scoped fixture that starts an echo server standing in for the CRM gateway
    plus a Zato server with the example connector and a test service deployed at boot.
    """
    start_time = time.monotonic()

    # Generate the credentials used by the invoke API ..
    invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

    # .. start the target servers the connectors will talk to ..
    echo_port = _start_echo_server()
    handshake_port = _start_handshake_server()

    # .. create a quickstart environment ..
    _state.quickstart_directory = tempfile.mkdtemp(prefix='zato_sdk_live_qs_')

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

    # .. drop the connector module and the test service into the pickup directory
    # .. so the boot scan deploys them ..
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    connector_deployed_path = os.path.join(pickup_directory, 'crm_connector.py')
    _ = shutil.copy2(_connector_source_path, connector_deployed_path)
    _ = shutil.copy2(_mainframe_source_path, os.path.join(pickup_directory, 'mainframe_connector.py'))
    _ = shutil.copy2(_services_source_path, os.path.join(pickup_directory, 'crm_test_services.py'))

    # .. patch server.conf so the server binds to a dynamically allocated port ..
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

    # .. and start the server.
    broker_port = _find_free_port()
    _start_server(server_directory, server_port, broker_port)

    host = '127.0.0.1'
    base_url = f'http://{host}:{server_port}'

    logger.info('Total setup: %.1fs', time.monotonic() - start_time)

    yield {
        'host': host,
        'port': server_port,
        'invoke_password': invoke_password,
        'base_url': base_url,
        'echo_port': echo_port,
        'handshake_port': handshake_port,
        'server_directory': server_directory,
        'connector_deployed_path': connector_deployed_path,
    }

    _state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
