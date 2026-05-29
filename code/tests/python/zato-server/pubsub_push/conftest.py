# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import logging
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

sys.path.insert(0, os.path.dirname(__file__))

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from _receiver import WebhookReceiver
    from config import endpoint_config_dict as endpoint_config_dict
    from zato.common.typing_ import any_, anydict, strstrdict

# ################################################################################################################################
# ################################################################################################################################

webhook_receiver_list = list['WebhookReceiver']
str_strint_dict       = dict[str, 'str | int']

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.pubsub_push.conftest')

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

_template_path = os.path.join(os.path.dirname(__file__), '_enmasse_template.yaml')

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_ping_poll_interval   = 0.5

# ################################################################################################################################
# ################################################################################################################################

_topic_names = [
    'iam.user.created',
    'iam.user.deleted',
    'iam.role.assigned',
    'iam.password.changed',
    'iam.login.failed',
    'customer.registered',
    'customer.updated',
    'customer.deactivated',
    'order.placed',
    'order.shipped',
]

# ################################################################################################################################
# ################################################################################################################################

class _SessionState:
    """ Holds all mutable session state so there are no module-level global variables.
    """

    def __init__(self) -> 'None':
        self.server_process:'subprocess.Popen[bytes] | None' = None
        self.quickstart_directory:'str | None' = None
        self.test_data_directory:'str | None' = None
        self.receivers:'webhook_receiver_list' = []

# ################################################################################################################################

    def kill_server(self) -> 'None':
        """ Terminates the server subprocess if it is still running.
        """
        if self.server_process:
            if self.server_process.poll() is None:
                self.server_process.kill()
                _ = self.server_process.wait(timeout=_process_kill_timeout)
                logger.info('Killed server process')

        self.server_process = None

        # .. also kill any orphaned Zato server processes that may have forked ..
        _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)

# ################################################################################################################################

    def stop_all_receivers(self) -> 'None':
        """ Stops every running receiver.
        """
        for receiver in self.receivers:
            receiver.stop()

        receiver_count = len(self.receivers)
        self.receivers.clear()
        logger.info('Stopped %d receiver(s)', receiver_count)

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Full teardown - server, receivers, temp directory.
        """
        # Copy server logs before killing anything ..
        if self.quickstart_directory:
            server_log_path = os.path.join(self.quickstart_directory, 'server1', 'logs', 'server.log')
            if os.path.exists(server_log_path):
                shutil.copy(server_log_path, '/tmp/server-logs.txt')
                logger.info('Copied server logs to /tmp/server-logs.txt')

        # Stop the server process ..
        self.kill_server()

        # .. then stop all receivers ..
        self.stop_all_receivers()

        # .. then clean up the temporary directories.
        if self.quickstart_directory:
            shutil.rmtree(self.quickstart_directory, ignore_errors=True)
            logger.info('Removed quickstart directory %s', self.quickstart_directory)

        if self.test_data_directory:
            shutil.rmtree(self.test_data_directory, ignore_errors=True)
            logger.info('Removed test data directory %s', self.test_data_directory)

        self.quickstart_directory = None
        self.test_data_directory = None

# ################################################################################################################################
# ################################################################################################################################

_state = _SessionState()
_ = atexit.register(_state.cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _topic_to_key(topic_name:'str') -> 'str':
    """ Converts a topic name like 'iam.user.created' to a placeholder key like 'iam_user_created'.
    """
    out = topic_name.replace('.', '_')
    return out

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Returns a free TCP port on localhost.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        socket_name = tcp_socket.getsockname()

        out = socket_name[1]
        return out

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'str', port:'int', timeout:'int'=_server_wait_timeout) -> 'None':
    """ Polls the server's /zato/ping endpoint until it returns 200 or the timeout expires.
    """

    ping_url = f'http://{host}:{port}/zato/ping'
    start_time = time.monotonic()
    deadline = start_time + timeout
    attempt_number = 0

    while time.monotonic() < deadline:

        attempt_number += 1
        current_time = time.monotonic()
        elapsed = current_time - start_time

        try:
            request = Request(ping_url, method='GET')

            with urlopen(request, timeout=_process_kill_timeout) as response:
                if response.status == OK:
                    logger.info('Ping OK after %.1fs (attempt %d)', elapsed, attempt_number)
                    return

        except (ConnectionRefusedError, OSError, URLError):
            logger.debug('Ping attempt %d at %.1fs: not ready', attempt_number, elapsed)

        time.sleep(_ping_poll_interval)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _render_template(placeholders:'anydict') -> 'str':
    """ Reads the enmasse YAML template and replaces all {{placeholder}} tokens.
    """
    with open(_template_path, 'r') as template_file:
        out = template_file.read()

    for key, value in placeholders.items():
        token = '{{' + key + '}}'
        string_value = str(value)
        out = out.replace(token, string_value)

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'any_':
    """ Session-scoped fixture that spins up a Zato quickstart environment,
    imports the enmasse YAML, starts per-topic receivers, starts the server,
    and yields connection details for the pub/sub push tests.
    """

    from _receiver import WebhookReceiver
    from config import EndpointConfig, TestConfig

    # Kill any leftover Zato servers from interrupted previous runs ..
    _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
    time.sleep(2)

    start_time = time.monotonic()

    # Generate random passwords ..
    random_bytes = os.urandom(8)
    random_suffix = random_bytes.hex()
    publisher_password = 'test.pub.' + random_suffix

    random_bytes = os.urandom(8)
    random_suffix = random_bytes.hex()
    puller_password = 'test.pull.' + random_suffix

    random_bytes = os.urandom(8)
    random_suffix = random_bytes.hex()
    invoke_password = 'test.invoke.' + random_suffix

    subscriber_passwords:'strstrdict' = {}

    for topic_name in _topic_names:
        key = _topic_to_key(topic_name)
        random_bytes = os.urandom(8)
        random_suffix = random_bytes.hex()
        subscriber_passwords[key] = 'test.sub.' + random_suffix

    # Allocate ports and start receivers ..
    _state.quickstart_directory = tempfile.mkdtemp(prefix='zato_pubsub_push_qs_')
    _state.test_data_directory = tempfile.mkdtemp(prefix='zato_pubsub_push_data_')
    endpoints:'endpoint_config_dict' = {}
    placeholders:'str_strint_dict' = {}

    placeholders['publisher_password'] = publisher_password
    placeholders['puller_password'] = puller_password

    for topic_name in _topic_names:
        key = _topic_to_key(topic_name)

        # .. password placeholder ..
        placeholders[f'sub_{key}_password'] = subscriber_passwords[key]

        # .. port placeholder ..
        port = _find_free_port()
        placeholders[f'port_{key}'] = port

        # .. output directory ..
        output_directory = os.path.join(_state.test_data_directory, 'receivers', key)
        os.makedirs(output_directory, exist_ok=True)

        # .. start the receiver ..
        receiver = WebhookReceiver(port, output_directory)
        receiver.start()
        _state.receivers.append(receiver)

        endpoint_config = EndpointConfig(
            port=port,
            output_directory=output_directory,
            receiver=receiver,
        )
        endpoints[topic_name] = endpoint_config

    receiver_time = time.monotonic()
    receiver_elapsed = receiver_time - start_time
    logger.info('Receivers started: %.1fs', receiver_elapsed)

    # Render the enmasse template ..
    rendered_yaml = _render_template(placeholders)
    rendered_path = os.path.join(_state.test_data_directory, 'enmasse.yaml')

    with open(rendered_path, 'w') as rendered_file:
        _ = rendered_file.write(rendered_yaml)

    # Create a quickstart environment ..
    quickstart_environment = os.environ.copy()
    _ = quickstart_environment.pop('COVERAGE_PROCESS_START', None)

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
        timeout=_quickstart_timeout, env=quickstart_environment)

    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    quickstart_time = time.monotonic()
    quickstart_elapsed = quickstart_time - receiver_time
    logger.info('Quickstart create: %.1fs', quickstart_elapsed)

    server_directory = os.path.join(_state.quickstart_directory, 'server1')

    # Import the enmasse YAML into the ODB before starting the server ..
    enmasse_environment = os.environ.copy()
    enmasse_environment['Zato_Needs_Config_Reload'] = 'False'

    enmasse_command = [
        _zato_bin, 'enmasse', '--import', '--input', rendered_path, server_directory,
    ]

    enmasse_result = subprocess.run(
        enmasse_command, capture_output=True, text=True, check=False,
        timeout=_quickstart_timeout, env=enmasse_environment)

    if enmasse_result.returncode != 0:
        raise RuntimeError(f'enmasse import failed:\nstdout: {enmasse_result.stdout}\nstderr: {enmasse_result.stderr}')

    enmasse_time = time.monotonic()
    enmasse_elapsed = enmasse_time - quickstart_time
    logger.info('Enmasse import: %.1fs', enmasse_elapsed)

    # Start the server in foreground mode ..
    server_port = _find_free_port()
    broker_port = _find_free_port()

    server_environment = os.environ.copy()
    server_environment['Zato_Config_Bind_Port'] = str(server_port)
    server_environment['Zato_Broker_HTTP_Port'] = str(broker_port)
    _ = server_environment.pop('COVERAGE_PROCESS_START', None)

    _state.server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    popen_time = time.monotonic()
    popen_elapsed = popen_time - enmasse_time
    logger.info('Popen started: %.1fs', popen_elapsed)

    # .. stream server stdout in a background thread ..
    def _stream_server_output() -> 'None':
        stdout = _state.server_process.stdout # type: ignore[union-attr]
        readline = stdout.readline # pyright: ignore[reportOptionalMemberAccess]

        for line in iter(readline, b''):
            decoded = line.decode('utf-8', errors='replace')
            text = decoded.rstrip()
            current_time = time.monotonic()
            elapsed = current_time - popen_time
            logger.debug('[SERVER %6.1fs] %s', elapsed, text)

    stdout_thread = threading.Thread(target=_stream_server_output, daemon=True)
    stdout_thread.start()

    # .. wait for the server to come up ..
    host = '127.0.0.1'

    try:
        _wait_for_server(host, server_port)
        ready_time = time.monotonic()
        ready_elapsed = ready_time - popen_time
        logger.info('Server ready: %.1fs', ready_elapsed)

    except (ConnectionRefusedError, OSError, RuntimeError):
        logger.error('Server did not become ready')
        _state.kill_server()
        raise

    setup_time = time.monotonic()
    total_elapsed = setup_time - start_time
    logger.info('Total setup: %.1fs', total_elapsed)

    # .. populate TestConfig ..
    TestConfig.base_url             = f'http://{host}:{server_port}'
    TestConfig.password             = invoke_password
    TestConfig.publisher_username   = 'test.pubsub.publisher'
    TestConfig.publisher_password   = publisher_password
    TestConfig.puller_username      = 'test.pubsub.puller'
    TestConfig.puller_password      = puller_password
    TestConfig.server_directory     = server_directory
    TestConfig.endpoints            = endpoints

    yield

    _state.cleanup()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clear_all_outputs() -> 'any_':
    """ Clears all delivered message files from every receiver's output directory before each test.
    """
    from config import TestConfig

    for endpoint_config in TestConfig.endpoints.values():
        endpoint_config.receiver.clear_output()

    yield

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def reset_receivers() -> 'any_':
    """ Resets all receivers to accept mode before the test, then clears output.
    """
    from config import TestConfig

    for endpoint_config in TestConfig.endpoints.values():
        endpoint_config.receiver.behavior.reset()
        endpoint_config.receiver.clear_output()

    yield

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def drain_pull_queue() -> 'any_':
    """ Drains the pull queue so the test starts with zero pending messages.
    """
    from zato.common.test.client import PullClient
    from config import TestConfig

    client = PullClient(TestConfig.base_url, TestConfig.puller_username, TestConfig.puller_password)
    client.drain()

    yield

# ################################################################################################################################
# ################################################################################################################################
