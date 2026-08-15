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
from urllib.error import URLError
from urllib.request import Request, urlopen

_this_directory = os.path.dirname(__file__)
_keycloak_directory = os.path.join(_this_directory, '..', '..', 'zato-common', 'test')

sys.path.insert(0, _this_directory)
sys.path.insert(0, _keycloak_directory)

# pytest
import pytest  # noqa: E402

# Zato
from zato.common.test import kill_server_process, rand_string  # noqa: E402
from zato.common.typing_ import cast_  # noqa: E402
from zato.common.util.config import get_config_object, update_config_file  # noqa: E402

# Zato - test helpers
import _constants  # noqa: E402
import _diag  # noqa: E402
import _enmasse  # noqa: E402
import containers  # noqa: E402
import keycloak_  # noqa: E402

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

@pytest.fixture(autouse=True)
def wire_log(request:'any_') -> 'any_':
    """ Points the wire log at a per-test file for the duration of each test.
    """

    _diag.set_current_test(request.node.nodeid)

    yield

    _diag.clear_current_test()

# ################################################################################################################################

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item:'any_', call:'any_') -> 'any_':
    """ On failure, dumps the Ollama container log next to the test's wire log
    and prints both paths in the failure output.
    """

    outcome = yield
    report = outcome.get_result()

    if report.when == 'call':
        if report.failed:

            if wire_path := _diag.get_current_path():

                lines = [f'wire log: {wire_path}']

                if ollama_path := _diag.dump_ollama_logs():
                    lines.append(f'ollama log: {ollama_path}')

                section_text = '\n'.join(lines)
                report.sections.append(('wire diagnostics', section_text))

# ################################################################################################################################
# ################################################################################################################################

_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')
_zato_py   = os.path.join(_zato_base, 'code', 'bin', 'python')

# The file-transfer listener that watches the pickup directory for runtime hot-deploy
_listener_path = os.path.join(
    _zato_base, 'code', 'zato-common', 'src', 'zato', 'common', 'file_transfer', 'listener.py')

# Where the fixture services and skills live, relative to this file
_fixtures_directory = os.path.join(_this_directory, 'fixtures')

_password = 'test.llm.invoke.' + rand_string()

_process_kill_timeout   = 5
_server_wait_timeout    = 120
_quickstart_timeout     = 180
_ping_poll_interval     = 0.5
_listener_settle_seconds = 2

# How long the boot-time hot deploy of the fixture services plus the enmasse-created
# gateways may need before the tool registries answer with the CRM tools
_gateway_ready_timeout = 60
_gateway_poll_interval = 0.5

_server_process   = None
_listener_process = None
_temp_directory   = None

# Where the server's output is persisted, outside the temp dir so it survives teardown
_server_log_path = os.path.join(tempfile.gettempdir(), 'zato_mcp_llm_live_server.log')

# Where the file listener's output is persisted
_listener_log_path = os.path.join(tempfile.gettempdir(), 'zato_mcp_llm_live_listener.log')

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

def _kill_process(process:'any_') -> 'None':
    """ Terminates a subprocess if it is still running, force-killing on timeout.
    """

    if process:
        if process.poll() is None:

            # Try graceful termination first ..
            process.terminate()

            try:
                _ = process.wait(timeout=_process_kill_timeout)

            # .. if it does not stop in time, force kill it.
            except subprocess.TimeoutExpired:
                process.kill()
                _ = process.wait(timeout=_process_kill_timeout)

# ################################################################################################################################
# ################################################################################################################################

def _kill_server() -> 'None':
    """ Terminates the server and file-listener subprocesses if they are still running.
    """

    global _server_process, _listener_process

    # Stop the file listener first so it does not race the server shutdown ..
    _kill_process(_listener_process)
    _listener_process = None

    # .. then stop the server and its child processes.
    kill_server_process(_server_process, _process_kill_timeout, server_directory=_temp_directory or '')
    _server_process = None

# ################################################################################################################################
# ################################################################################################################################

def _cleanup() -> 'None':
    """ Kills the server and removes the temporary directory.
    """

    # Stop the server process first ..
    _kill_server()

    global _temp_directory

    # .. then clean up the temporary directory.
    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

_ = atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'str', port:'int', timeout:'int' = _server_wait_timeout) -> 'None':
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
                    print(f'[TIMING] ping OK after {elapsed:.1f}s (attempt {attempt_number})')
                    return

        except (ConnectionRefusedError, OSError, URLError):
            elapsed_now = time.monotonic() - start_time
            print(f'[TIMING] ping attempt {attempt_number} at {elapsed_now:.1f}s: not ready')

        time.sleep(_ping_poll_interval)

    raise Exception(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _copy_fixture_services(server_directory:'str') -> 'None':
    """ Copies the CRM fixture services into the pickup directory before the server starts,
    so the boot scan deploys them and enmasse can put them on the gateways' allow lists.
    """

    source_directory = os.path.join(_fixtures_directory, 'services')
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')

    for file_name in sorted(os.listdir(source_directory)):
        if file_name.endswith('.py'):
            source_path = os.path.join(source_directory, file_name)
            _ = shutil.copy(source_path, os.path.join(pickup_directory, file_name))

# ################################################################################################################################

def _copy_fixture_skills(server_directory:'str') -> 'None':
    """ Copies the fixture skills into the server's config/repo/skills directory,
    where the gateways read them from on each prompts request.
    """

    source_directory = os.path.join(_fixtures_directory, 'skills')
    skills_directory = os.path.join(server_directory, 'config', 'repo', 'skills')

    for skill_name in sorted(os.listdir(source_directory)):

        source_path = os.path.join(source_directory, skill_name)
        target_path = os.path.join(skills_directory, skill_name)

        if os.path.isdir(source_path):
            _ = shutil.copytree(source_path, target_path, dirs_exist_ok=True)

# ################################################################################################################################

def _spawn_server(server_directory:'str', server_env:'any_', log_mode:'str') -> 'None':
    """ Starts the server process in foreground mode and streams its output
    to the console and to the persistent log file.
    """

    global _server_process

    _server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    popen_time = time.monotonic()
    server_log_file = open(_server_log_path, log_mode)

    # Stream server stdout in a background thread, printing each line and writing it to the log file.
    def _stream_server_output() -> 'None':
        """ Reads server stdout line by line, prints each with a timestamp prefix,
        and writes it to the persistent log file.
        """

        server_process = _server_process
        assert server_process is not None
        assert server_process.stdout is not None
        stdout = server_process.stdout
        for line in iter(stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - popen_time
            print(f'[SERVER {elapsed:6.1f}s] {text}')

            # .. mirror to the persistent log file and flush so it is readable on timeout ..
            _ = server_log_file.write(f'[SERVER {elapsed:6.1f}s] {text}\n')
            server_log_file.flush()

    stdout_thread = threading.Thread(target=_stream_server_output, daemon=True)
    stdout_thread.start()

# ################################################################################################################################

def _spawn_listener(pickup_directory:'str', listener_env:'any_', log_mode:'str') -> 'None':
    """ Starts the file-transfer listener that watches the pickup directory,
    with its output going to the persistent listener log file.
    """

    global _listener_process

    listener_log_file = open(_listener_log_path, log_mode)

    _listener_process = subprocess.Popen(
        [_zato_py, _listener_path, pickup_directory],
        env=listener_env,
        stdout=listener_log_file,
        stderr=subprocess.STDOUT,
    )

    # Give the listener a moment to initialize its directory watch
    time.sleep(_listener_settle_seconds)

# ################################################################################################################################

def _wait_for_gateways(host:'str', port:'int') -> 'None':
    """ Polls the main gateway until its tool registry answers with the CRM tools,
    which proves both the fixture services and the enmasse-created gateways are live.
    """

    # local
    from _client import MCPClient

    mcp_url = f'http://{host}:{port}{_constants.Path_Main}'
    auth = (_constants.Username_Basic, _constants.Password_Basic)

    deadline = time.monotonic() + _gateway_ready_timeout
    last_error = ''

    while time.monotonic() < deadline:

        try:
            client = MCPClient(mcp_url, auth=auth)
            initialize_result = client.initialize()

            response = client.jsonrpc('tools/list', session_id=initialize_result.session_id)
            body = response.json()

            tool_names = []

            for tool in body['result']['tools']:
                tool_names.append(tool['name'])

            if _constants.Service_Customer_Get in tool_names:
                print(f'[TIMING] gateways ready with tools: {tool_names}')
                return

            last_error = f'CRM tools not listed yet: {tool_names}'

        except Exception as e:
            last_error = str(e)

        time.sleep(_gateway_poll_interval)

    raise Exception(f'Gateways did not become ready within {_gateway_ready_timeout}s: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def ollama() -> 'any_':
    """ Session-scoped fixture that makes sure the Ollama container is running with the model pulled.
    Only the tests that drive the LLM depend on it - everything else runs without Docker.
    """

    if not containers.is_docker_available():
        pytest.skip('Docker is not available')

    containers.ensure_ollama()
    containers.ensure_model()

    out = {
        'openai_url': containers.Ollama_OpenAI_URL,
        'model': containers.Model_Name,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def keycloak() -> 'None':
    """ Session-scoped fixture that makes sure the Keycloak container is running and provisioned.
    Only the tests that use Keycloak-issued tokens depend on it.
    """

    if not containers.is_docker_available():
        pytest.skip('Docker is not available')

    keycloak_.ensure_keycloak()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server() -> 'any_':
    """ Session-scoped fixture that spins up a Zato quickstart environment with the CRM fixture
    services and skills in place, starts the server, imports the suite's security definitions,
    groups, gateways and the self.llm outconn via enmasse, and yields connection details.
    """

    global _server_process, _temp_directory

    start_time = time.monotonic()

    port = _find_free_port()
    _temp_directory = tempfile.mkdtemp(prefix='zato_mcp_llm_live_test_')

    # Create a quickstart environment with a clean env,
    # removing stale COVERAGE_PROCESS_START interference ..
    quickstart_env = os.environ.copy()
    _ = quickstart_env.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', _temp_directory,
        '--servers', '1',
        '--password', _password,
        '--server-api-client-for-scheduler-password', _password,
        '--no-scheduler',
    ]

    result = subprocess.run(
        quickstart_command, capture_output=True, text=True, check=False,
        timeout=_quickstart_timeout, env=quickstart_env)

    if result.returncode != 0:
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    quickstart_time = time.monotonic()
    print(f'\n[TIMING] quickstart create: {quickstart_time - start_time:.1f}s')

    # .. patch server.conf to use our dynamically allocated port ..
    server_directory = os.path.join(_temp_directory, 'server1')
    repo_location = os.path.join(server_directory, 'config', 'repo')
    config = cast_('any_', get_config_object(repo_location, 'server.conf'))
    config['main']['port'] = str(port)
    config['main']['bind'] = f'127.0.0.1:{port}'
    update_config_file(config, repo_location, 'server.conf')

    # .. the CRM services go into the pickup directory before the server starts,
    # so the boot scan deploys them and the skills go into config/repo/skills ..
    _copy_fixture_services(server_directory)
    _copy_fixture_skills(server_directory)

    # .. start the server in foreground mode ..
    broker_port = _find_free_port()

    # The marker directory is where the fixture services record their invocations -
    # both marker files exist from the start.
    marker_directory = os.path.join(_temp_directory, 'markers')
    os.makedirs(marker_directory, exist_ok=True)

    marker_path = os.path.join(marker_directory, 'invocations.txt')
    payload_path = os.path.join(marker_directory, 'payloads.txt')

    for _marker_file_path in (marker_path, payload_path):
        with open(_marker_file_path, 'w'):
            pass

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env['Zato_Test_LLM_Marker_Dir'] = marker_directory
    server_env['Zato_MCP_Session_Reaper_Interval'] = str(_constants.Reaper_Interval_Seconds)

    # Origin validation is on, so requests that carry an Origin header outside
    # a gateway's allowed list are refused - no test client sends one otherwise.
    server_env['Zato_MCP_Check_Origin'] = 'true'

    _ = server_env.pop('COVERAGE_PROCESS_START', None)

    # Point the audit log at a file inside the temp directory so the live server
    # never writes into the real environment's audit database.
    audit_db_path = os.path.join(_temp_directory, 'audit.db')
    server_env['Zato_Audit_Log_DB_Name'] = audit_db_path

    _spawn_server(server_directory, server_env, 'w')
    print(f'[TIMING] server log: {_server_log_path}')

    # .. wait for the server to come up ..
    host = '127.0.0.1'

    try:
        _wait_for_server(host, port)
        ready_time = time.monotonic()
        print(f'[TIMING] server ready: {ready_time - start_time:.1f}s')

    except Exception:

        # .. give the streaming thread a moment to flush any final lines ..
        time.sleep(1)

        # .. dump the full captured server output so the real startup failure is visible ..
        print('\n--- Server did not become ready, full server output follows ---\n')

        if os.path.isfile(_server_log_path):
            with open(_server_log_path) as captured_log:
                print(captured_log.read())

        print(f'\n--- End of server output (also saved at {_server_log_path}) ---\n')

        _kill_server()
        raise

    # .. one import creates the security definitions, groups, every gateway and the llm outconn ..
    _enmasse.run_import(server_directory, _enmasse.build_suite_config())

    # .. start the file-transfer listener that watches the pickup directory, so that
    # files dropped at runtime trigger hot-deploy - the runtime hot-deploy tests need it ..
    pickup_directory = os.path.join(server_directory, 'pickup', 'incoming', 'services')
    web_admin_repo = os.path.join(_temp_directory, 'web-admin', 'config', 'repo')

    listener_env = os.environ.copy()
    listener_env['Zato_Config_Bind_Port'] = str(port)
    listener_env['Zato_Web_Admin_Repo_Dir'] = web_admin_repo
    _ = listener_env.pop('COVERAGE_PROCESS_START', None)

    _spawn_listener(pickup_directory, listener_env, 'w')

    # .. wait until the main gateway answers with the CRM tools ..
    _wait_for_gateways(host, port)

    total_time = time.monotonic() - start_time
    print(f'[TIMING] total setup: {total_time:.1f}s')

    def _mcp_url(url_path:'str') -> 'str':
        out = f'http://{host}:{port}{url_path}'
        return out

    def _restart_server() -> 'None':
        """ Stops the server process and starts it again with the same configuration,
        returning once the gateways answer. The kill matches every process whose
        command line carries the temp directory, which includes the listener,
        so the listener stops first and starts anew once the server is back.
        """

        global _server_process, _listener_process

        _kill_process(_listener_process)
        _listener_process = None

        kill_server_process(_server_process, _process_kill_timeout, server_directory=_temp_directory or '')
        _server_process = None

        _spawn_server(server_directory, server_env, 'a')
        _wait_for_server(host, port)
        _wait_for_gateways(host, port)

        _spawn_listener(pickup_directory, listener_env, 'a')

    # .. yield connection details to the tests.
    yield {
        'restart': _restart_server,
        'host': host,
        'port': port,
        'password': _password,
        'server_directory': server_directory,
        'temp_directory': _temp_directory,
        'pickup_directory': pickup_directory,
        'audit_db_path': audit_db_path,
        'marker_path': marker_path,
        'payload_path': payload_path,
        'server_log_path': _server_log_path,
        'mcp_url': _mcp_url,
        'basic_auth': (_constants.Username_Basic, _constants.Password_Basic),
        'basic_auth_b': (_constants.Username_Basic_B, _constants.Password_Basic_B),
        'basic_auth_shared': (_constants.Username_Basic_Shared, _constants.Password_Basic_Shared),
        'apikey_value': _constants.APIKey_Value,
        'bearer_static_token': _constants.Bearer_Static_Token,
    }

    # Teardown: stop the server and remove the temporary directory.
    _kill_server()

    if _temp_directory:
        if os.path.isdir(_temp_directory):
            shutil.rmtree(_temp_directory, ignore_errors=True)

    _temp_directory = None

# ################################################################################################################################
# ################################################################################################################################
