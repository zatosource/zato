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
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# local
from config import PubSubPushTestConfig, _active_endpoints
from receivers import ReceiverServer

# ################################################################################################################################
# ################################################################################################################################

_zato_base = '/home/dsuch/projects/zatosource-zato/4.1'
_zato_bin = os.path.join(_zato_base, 'code', 'bin', 'zato')

_template_path = os.path.join(os.path.dirname(__file__), 'enmasse_pubsub_push.yaml.template')

_server_process = None

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Bind to port 0 and return the OS-assigned port number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))

        out = sock.getsockname()[1]
        return out

# ################################################################################################################################
# ################################################################################################################################

def _make_tmpdir_name(purpose:'str') -> 'str':
    """ Build a descriptive temp directory name with local time and a random suffix.
    """
    now = datetime.now()
    timestamp = now.strftime('%Y_%m_%dT%H_%M_%S')
    random_suffix = os.urandom(3).hex()
    dir_name = f'zato_pubsub_test_{purpose}_{timestamp}_{random_suffix}'

    out = os.path.join(tempfile.gettempdir(), dir_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _render_enmasse_template(
    publisher_password:'str',
    puller_password:'str',
    subscriber_password:'str',
    port_map:'dict[str, int]',
    ) -> 'str':
    """ Read the static enmasse YAML template and replace all placeholders
    with the actual passwords and port numbers.
    """
    with open(_template_path, 'r') as template_file:
        content = template_file.read()

    # Replace password placeholders
    content = content.replace('{{publisher_password}}', publisher_password)
    content = content.replace('{{puller_password}}', puller_password)
    content = content.replace('{{subscriber_password}}', subscriber_password)

    # Replace port placeholders for each endpoint
    for topic_name, port in port_map.items():
        placeholder_key = topic_name.replace('.', '_')
        placeholder = '{{port_' + placeholder_key + '}}'
        content = content.replace(placeholder, str(port))

    out = content
    return out

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'str', port:'int', timeout:'int'=90) -> 'None':
    """ Poll the server's ping endpoint until it responds or the timeout expires.
    """
    from urllib.request import Request, urlopen

    url = f'http://{host}:{port}/zato/ping'
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=5) as response:
                if response.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.5)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def pubsub_push_server() -> 'Generator[None, None, None]': # type: ignore[misc]
    """ Start HTTP receivers and a Zato server for the pub/sub push test suite.
    """
    global _server_process

    # Kill any lingering Zato server processes from previous runs.
    # We use pkill here because at this point we have no PID to target -
    # these are orphans from previous test runs.
    _ = subprocess.run(['pkill', '-9', '-f', 'zato.server.main'], capture_output=True)
    time.sleep(1)

    # Generate random passwords for this test run
    publisher_password = 'test.pub.' + os.urandom(8).hex()
    puller_password    = 'test.pull.' + os.urandom(8).hex()
    subscriber_password = 'test.sub.' + os.urandom(8).hex()
    invoke_password    = 'test.invoke.' + os.urandom(8).hex()

    # Store passwords in config so tests can use them
    PubSubPushTestConfig.publisher_password = publisher_password
    PubSubPushTestConfig.puller_password    = puller_password
    PubSubPushTestConfig.subscriber_password = subscriber_password

    # Start an HTTP receiver for each active endpoint
    receiver_servers = []

    for topic_name in _active_endpoints:

        # Allocate a port and a named output directory
        port = _find_free_port()
        purpose = topic_name.replace('.', '_')
        output_directory = _make_tmpdir_name(purpose)
        os.makedirs(output_directory, exist_ok=True)

        # Record in config
        PubSubPushTestConfig.endpoint_ports[topic_name] = port
        PubSubPushTestConfig.endpoint_output_dirs[topic_name] = output_directory

        # Start the receiver
        receiver = ReceiverServer(port, output_directory)
        receiver.start()
        receiver_servers.append(receiver)

    # Build a port map for all 10 endpoints in the template.
    # Inactive endpoints get a dummy port that will never be connected to.
    all_topics = [
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

    port_map = {}

    for topic_name in all_topics:
        if topic_name in PubSubPushTestConfig.endpoint_ports:
            port_map[topic_name] = PubSubPushTestConfig.endpoint_ports[topic_name]
        else:
            port_map[topic_name] = 99999

    # Render the enmasse YAML template with actual values
    rendered_yaml = _render_enmasse_template(
        publisher_password,
        puller_password,
        subscriber_password,
        port_map,
    )

    # Write the rendered YAML to a temp file
    enmasse_directory = _make_tmpdir_name('enmasse')
    os.makedirs(enmasse_directory, exist_ok=True)
    enmasse_path = os.path.join(enmasse_directory, 'enmasse_pubsub_push.yaml')

    with open(enmasse_path, 'w') as enmasse_file:
        _ = enmasse_file.write(rendered_yaml)

    # Create the Zato quickstart environment
    server_directory = _make_tmpdir_name('server')

    quickstart_environment = os.environ.copy()
    _ = quickstart_environment.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', server_directory,
        '--force',
        '--password', invoke_password,
        '--servers', '1',
        '--server-api-client-for-scheduler-password', invoke_password,
        '--no-scheduler',
    ]

    result = subprocess.run(
        quickstart_command,
        capture_output=True,
        text=True,
        timeout=180,
        env=quickstart_environment,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'
        )

    server_path = os.path.join(server_directory, 'server1')

    # Import enmasse YAML into the ODB before starting the server.
    # The server is not running yet, so enmasse cannot notify it (rc=16),
    # but the ODB is updated correctly. On startup, the server reads
    # from ODB and picks up all the imported definitions.
    _ = subprocess.run(
        [_zato_bin, 'enmasse', server_path, '--import', '--input', enmasse_path],
        capture_output=True,
        text=True,
        timeout=60,
        env=quickstart_environment,
    )

    # Allocate dynamic ports for this test run
    server_port = _find_free_port()
    broker_port = _find_free_port()

    server_environment = os.environ.copy()
    server_environment['Zato_Config_Bind_Port'] = str(server_port)
    server_environment['Zato_Broker_HTTP_Port'] = str(broker_port)
    _ = server_environment.pop('COVERAGE_PROCESS_START', None)

    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_path, '--fg'],
        env=server_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    start_time = time.monotonic()
    server_output_lines:'list[str]' = []

    def _capture_server_output() -> 'None':
        for line in iter(_server_process.stdout.readline, b''): # type: ignore[union-attr]
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - start_time
            server_output_lines.append(f'[SERVER {elapsed:6.1f}s] {text}')

    stdout_thread = threading.Thread(target=_capture_server_output, daemon=True)
    stdout_thread.start()

    host = '127.0.0.1'

    try:
        _wait_for_server(host, server_port)
    except Exception:
        print('\n--- Server did not become ready, captured output: ---')

        for line in server_output_lines:
            print(line)

        print('--- End of server output ---\n')

        _server_process.terminate()
        _server_process.wait(timeout=10)
        raise

    # Update the config so tests use the dynamically allocated port
    PubSubPushTestConfig.base_url = f'http://{host}:{server_port}'

    yield

    # Teardown - terminate the server process we started
    if _server_process and _server_process.poll() is None:
        _server_process.terminate()
        _server_process.wait(timeout=10)

    # .. and shut down all HTTP receivers.
    for receiver in receiver_servers:
        receiver.shutdown()

# ################################################################################################################################
# ################################################################################################################################
