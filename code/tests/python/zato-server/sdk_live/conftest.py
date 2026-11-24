# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import logging
import os
import queue
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
from zato.common.test.pickup_listener import PickupListener
from zato.common.test.zato_database import create_test_database, drop_test_database

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# The GLPI mode of the target server
from _glpi_target import GLPIHandler, glpi_state

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.sdk_live.conftest')

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_suite_directory = os.path.dirname(__file__)

# The connector modules and the test services deployed at the server's boot.
_deployed_modules = [
    'crm_connector.py',
    'mainframe_connector.py',
    'payments_connector.py',
    'feed_connector.py',
    'audit_connector.py',
    'inventory_connector.py',
    'textproc_connector.py',
    'tunnel_connector.py',
    'glpi_connector.py',
]

_services_source_path = os.path.join(_suite_directory, '_services.py')

# Fixture files the process-based connectors use - a prebuilt jar, a module run in a clean interpreter and a CLI tool.
fixtures_directory = os.path.join(_suite_directory, 'fixtures')

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_ping_poll_interval   = 0.5

# How long the handshake gateway sleeps over a slow command, which is what lets concurrent
# service invocations overlap and prove that each of them borrowed a distinct pooled connection.
_slow_command_delay = 1.0

# How many connections each mode of the target server serves at a time. The worker threads that serve them start
# with the mode, so a connection that a test opens and that outlives it is served by a thread that existed before the test.
_target_workers_per_mode = 64

# What a worker of the target server receives instead of a connection when its mode stops.
_stop_worker = None

# ################################################################################################################################
# ################################################################################################################################

class EchoState:
    """ The failure switches of the echo mode - tests flip them to make the target stall
    without closing the socket or start rejecting an auth token.
    """
    def __init__(self) -> 'None':

        # When set, every reply goes out only after this many seconds ..
        self.stall_seconds = 0.0

        # .. unless the stall ends earlier, in which case a stalled request is abandoned,
        # .. because its caller has already timed out.
        self.stall_ended = threading.Event()

        # Requests carrying any of these keys are answered with a token-expired error.
        self.expired_keys = set()

        # What a renew-token request hands out.
        self.renewed_key = ''

# ################################################################################################################################

    def start_stall(self, stall_seconds:'float') -> 'None':
        """ Makes every reply go out only after the given number of seconds.
        """
        self.stall_ended.clear()
        self.stall_seconds = stall_seconds

# ################################################################################################################################

    def end_stall(self) -> 'None':
        """ Makes replies go out at once and releases the requests that are stalled.
        """
        self.stall_seconds = 0.0
        self.stall_ended.set()

echo_state = EchoState()

# ################################################################################################################################
# ################################################################################################################################

class _EchoHandler(socketserver.StreamRequestHandler):
    """ Answers each line it receives with the very same line - it stands in for the CRM gateway
    the example connector talks to. Failure switches make it stall or reject the auth token (7.2).
    """
    def handle(self) -> 'None':
        for line in self.rfile:
            text = line.decode('utf8').strip()

            # The stall switch keeps the reply from going out, without closing the socket.
            if echo_state.stall_seconds:
                is_ended = echo_state.stall_ended.wait(echo_state.stall_seconds)
                if is_ended:
                    return

            # Each request line starts with the caller's key.
            key, _, rest = text.partition(' ')

            # A token renewal always succeeds and hands out the key the test configured.
            if rest == 'renew-token':
                reply = f'token {echo_state.renewed_key}'

            # An expired key is rejected until the caller renews it.
            elif key in echo_state.expired_keys:
                reply = 'error token-expired'

            # The normal path echoes the line back whole.
            else:
                reply = text

            _ = self.wfile.write(f'{reply}\n'.encode('utf8'))
            self.wfile.flush()

# ################################################################################################################################
# ################################################################################################################################

class _EchoServer(socketserver.TCPServer):
    """ The TCP server every target mode runs on. Its connections are served by a fixed set of worker threads,
    and it tracks them so that killing the target severs them too, the way a real crash would.
    """
    allow_reuse_address = True

    def __init__(self, mode:'str', *args:'any_') -> 'None':
        super().__init__(*args)
        self.active_connections = []
        self.request_queue:'queue.Queue[any_]' = queue.Queue()
        self.workers:'list[threading.Thread]' = []

        for idx in range(_target_workers_per_mode):
            name = f'zato-sdk-live-target-{mode}-worker-{idx}'
            worker = threading.Thread(target=self._serve_requests, name=name, daemon=True)
            worker.start()
            self.workers.append(worker)

    def process_request(self, request:'any_', client_address:'any_') -> 'None':
        self.active_connections.append(request)
        self.request_queue.put((request, client_address))

    def _serve_requests(self) -> 'None':
        """ Serves one connection after another until the mode stops.
        """
        while True:
            item = self.request_queue.get()

            if item is _stop_worker:
                return

            request, client_address = item

            try:
                self.finish_request(request, client_address)
            except Exception:
                self.handle_error(request, client_address)
            finally:
                self.shutdown_request(request)

    def stop_workers(self) -> 'None':
        """ Makes each worker end once the connection it serves, if any, is closed.
        """
        for _ in self.workers:
            self.request_queue.put(_stop_worker)

    def kill_connections(self) -> 'None':
        """ Severs every connection this target ever accepted - closed ones are simply skipped.
        """
        for request in self.active_connections:
            try:
                request.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                request.close()
            except OSError:
                pass

        self.active_connections.clear()

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

class CorrelationState:
    """ What the correlation mode shares with tests - how many connections were ever made,
    which is how tests prove that concurrent requests multiplex over one socket.
    """
    def __init__(self) -> 'None':
        self.lock = threading.Lock()
        self.connection_count = 0

correlation_state = CorrelationState()

# ################################################################################################################################
# ################################################################################################################################

class _CorrelationHandler(socketserver.StreamRequestHandler):
    """ The correlation mode of the suite's target server - each request line is `corr_id payload`
    and the reply `corr_id echo payload` goes out from its own thread, so slow requests are answered
    after fast ones and replies arrive out of order (7.2).
    """
    def handle(self) -> 'None':

        with correlation_state.lock:
            correlation_state.connection_count += 1

        # Replies come from many threads, so writes are serialized per connection.
        write_lock = threading.Lock()

        for line in self.rfile:
            text = line.decode('utf8').strip()
            corr_id, _, payload = text.partition(' ')

            def _reply(corr_id:'str'=corr_id, payload:'str'=payload) -> 'None':

                # A slow request is answered late, letting fast ones overtake it.
                if payload.startswith('slow'):
                    time.sleep(_slow_command_delay)

                try:
                    with write_lock:
                        _ = self.wfile.write(f'{corr_id} echo {payload}\n'.encode('utf8'))
                        self.wfile.flush()
                except OSError:
                    # The connection is gone, so there is nowhere to reply to.
                    pass

            reply_thread = threading.Thread(target=_reply, daemon=True)
            reply_thread.start()

# ################################################################################################################################
# ################################################################################################################################

class PushState:
    """ What the push mode shares with tests - the subscriber sockets messages are pushed to
    and a counter of subscriptions, which is how tests prove that a reconnect resubscribed.
    """
    def __init__(self) -> 'None':
        self.lock = threading.Lock()
        self.subscribe_count = 0
        self.subscribers = []

# ################################################################################################################################

    def push(self, message:'str') -> 'None':
        """ Pushes one message to every subscriber, dropping the ones that are gone.
        """
        with self.lock:
            for subscriber in list(self.subscribers):
                try:
                    _ = subscriber.write(f'push {message}\n'.encode('utf8'))
                    subscriber.flush()
                except OSError:
                    self.subscribers.remove(subscriber)

push_state = PushState()

# ################################################################################################################################
# ################################################################################################################################

class _PushHandler(socketserver.StreamRequestHandler):
    """ The push mode of the suite's target server - clients subscribe and from then on
    the tests push messages to them through push_state, on the server's own initiative (7.2).
    """
    def handle(self) -> 'None':

        for line in self.rfile:
            text = line.decode('utf8').strip()

            # A subscription registers this connection as a push target.
            if text.startswith('subscribe'):
                with push_state.lock:
                    push_state.subscribe_count += 1
                    push_state.subscribers.append(self.wfile)
                _ = self.wfile.write(b'subscribed\n')
                self.wfile.flush()

            # Pings confirm the connection is alive between pushes.
            elif text == 'ping':
                _ = self.wfile.write(b'pong\n')
                self.wfile.flush()

        # The connection ended, so it stops being a push target.
        with push_state.lock:
            if self.wfile in push_state.subscribers:
                push_state.subscribers.remove(self.wfile)

# ################################################################################################################################
# ################################################################################################################################

class CountingState:
    """ What the counting mode shares with tests - every line the target ever received,
    which is how tests prove that buffered senders flushed everything (7.2).
    """
    def __init__(self) -> 'None':
        self.lock = threading.Lock()
        self.received = []

counting_state = CountingState()

# ################################################################################################################################
# ################################################################################################################################

class _CountingHandler(socketserver.StreamRequestHandler):
    """ The counting mode of the suite's target server - it never replies, it only records
    every line it receives.
    """
    def handle(self) -> 'None':
        for line in self.rfile:
            text = line.decode('utf8').strip()
            with counting_state.lock:
                counting_state.received.append(text)

# ################################################################################################################################
# ################################################################################################################################

class _SessionState:
    """ Holds all mutable session state.
    """

    def __init__(self) -> 'None':
        self.server_process:'subprocess.Popen[bytes] | None' = None
        self.quickstart_directory:'str | None' = None

        # The Zato_Database_* variables of the database of the environment, empty until the environment is created
        self.database_env:'strstrdict' = {}

        # The listener of the pickup directory, which is not running until the environment is complete
        self.pickup_listener:'PickupListener | None' = None

        # All the target servers the suite owns, one per mode, keyed by mode name.
        self.target_servers:'dict[str, _EchoServer]' = {}

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

        if self.pickup_listener:
            self.pickup_listener.stop()

        self.pickup_listener = None

        self.kill_server()

        for target_server in self.target_servers.values():
            target_server.shutdown()
            target_server.server_close()
            target_server.kill_connections()
            target_server.stop_workers()

        self.target_servers.clear()

        if self.quickstart_directory:
            shutil.rmtree(self.quickstart_directory, ignore_errors=True)

        self.quickstart_directory = None

        # The variables that selected the database are removed together with the database
        if self.database_env:
            for name in self.database_env:
                del os.environ[name]

            drop_test_database(self.database_env)
            self.database_env = {}

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

def _start_target_server(mode:'str', handler_class:'any_', port:'int'=0) -> 'int':
    """ Starts one mode of the suite's target server and returns its port. A port of 0 means
    any free port, a concrete port lets a mode restart in place after being killed.
    """
    target_server = _EchoServer(mode, ('127.0.0.1', port), handler_class)
    _state.target_servers[mode] = target_server

    # The name stays the same when a mode restarts, which is what tells the thread apart from one that a test leaves behind.
    target_thread = threading.Thread(target=target_server.serve_forever, name=f'zato-sdk-live-target-{mode}', daemon=True)
    target_thread.start()

    out = target_server.server_address[1]
    logger.info('Target server mode `%s` started on port %s', mode, out)
    return out

# ################################################################################################################################
# ################################################################################################################################

def kill_target_server(mode:'str') -> 'int':
    """ Kills one mode of the target server, dropping all its connections, and returns its port
    so that restart_target_server can bring it back in place.
    """
    target_server = _state.target_servers.pop(mode)
    out = target_server.server_address[1]

    target_server.shutdown()
    target_server.server_close()

    # A real crash severs live connections too, which is what reconnect tests rely on.
    target_server.kill_connections()
    target_server.stop_workers()

    logger.info('Target server mode `%s` killed on port %s', mode, out)
    return out

# ################################################################################################################################
# ################################################################################################################################

_mode_handlers = {
    'echo': _EchoHandler,
    'handshake': _HandshakeHandler,
    'correlation': _CorrelationHandler,
    'push': _PushHandler,
    'counting': _CountingHandler,
    'glpi': GLPIHandler,
}

def restart_target_server(mode:'str', port:'int') -> 'None':
    """ Starts a killed mode of the target server again on its original port.
    """
    _ = _start_target_server(mode, _mode_handlers[mode], port)

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

    # The name stays the same when the server restarts, which is what tells the thread apart from one that a test leaves behind.
    stdout_thread = threading.Thread(target=_stream_output, name='zato-sdk-live-server-output', daemon=True)
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

    # .. start the target servers the connectors will talk to, one per mode ..
    echo_port = _start_target_server('echo', _EchoHandler)
    handshake_port = _start_target_server('handshake', _HandshakeHandler)
    correlation_port = _start_target_server('correlation', _CorrelationHandler)
    push_port = _start_target_server('push', _PushHandler)
    counting_port = _start_target_server('counting', _CountingHandler)
    glpi_port = _start_target_server('glpi', GLPIHandler)

    # .. the environment receives a Zato database of its own, which persists across a restart of the server
    # and which the quickstart, the server and every enmasse command that this process runs use ..
    _state.database_env = create_test_database()
    os.environ.update(_state.database_env)

    # .. the cleanup at exit runs before the PostgreSQL server that holds the database is removed ..
    atexit.unregister(_state.cleanup)
    _ = atexit.register(_state.cleanup)

    # .. create a quickstart environment ..
    _state.quickstart_directory = tempfile.mkdtemp(prefix='zato_sdk_live_qs_')

    quickstart_env = os.environ.copy()
    _ = quickstart_env.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', _state.quickstart_directory,
        '--force',
        '--password', invoke_password,
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

    for module_name in _deployed_modules:
        _ = shutil.copy2(os.path.join(_suite_directory, module_name), os.path.join(pickup_directory, module_name))

    connector_deployed_path = os.path.join(pickup_directory, 'crm_connector.py')
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

    # .. start the server ..
    broker_port = _find_free_port()
    _start_server(server_directory, server_port, broker_port)

    # .. and the listener of the pickup directory, which runs for as long as the environment does.
    web_admin_repo_dir = os.path.join(_state.quickstart_directory, 'web-admin', 'config', 'repo')

    pickup_listener = PickupListener('sdk_live', server_directory, web_admin_repo_dir, server_port)
    _state.pickup_listener = pickup_listener
    pickup_listener.start()

    host = '127.0.0.1'
    base_url = f'http://{host}:{server_port}'

    logger.info('Total setup: %.1fs', time.monotonic() - start_time)

    # Note that the shared state objects and the helper functions below are passed through
    # this dict on purpose - pytest imports this conftest under a package-like module name,
    # so a plain `from conftest import x` in a test file would create a second module instance
    # with its own, disconnected copies of everything.
    yield {
        'host': host,
        'port': server_port,
        'invoke_password': invoke_password,
        'base_url': base_url,
        'echo_port': echo_port,
        'handshake_port': handshake_port,
        'correlation_port': correlation_port,
        'push_port': push_port,
        'counting_port': counting_port,
        'glpi_port': glpi_port,
        'server_directory': server_directory,
        'connector_deployed_path': connector_deployed_path,
        'pickup_listener': pickup_listener,
        'echo_state': echo_state,
        'correlation_state': correlation_state,
        'push_state': push_state,
        'counting_state': counting_state,
        'glpi_state': glpi_state,
        'kill_target_server': kill_target_server,
        'restart_target_server': restart_target_server,
        'restart_zato_server': restart_zato_server,
    }

    _state.cleanup()

# ################################################################################################################################
# ################################################################################################################################
