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
import socket
import subprocess
import tempfile
import threading
import time
from http.client import OK
from urllib.error import URLError
from urllib.request import Request, urlopen

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callable_, strstrdict

# ################################################################################################################################
# ################################################################################################################################

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_ping_poll_interval   = 0.5

# ################################################################################################################################
# ################################################################################################################################

class SessionState:
    """ Holds all mutable session state so there are no module-level global variables.
    """

    def __init__(self, logger_name:'str', server_log_copy_name:'str') -> 'None':
        self.server_process:'subprocess.Popen[bytes] | None' = None
        self.quickstart_directory:'str | None' = None
        self.test_data_directory:'str | None' = None
        self.receivers:'list' = []
        self._logger = logging.getLogger(logger_name)
        self._server_log_copy_name = server_log_copy_name

# ################################################################################################################################

    def kill_server(self) -> 'None':
        """ Terminates the server subprocess if it is still running.
        """
        if self.server_process:
            if self.server_process.poll() is None:
                self.server_process.kill()
                _ = self.server_process.wait(timeout=_process_kill_timeout)
                self._logger.info('Killed server process')

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
        self._logger.info('Stopped %d receiver(s)', receiver_count)

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Full teardown - server, receivers, temp directory.
        """
        # Copy server logs before killing anything ..
        if self.quickstart_directory:
            server_log_path = os.path.join(self.quickstart_directory, 'server1', 'logs', 'server.log')
            if os.path.exists(server_log_path):
                destination = f'/tmp/{self._server_log_copy_name}'
                shutil.copy(server_log_path, destination)
                self._logger.info('Copied server logs to %s', destination)

        # Stop the server process ..
        self.kill_server()

        # .. then stop all receivers ..
        self.stop_all_receivers()

        # .. then clean up the temporary directories.
        if self.quickstart_directory:
            shutil.rmtree(self.quickstart_directory, ignore_errors=True)
            self._logger.info('Removed quickstart directory %s', self.quickstart_directory)

        if self.test_data_directory:
            shutil.rmtree(self.test_data_directory, ignore_errors=True)
            self._logger.info('Removed test data directory %s', self.test_data_directory)

        self.quickstart_directory = None
        self.test_data_directory = None

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':
    """ Returns a free TCP port on localhost.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        socket_name = tcp_socket.getsockname()

        out = socket_name[1]
        return out

# ################################################################################################################################
# ################################################################################################################################

def wait_for_server(logger:'logging.Logger', host:'str', port:'int', timeout:'int'=_server_wait_timeout) -> 'None':
    """ Polls the server's /zato/ping endpoint until it returns 200 or the timeout expires.
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

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def render_template(template_path:'str', placeholders:'anydict') -> 'str':
    """ Reads the enmasse YAML template and replaces all {{placeholder}} tokens.
    """
    with open(template_path, 'r') as template_file:
        out = template_file.read()

    for key, value in placeholders.items():
        token = '{{' + key + '}}'
        string_value = str(value)
        out = out.replace(token, string_value)

    return out

# ################################################################################################################################
# ################################################################################################################################

def start_server_process(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    server_directory:'str',
    server_port:'int',
    broker_port:'int',
    extra_server_env:'strstrdict',
    patch_server_conf_bind:'bool',
) -> 'float':
    """ Starts the Zato server process, streams stdout, and waits for it to be ready.
    Returns the popen timestamp.
    """
    server_environment = os.environ.copy()
    server_environment['Zato_Config_Bind_Port'] = str(server_port)
    server_environment['Zato_Broker_HTTP_Port'] = str(broker_port)
    _ = server_environment.pop('COVERAGE_PROCESS_START', None)

    # .. apply any extra env vars ..
    for env_key, env_value in extra_server_env.items():
        server_environment[env_key] = env_value

    # .. patch server.conf if needed so that CLI commands use the dynamic port ..
    if patch_server_conf_bind:
        server_conf_path = os.path.join(server_directory, 'config', 'repo', 'server.conf')

        with open(server_conf_path, 'r') as server_conf_file:
            server_conf_content = server_conf_file.read()

        server_conf_content = re.sub(
            r'^(bind\s*=\s*)\S+',
            f'\\g<1>0.0.0.0:{server_port}',
            server_conf_content,
            flags=re.MULTILINE,
        )

        with open(server_conf_path, 'w') as server_conf_file:
            _ = server_conf_file.write(server_conf_content)

    state.server_process = subprocess.Popen(
        [zato_bin, 'start', server_directory, '--fg'],
        env=server_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    popen_time = time.monotonic()

    # .. stream server stdout in a background thread ..
    def _stream_server_output() -> 'None':
        stdout = state.server_process.stdout # type: ignore[union-attr]
        readline = stdout.readline # pyright: ignore[reportOptionalMemberAccess]

        for line in iter(readline, b''):
            decoded = line.decode('utf-8', errors='replace')
            text = decoded.rstrip()
            elapsed = time.monotonic() - popen_time
            logger.debug('[SERVER %6.1fs] %s', elapsed, text)

    stdout_thread = threading.Thread(target=_stream_server_output, daemon=True)
    stdout_thread.start()

    # .. wait for the server to come up ..
    host = '127.0.0.1'

    try:
        wait_for_server(logger, host, server_port)
        logger.info('Server ready: %.1fs', time.monotonic() - popen_time)

    except (ConnectionRefusedError, OSError, RuntimeError):
        logger.error('Server did not become ready')
        state.kill_server()
        raise

    return popen_time

# ################################################################################################################################
# ################################################################################################################################

def run_quickstart_and_enmasse(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    invoke_password:'str',
    rendered_yaml:'str',
    quickstart_prefix:'str',
) -> 'str':
    """ Creates a quickstart environment and imports the enmasse YAML.
    Returns the server directory path.
    """
    start_time = time.monotonic()

    state.quickstart_directory = tempfile.mkdtemp(prefix=quickstart_prefix)

    quickstart_environment = os.environ.copy()
    _ = quickstart_environment.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        zato_bin, 'quickstart', 'create', state.quickstart_directory,
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
    logger.info('Quickstart create: %.1fs', quickstart_time - start_time)

    server_directory = os.path.join(state.quickstart_directory, 'server1')

    # .. write the rendered YAML and import it, but only if we have a template ..
    if rendered_yaml:
        rendered_path = os.path.join(state.quickstart_directory, 'enmasse.yaml')

        with open(rendered_path, 'w') as rendered_file:
            _ = rendered_file.write(rendered_yaml)

        enmasse_environment = os.environ.copy()
        enmasse_environment['Zato_Needs_Config_Reload'] = 'False'

        enmasse_command = [
            zato_bin, 'enmasse', '--import', '--input', rendered_path, server_directory,
        ]

        enmasse_result = subprocess.run(
            enmasse_command, capture_output=True, text=True, check=False,
            timeout=_quickstart_timeout, env=enmasse_environment)

        if enmasse_result.returncode != 0:
            raise RuntimeError(f'enmasse import failed:\nstdout: {enmasse_result.stdout}\nstderr: {enmasse_result.stderr}')

        enmasse_time = time.monotonic()
        logger.info('Enmasse import: %.1fs', enmasse_time - quickstart_time)

    return server_directory

# ################################################################################################################################
# ################################################################################################################################

def create_zato_server_fixture(
    logger_name:'str',
    server_log_copy_name:'str',
    template_path:'str',
    quickstart_prefix:'str',
    extra_server_env:'strstrdict',
    patch_server_conf_bind:'bool',
    build_config_callback:'callable_',
) -> 'any_':
    """ Factory that returns a session-scoped pytest fixture for spinning up a Zato server.

    The build_config_callback receives (state, logger, zato_bin, server_directory, server_port, invoke_password)
    and must return (placeholders_dict, pre_server_callable_or_None).
    The pre_server_callable, if not None, is called after enmasse import but before starting the server.

    After the server is ready, build_config_callback is called again via populate_callback
    (set as an attribute on the returned fixture function).
    """

    logger = logging.getLogger(logger_name)

    state = SessionState(logger_name, server_log_copy_name)
    _ = atexit.register(state.cleanup)

    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin  = os.path.join(zato_base, 'code', 'bin', 'zato')

    @pytest.fixture(scope='session', autouse=True)
    def zato_server() -> 'any_':
        """ Session-scoped fixture that spins up a Zato quickstart environment.
        """
        # Kill any leftover Zato servers from interrupted previous runs ..
        _ = subprocess.run(['pkill', '-f', 'zato.server.main'], capture_output=True)
        time.sleep(2)

        start_time = time.monotonic()

        invoke_password = 'test.invoke.' + os.urandom(8).hex()

        # .. let the callback build placeholders, passwords and any pre-server work ..
        server_port = find_free_port()

        setup_result = build_config_callback(
            state=state,
            logger=logger,
            zato_bin=zato_bin,
            server_port=server_port,
            invoke_password=invoke_password,
        )

        placeholders = setup_result['placeholders']
        populate_callback = setup_result['populate_callback']

        # .. render the enmasse template if one was provided ..
        rendered_yaml = ''
        if template_path:
            rendered_yaml = render_template(template_path, placeholders)

        # .. create quickstart and optionally import enmasse ..
        server_directory = run_quickstart_and_enmasse(
            state=state,
            logger=logger,
            zato_bin=zato_bin,
            invoke_password=invoke_password,
            rendered_yaml=rendered_yaml,
            quickstart_prefix=quickstart_prefix,
        )

        # .. copy services into the pickup directory if needed ..
        hot_deploy_sources = setup_result.get('hot_deploy_sources', []) # type: ignore[union-attr]

        for source_path in hot_deploy_sources:
            pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
            file_name = os.path.basename(source_path)
            destination = os.path.join(pickup_directory, file_name)
            _ = shutil.copy2(source_path, destination)
            logger.info('Copied %s to %s', source_path, destination)

        # .. start the server ..
        broker_port = find_free_port()

        _ = start_server_process(
            state=state,
            logger=logger,
            zato_bin=zato_bin,
            server_directory=server_directory,
            server_port=server_port,
            broker_port=broker_port,
            extra_server_env=extra_server_env,
            patch_server_conf_bind=patch_server_conf_bind,
        )

        logger.info('Total setup: %.1fs', time.monotonic() - start_time)

        # .. let the callback populate TestConfig ..
        host = '127.0.0.1'

        populate_callback(
            host=host,
            server_port=server_port,
            invoke_password=invoke_password,
            server_directory=server_directory,
            zato_bin=zato_bin,
        )

        yield

        state.cleanup()

    # .. attach state to the fixture function so conftest files can reference it ..
    zato_server._state = state # type: ignore[attr-defined]

    return zato_server

# ################################################################################################################################
# ################################################################################################################################
