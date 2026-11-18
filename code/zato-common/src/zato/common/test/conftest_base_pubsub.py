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
import subprocess
import tempfile
import threading
import time
from http.client import OK
from urllib.error import URLError
from urllib.request import Request, urlopen

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.api import PubSub
from zato.common.db_env.database import database_config
from zato.common.db_env.database_env import DatabaseEnv
from zato.common.db_env.fence import ModuleCtx as FenceCtx
from zato.common.hl7.mllp.haproxy import Env_Port_Name as MLLP_Env_Port_Name
from zato.common.test.process_util import get_process_tree_pids
from zato.common.typing_ import cast_
from zato.common.test.pubsub_database import get_db_mode, is_postgresql_mode, start_pubsub_database, \
    stop_pubsub_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Literal
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anydict, callable_, intlist, strnone, strstrdict, strtuple

    fixture_scope = Literal['session', 'package', 'module', 'class', 'function']

# ################################################################################################################################
# ################################################################################################################################

_process_kill_timeout = 5
_server_wait_timeout  = 120

# Large enough for the system perf suite, whose enmasse import creates over
# two thousand objects - ordinary suites finish well within the old 180 seconds.
_quickstart_timeout   = 600

# How long an import into a running server waits for a service that an object names to be deployed, in seconds
_enmasse_missing_wait_time = 30

_ping_poll_interval   = 0.5

# The process name of the worker of a server, the process ID returned when a server has no worker,
# how long the arbiter is given to start a new worker and how often the processes of a server are read, in seconds
_worker_process_name  = 'zato-worker'
_no_worker_pid        = 0
_worker_timeout       = 120.0
_worker_poll_interval = 0.2

# The address that a server of a session listens on
_server_host = '127.0.0.1'

# The variable that keeps the quickstart directory of a session, with its database, after the session ends
Env_Keep_Quickstart = 'Zato_Test_Keep_Quickstart'

# What the arbiter logs the first time that the worker is ready
_worker_ready_pattern = re.compile(r'zato\.server\.arbiter:\d+ - Worker is ready')

# The variables of the operating system that a server process needs, the only ones that it receives
# from the environment of the test process apart from those that select the Zato database
_system_env_names = ('HOME', 'LANG', 'LC_ALL', 'LD_LIBRARY_PATH', 'LOGNAME', 'PATH', 'TMPDIR', 'TZ', 'USER')

# The variables that select the Zato database and the file of the generation of the active server, which the session
# sets for the test process and the server alike. The size of the pool is not one of them, it reaches the server
# only through the explicit variables of the server.
_database_env_names = (
    database_config.env_type,
    database_config.env_path,
    database_config.env_host,
    database_config.env_port,
    database_config.env_username,
    database_config.env_password,
    database_config.env_password_file,
    database_config.env_name,
    database_config.env_ssl,
    database_config.env_ssl_ca_file,
    database_config.env_ssl_cert_file,
    database_config.env_ssl_key_file,
    database_config.env_ssl_verify,
    FenceCtx.Env_Generation_File,
)

# The logs that are copied out of an environment before it is torn down
_server_log_file_name        = 'server.log'
_file_transfer_log_file_name = 'file-transfer.log'

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
        self.pubsub_database:'PubSubDatabase | None' = None

        # The internal MLLP port of the server of this session, the same one each time that the server starts
        self.mllp_port = find_free_port()

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

        # .. also kill the processes that the server of this session forked, and no other server ..
        if self.quickstart_directory:
            _ = subprocess.run(['pkill', '-f', f'zato.server.main {self.quickstart_directory}'], capture_output=True)

# ################################################################################################################################

    def stop_all_receivers(self) -> 'None':
        """ Stops every running receiver.
        """
        for receiver in self.receivers:
            receiver.stop()

        receiver_count = len(self.receivers)
        self.receivers.clear()
        suffix = 'receiver' if receiver_count == 1 else 'receivers'
        self._logger.info('Stopped %d %s', receiver_count, suffix)

# ################################################################################################################################

    def cleanup(self) -> 'None':
        """ Full teardown - server, receivers, temp directory.
        """
        # Copy server logs before killing anything ..
        if self.quickstart_directory:
            logs_directory = os.path.join(self.quickstart_directory, 'server1', 'logs')

            # The server's log is copied out under the configured name, the file transfer one
            # under that name prefixed, so that the two copies never collide.
            log_copies = {
                _server_log_file_name: self._server_log_copy_name,
                _file_transfer_log_file_name: f'file-transfer-{self._server_log_copy_name}',
            }

            for log_file_name, copy_name in log_copies.items():
                log_path = os.path.join(logs_directory, log_file_name)
                if os.path.exists(log_path):
                    destination = f'/tmp/{copy_name}'
                    _ = shutil.copy(log_path, destination)
                    self._logger.info('Copied %s to %s', log_file_name, destination)

        # Stop the server process ..
        self.kill_server()

        # .. then stop all receivers ..
        self.stop_all_receivers()

        # .. then clean up the temporary directories, unless the quickstart one is to be kept for an analysis.
        if self.quickstart_directory:
            if os.environ.get(Env_Keep_Quickstart, ''):
                self._logger.info('Kept quickstart directory %s', self.quickstart_directory)
            else:
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

def get_server_pids(state:'SessionState') -> 'intlist':
    """ Returns the processes of the server of a session, which descend from the process that started it.
    """
    server_process = cast_('subprocess.Popen[bytes]', state.server_process)

    out = get_process_tree_pids(server_process.pid)
    return out

# ################################################################################################################################

def _get_worker_pid(state:'SessionState') -> 'int':
    """ Returns the process ID of the worker of the server of a session, or zero if the server has no worker.
    """
    for pid in get_server_pids(state):

        try:
            with open(f'/proc/{pid}/comm') as process_name_file:
                process_name = process_name_file.read()
        except FileNotFoundError:
            continue

        if process_name.strip() == _worker_process_name:
            out = pid
            break

    else:
        out = _no_worker_pid

    return out

# ################################################################################################################################

def kill_server_worker(logger:'logging.Logger', state:'SessionState', port:'int') -> 'None':
    """ Kills the worker of the server of a session with SIGKILL and waits until the arbiter has started a new one
    that responds.
    """
    old_pid = _get_worker_pid(state)

    if old_pid == _no_worker_pid:
        raise Exception('No worker process of the server found')

    os.kill(old_pid, signal.SIGKILL)

    deadline = time.monotonic() + _worker_timeout

    # Wait for a worker with another process ID ..
    while True:

        if time.monotonic() > deadline:
            raise Exception(f'No new worker within {_worker_timeout}s')

        new_pid = _get_worker_pid(state)

        if new_pid not in (_no_worker_pid, old_pid):
            break

        time.sleep(_worker_poll_interval)

    # .. and until it responds.
    wait_for_server(logger, _server_host, port)

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

def get_process_environment() -> 'strstrdict':
    """ Builds the environment of a process of an installation, such as the cleanup process of pub/sub,
    from the variables of the operating system and those that select the Zato database alone.
    """
    out:'strstrdict' = {}

    for name in _system_env_names + _database_env_names:
        if name in os.environ:
            out[name] = os.environ[name]

    return out

# ################################################################################################################################

def get_server_environment(
    server_port:'int',
    broker_port:'int',
    mllp_port:'int',
    extra_server_env:'strstrdict',
    ) -> 'strstrdict':
    """ Builds the environment of a server process from an explicit mapping - the variables of the operating system,
    those that select the Zato database, the ports of the server and the variables that the caller gives,
    so that no other variable of the environment of the test process reaches the server.
    """
    out = get_process_environment()

    out['Zato_Config_Bind_Port'] = str(server_port)
    out['Zato_Broker_HTTP_Port'] = str(broker_port)
    out[MLLP_Env_Port_Name] = str(mllp_port)

    out.update(extra_server_env)

    return out

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
    command_prefix:'strtuple' = (),
) -> 'float':
    """ Starts the Zato server process, streams stdout, and waits for it to be ready, with the command of the server
    preceded by the given prefix, such as the command that places the server in a transient systemd scope.
    Returns the popen timestamp.
    """
    server_environment = get_server_environment(server_port, broker_port, state.mllp_port, extra_server_env)

    patch_server_conf(server_directory, server_port, patch_server_conf_bind)

    command = [*command_prefix, zato_bin, 'start', server_directory, '--fg']

    state.server_process = subprocess.Popen(
        command,
        env=server_environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    popen_time = time.monotonic()

    # The worker answers before it has deployed the services of the pickup directory,
    # so the server is ready for the tests only once the arbiter reports the worker ready.
    worker_ready = threading.Event()

    # .. stream server stdout in a background thread ..
    def _stream_server_output() -> 'None':
        stdout = state.server_process.stdout # type: ignore[union-attr]
        readline = stdout.readline # pyright: ignore[reportOptionalMemberAccess]

        for line in iter(readline, b''):
            decoded = line.decode('utf-8', errors='replace')
            text = decoded.rstrip()
            elapsed = time.monotonic() - popen_time
            logger.debug('[SERVER %6.1fs] %s', elapsed, text)

            if _worker_ready_pattern.search(text):
                worker_ready.set()

    stdout_thread = threading.Thread(target=_stream_server_output, name='server-output', daemon=True)
    stdout_thread.start()

    # .. wait for the server to come up ..
    host = '127.0.0.1'

    try:
        wait_for_server(logger, host, server_port)

        # .. and for its worker.
        if not worker_ready.wait(_server_wait_timeout):
            raise RuntimeError(f'The worker of the server was not ready within {_server_wait_timeout}s')

        logger.info('Server ready: %.1fs', time.monotonic() - popen_time)

    except (ConnectionRefusedError, OSError, RuntimeError):
        logger.error('Server did not become ready')
        state.kill_server()
        raise

    return popen_time

# ################################################################################################################################

def patch_server_conf(server_directory:'str', server_port:'int', patch_server_conf_bind:'bool') -> 'None':
    """ Points the server.conf of a server at the test Redis database and, if requested, at the given port.
    """
    server_conf_path = os.path.join(server_directory, 'config', 'repo', 'server.conf')

    with open(server_conf_path, 'r') as server_conf_file:
        server_conf_content = server_conf_file.read()

    server_conf_content = re.sub(
        r'^(db\s*=\s*)\d+',
        f'\\g<1>{PubSub.Test_Redis_DB}',
        server_conf_content,
        flags=re.MULTILINE,
    )

    # .. patch bind port if needed so that CLI commands use the dynamic port ..
    if patch_server_conf_bind:
        server_conf_content = re.sub(
            r'^(bind\s*=\s*)\S+',
            f'\\g<1>0.0.0.0:{server_port}',
            server_conf_content,
            flags=re.MULTILINE,
        )

    with open(server_conf_path, 'w') as server_conf_file:
        _ = server_conf_file.write(server_conf_content)

# ################################################################################################################################
# ################################################################################################################################

def run_quickstart_and_enmasse(
    state:'SessionState',
    logger:'logging.Logger',
    zato_bin:'str',
    invoke_password:'str',
    rendered_yaml:'str',
    quickstart_prefix:'str',
    extra_env:'strstrdict | None' = None,
    quickstart_parent_dir:'strnone' = None,
) -> 'str':
    """ Creates a quickstart environment and imports the enmasse YAML, with the given variables added
    to the environment of both commands and under the given parent directory, if any.
    Returns the server directory path.
    """
    start_time = time.monotonic()

    state.quickstart_directory = tempfile.mkdtemp(prefix=quickstart_prefix, dir=quickstart_parent_dir)

    quickstart_environment = os.environ.copy()
    _ = quickstart_environment.pop('COVERAGE_PROCESS_START', None)

    if extra_env:
        quickstart_environment.update(extra_env)

    quickstart_command = [
        zato_bin, 'quickstart', 'create', state.quickstart_directory,
        '--force',
        '--password', invoke_password,
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

        if extra_env:
            enmasse_environment.update(extra_env)

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

def import_into_running_server(zato_bin:'str', server_directory:'str', yaml_text:'str', directory:'str') -> 'None':
    """ Imports the enmasse YAML into a running server, which is what objects need when they name services
    that the server deploys from its pickup directory as it starts.
    """
    yaml_path = os.path.join(directory, 'enmasse-running.yaml')

    with open(yaml_path, 'w') as yaml_file:
        _ = yaml_file.write(yaml_text)

    command = [
        zato_bin, 'enmasse', server_directory, '--import', '--input', yaml_path,
        '--missing-wait-time', str(_enmasse_missing_wait_time),
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=_quickstart_timeout)

    if result.returncode != 0:
        raise RuntimeError(f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

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
    scope:'fixture_scope' = 'session',
    autouse:'bool' = True,
    uses_environment_database:'bool' = False,
    quickstart_parent_dir:'strnone' = None,
) -> 'any_':
    """ Factory that returns a pytest fixture of the given scope that starts a Zato server.

    The build_config_callback receives (state, logger, zato_bin, server_port, invoke_password) and returns a dict
    with 'placeholders' for the enmasse template and 'populate_callback', which is called with (host, server_port,
    invoke_password, server_directory, zato_bin) once the server is ready. The dict may also hold 'enmasse_yaml',
    the definition to import when there is no template, 'pre_server_callback', which is called with (server_directory)
    once the database is selected and before the server starts, 'hot_deploy_sources', the service files of the pickup
    directory, 'server_env', the variables added to the environment of the server, and 'server_command_prefix',
    the command that the command of the server is started through.

    With uses_environment_database, the server uses the Zato database that the environment of the test process
    already selects, otherwise the fixture starts a database of its own. With quickstart_parent_dir, the environment
    and its SQLite database are created under that directory.
    """

    logger = logging.getLogger(logger_name)

    state = SessionState(logger_name, server_log_copy_name)
    _ = atexit.register(state.cleanup)

    zato_base = os.environ['ZATO_TEST_BASE_DIR']
    zato_bin  = os.path.join(zato_base, 'code', 'bin', 'zato')

    @pytest.fixture(scope=scope, autouse=autouse)
    def zato_server() -> 'any_':
        """ Fixture that spins up a Zato quickstart environment.
        """
        start_time = time.monotonic()

        invoke_password = 'test.invoke.' + CryptoManager.generate_hex_string()

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

        # .. render the enmasse template if one was provided, or take the definition that the callback built ..
        rendered_yaml = ''
        if template_path:
            rendered_yaml = render_template(template_path, placeholders)
        elif 'enmasse_yaml' in setup_result:
            rendered_yaml = setup_result['enmasse_yaml']

        # .. create quickstart and optionally import enmasse ..
        server_directory = run_quickstart_and_enmasse(
            state=state,
            logger=logger,
            zato_bin=zato_bin,
            invoke_password=invoke_password,
            rendered_yaml=rendered_yaml,
            quickstart_prefix=quickstart_prefix,
            quickstart_parent_dir=quickstart_parent_dir,
        )

        # .. point the Zato database at this environment's own file, or at a PostgreSQL container of this session,
        # .. so the server, any subprocesses and the test process itself all share one database
        # .. that starts empty and disappears together with the environment ..
        db_mode = get_db_mode()

        # .. the generation of the active server is recorded in this environment too ..
        generation_file_path = os.path.join(server_directory, 'database-generation')
        os.environ['Zato_Database_Generation_File'] = generation_file_path

        # .. the server receives the variables of the suite and those of its database explicitly ..
        server_env = dict(extra_server_env)

        if 'server_env' in setup_result:
            server_env.update(setup_result['server_env'])

        # .. a database that the environment selects already is the one that the server uses ..
        if uses_environment_database:
            pubsub_database = None
            logger.info('Zato database: %s', os.environ[DatabaseEnv.Env_Type])

        elif is_postgresql_mode(db_mode):
            pubsub_database = start_pubsub_database('live', db_mode)
            state.pubsub_database = pubsub_database
            _ = atexit.register(stop_pubsub_database, pubsub_database)
            os.environ.update(pubsub_database.env)
            server_env.update(pubsub_database.env)
            logger.info('Zato database: %s (%s)', pubsub_database.container_name, db_mode)
        else:
            pubsub_database = None
            db_path = os.path.join(server_directory, DatabaseEnv.File_Name)
            os.environ[DatabaseEnv.Env_Type] = DatabaseEnv.Type_SQLite
            os.environ[DatabaseEnv.Env_Path] = db_path
            logger.info('Zato database: %s', db_path)

        # .. let the callback seed the database before the server uses it ..
        if 'pre_server_callback' in setup_result:
            setup_result['pre_server_callback'](server_directory=server_directory)

        # .. copy services into the pickup directory if needed ..
        hot_deploy_sources = setup_result.get('hot_deploy_sources', []) # type: ignore[union-attr]

        for source_path in hot_deploy_sources:
            pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
            file_name = os.path.basename(source_path)
            destination = os.path.join(pickup_directory, file_name)
            _ = shutil.copy2(source_path, destination)
            logger.info('Copied %s to %s', source_path, destination)

        # .. the command of the server may be started through another one ..
        if 'server_command_prefix' in setup_result:
            command_prefix = tuple(setup_result['server_command_prefix'])
        else:
            command_prefix = ()

        # .. start the server ..
        broker_port = find_free_port()

        _ = start_server_process(
            state=state,
            logger=logger,
            zato_bin=zato_bin,
            server_directory=server_directory,
            server_port=server_port,
            broker_port=broker_port,
            extra_server_env=server_env,
            patch_server_conf_bind=patch_server_conf_bind,
            command_prefix=command_prefix,
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

        if pubsub_database:
            stop_pubsub_database(pubsub_database)
            state.pubsub_database = None

    # .. attach state to the fixture function so conftest files can reference it ..
    zato_server._state = state # type: ignore[attr-defined]

    return zato_server

# ################################################################################################################################
# ################################################################################################################################
