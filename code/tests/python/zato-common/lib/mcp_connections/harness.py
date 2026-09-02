# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from http.client import OK
from json import dumps
from urllib.error import URLError
from urllib.request import Request, urlopen

# requests
import requests

# PyYAML
from yaml import safe_dump

# Zato
from zato.common.test import kill_server_process
from zato.common.typing_ import cast_
from zato.common.util.config import get_config_object, update_config_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strlist, strnone, tupnone

# ################################################################################################################################
# ################################################################################################################################

# Where the zato binaries live.
_zato_base = os.environ['ZATO_TEST_BASE_DIR']
_zato_bin  = os.path.join(_zato_base, 'code', 'bin', 'zato')

# Where the shared LLM agent harness lives.
llm_harness_directory = os.path.join(
    _zato_base, 'code', 'tests', 'python', 'zato-server', 'mcp_llm_live')

_process_kill_timeout = 5
_server_wait_timeout  = 120
_quickstart_timeout   = 180
_enmasse_timeout      = 120
_ping_poll_interval   = 0.5

# How long the enmasse-created gateway may need before its tool registry
# answers with the expected connection tool
_gateway_ready_timeout = 60
_gateway_poll_interval = 0.5

# How long one MCP JSON-RPC request of the readiness poll may take, in seconds
_request_timeout = 30

# The header carrying the MCP session between requests
_session_header = 'Mcp-Session-Id'

# The protocol revision the readiness poll initializes with
_protocol_version = '2025-06-18'

# ################################################################################################################################
# ################################################################################################################################

def add_llm_harness_to_path() -> 'None':
    """ Makes the shared LLM agent harness importable flat - ollama_containers,
    _agent, _client and the rest.
    """

    # The path goes last - the directory has its own conftest.py and going first
    # would shadow the conftest of the suite that calls this function.
    if llm_harness_directory not in sys.path:
        sys.path.append(llm_harness_directory)

# ################################################################################################################################
# ################################################################################################################################

def find_free_port() -> 'int':
    """ Returns a free TCP port on localhost.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))

        socket_address = tcp_socket.getsockname()

        out = socket_address[1]
        return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class LiveEnvironment:
    """ One quickstart environment running for a live suite - the server underneath,
    where it listens and where its files live.
    """

    host: 'str'
    port: 'int'
    server_directory: 'str'
    temp_directory: 'str'
    server_log_path: 'str'
    server_process: 'any_'

    def mcp_url(self, url_path:'str') -> 'str':
        """ The full address of one MCP gateway of this environment.
        """

        out = f'http://{self.host}:{self.port}{url_path}'
        return out

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'str', port:'int') -> 'None':
    """ Polls the server's /zato/ping endpoint until it returns 200 or the timeout expires.
    """

    ping_url = f'http://{host}:{port}/zato/ping'
    deadline = time.monotonic() + _server_wait_timeout

    while time.monotonic() < deadline:

        try:
            request = Request(ping_url, method='GET')

            with urlopen(request, timeout=_process_kill_timeout) as response:
                if response.status == OK:
                    return

        except (ConnectionRefusedError, OSError, URLError):
            pass

        time.sleep(_ping_poll_interval)

    raise Exception(f'Server at {host}:{port} did not respond within {_server_wait_timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def start_environment(prefix:'str', extra_environ:'anydict | None' = None) -> 'LiveEnvironment':
    """ Creates a quickstart environment on free ports and starts its server
    in foreground mode, streaming the output to the console and to a log file
    that survives the environment's teardown.
    """

    password = f'test.{prefix}.password'

    port = find_free_port()
    temp_directory = tempfile.mkdtemp(prefix=f'zato_{prefix}_test_')

    # Create the quickstart environment with a clean environment,
    # removing stale COVERAGE_PROCESS_START interference ..
    quickstart_environ = os.environ.copy()
    _ = quickstart_environ.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _zato_bin, 'quickstart', 'create', temp_directory,
        '--servers', '1',
        '--password', password,
        '--server-api-client-for-scheduler-password', password,
        '--no-scheduler',
    ]

    result = subprocess.run(
        quickstart_command, capture_output=True, text=True, check=False,
        timeout=_quickstart_timeout, env=quickstart_environ)

    if result.returncode != 0:
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    # .. patch server.conf to use the dynamically allocated port ..
    server_directory = os.path.join(temp_directory, 'server1')
    repo_location = os.path.join(server_directory, 'config', 'repo')
    config = cast_('any_', get_config_object(repo_location, 'server.conf'))
    config['main']['port'] = str(port)
    config['main']['bind'] = f'127.0.0.1:{port}'
    update_config_file(config, repo_location, 'server.conf')

    # .. the server's environment carries the port, its own broker port
    # and an audit database inside the temp directory ..
    broker_port = find_free_port()
    audit_db_path = os.path.join(temp_directory, 'audit.db')

    server_environ = os.environ.copy()
    server_environ['Zato_Config_Bind_Port'] = str(port)
    server_environ['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_environ['Zato_Audit_Log_DB_Name'] = audit_db_path
    _ = server_environ.pop('COVERAGE_PROCESS_START', None)

    if extra_environ:
        server_environ.update(extra_environ)

    # .. start the server in foreground mode ..
    server_process = subprocess.Popen(
        [_zato_bin, 'start', server_directory, '--fg'],
        env=server_environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # .. its output goes both to the console and to a log file
    # outside the temp directory ..
    server_log_path = os.path.join(tempfile.gettempdir(), f'zato_{prefix}_server.log')
    server_log_file = open(server_log_path, 'w')
    start_time = time.monotonic()

    def _stream_server_output() -> 'None':
        """ Reads server stdout line by line, prints each with a timestamp prefix
        and mirrors it to the persistent log file.
        """

        stdout = server_process.stdout
        assert stdout is not None

        for line in iter(stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - start_time
            print(f'[SERVER {elapsed:6.1f}s] {text}')

            _ = server_log_file.write(f'[SERVER {elapsed:6.1f}s] {text}\n')
            server_log_file.flush()

    stdout_thread = threading.Thread(target=_stream_server_output, daemon=True)
    stdout_thread.start()

    # .. and wait until it answers, dumping the captured log if it does not.
    host = '127.0.0.1'

    out = LiveEnvironment()
    out.host = host
    out.port = port
    out.server_directory = server_directory
    out.temp_directory = temp_directory
    out.server_log_path = server_log_path
    out.server_process = server_process

    try:
        _wait_for_server(host, port)

    except Exception:

        # Give the streaming thread a moment to flush any final lines ..
        time.sleep(1)

        # .. show the full server output ..
        print('\n--- Server did not become ready, full server output follows ---\n')

        if os.path.isfile(server_log_path):
            with open(server_log_path) as captured_log:
                print(captured_log.read())

        print(f'\n--- End of server output (also saved at {server_log_path}) ---\n')

        # .. and stop everything before re-raising.
        stop_environment(out)
        raise

    return out

# ################################################################################################################################
# ################################################################################################################################

def stop_environment(environment:'LiveEnvironment') -> 'None':
    """ Stops the environment's server and removes its temporary directory.
    """

    kill_server_process(
        environment.server_process, _process_kill_timeout, server_directory=environment.temp_directory)

    if os.path.isdir(environment.temp_directory):
        shutil.rmtree(environment.temp_directory, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

def run_enmasse_import(server_directory:'str', config:'stranydict') -> 'None':
    """ Writes the config out as YAML and runs one enmasse import against the live server.
    """

    yaml_text = safe_dump(config, default_flow_style=False, sort_keys=False)

    tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-mcp-connections-{os.getpid()}.yaml')

    try:
        with open(tmp_yaml, 'w') as yaml_file:
            _ = yaml_file.write(yaml_text)

        result = subprocess.run(
            [_zato_bin, 'enmasse', server_directory, '--verbose', '--import', '--input', tmp_yaml],
            capture_output=True, text=True, timeout=_enmasse_timeout,
        )

        if result.returncode != 0:
            raise Exception(
                f'enmasse --import failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

    finally:
        if os.path.isfile(tmp_yaml):
            os.unlink(tmp_yaml)

# ################################################################################################################################
# ################################################################################################################################

def run_enmasse_export(server_directory:'str', output_path:'str', include_type:'str') -> 'None':
    """ Runs one enmasse export of the given object types against the live server.
    """

    result = subprocess.run(
        [_zato_bin, 'enmasse', server_directory, '--verbose', '--export',
            '--output', output_path, '--include-type', include_type],
        capture_output=True, text=True, timeout=_enmasse_timeout,
    )

    if result.returncode != 0:
        raise Exception(
            f'enmasse --export failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################
# ################################################################################################################################

def _jsonrpc(mcp_url:'str', auth:'tupnone', method:'str', params:'anydict', session_id:'strnone') -> 'anydict':
    """ Sends one MCP JSON-RPC request and returns the parsed response body.
    """

    headers = {'Content-Type': 'application/json'}

    if session_id:
        headers[_session_header] = session_id

    body = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': method,
        'params': params,
    }

    response = requests.post(mcp_url, data=dumps(body), headers=headers, auth=auth, timeout=_request_timeout)

    if not response.ok:
        raise Exception(f'MCP request `{method}` failed with HTTP {response.status_code}: {response.text}')

    out = response.json()
    out['_session_id'] = response.headers.get(_session_header)

    return out

# ################################################################################################################################

def get_tool_names(mcp_url:'str', auth:'tupnone') -> 'anylist':
    """ The names of every tool one gateway lists right now - one initialize,
    one tools/list, the session discarded afterwards.
    """

    initialize_params = {
        'protocolVersion': _protocol_version,
        'capabilities': {},
        'clientInfo': {'name': 'mcp-connections-harness', 'version': '1.0'},
    }

    initialize_body = _jsonrpc(mcp_url, auth, 'initialize', initialize_params, None)
    session_id = initialize_body['_session_id']

    list_body = _jsonrpc(mcp_url, auth, 'tools/list', {}, session_id)

    out = []

    for tool in list_body['result']['tools']:
        out.append(tool['name'])

    return out

# ################################################################################################################################

def wait_for_gateway_tool(mcp_url:'str', auth:'tupnone', tool_name:'str') -> 'None':
    """ Polls one gateway until its tool registry answers with the expected tool.
    """

    deadline = time.monotonic() + _gateway_ready_timeout
    last_error = ''

    while time.monotonic() < deadline:

        try:
            tool_names = get_tool_names(mcp_url, auth)

            if tool_name in tool_names:
                return

            last_error = f'tool `{tool_name}` not listed yet: {tool_names}'

        except Exception as e:
            last_error = str(e)

        time.sleep(_gateway_poll_interval)

    raise Exception(f'Gateway did not list `{tool_name}` within {_gateway_ready_timeout}s: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

def build_gateway_entry(
    name:'str',
    url_path:'str',
    security_group:'str',
    **allow_lists:'any_',
    ) -> 'stranydict':
    """ One mcp_gateway YAML entry with the given allow lists - services or any
    of the connection allow-list keys, e.g. rest_connections or sql_connections.
    """

    out:'stranydict' = {
        'name': name,
        'is_active': True,
        'url_path': url_path,
        'security_groups': [security_group],
    }

    out.update(allow_lists)

    return out

# ################################################################################################################################

def build_basic_auth_entry(name:'str', username:'str', password:'str') -> 'stranydict':
    """ One basic auth security definition YAML entry.
    """

    out:'stranydict' = {
        'name': name,
        'type': 'basic_auth',
        'username': username,
        'password': password,
    }

    return out

# ################################################################################################################################

def build_group_entry(name:'str', members:'strlist') -> 'stranydict':
    """ One security group YAML entry - the members are the names
    of the definitions the group holds.
    """

    out:'stranydict' = {
        'name': name,
        'members': members,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################
