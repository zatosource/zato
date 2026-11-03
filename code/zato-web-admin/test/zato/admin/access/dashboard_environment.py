# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import time
from dataclasses import dataclass
from http.client import FOUND, OK
from urllib.request import Request, urlopen

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.process_util import kill_process_tree

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

# The zato command of this installation, five directories above this one
_Code_Dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
_Zato_Bin = os.path.join(_Code_Dir, 'bin', 'zato')

_Host = '127.0.0.1'

_Quickstart_Timeout = 120
_Ready_Timeout      = 60
_Poll_Interval      = 0.5
_Request_Timeout    = 5

# How much of a component's log is quoted when it does not become ready
_Log_Tail_Size = 4000

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Environment:
    """ A quickstart environment with its own server and dashboard on ports the operating system assigned.
    """
    temporary_dir: 'str'
    dashboard_dir: 'str'
    dashboard_address: 'str'
    processes: 'anylist'

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to an ephemeral port and returns its number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind((_Host, 0))
        address = tcp_socket.getsockname()

    out = address[1]
    return out

# ################################################################################################################################

def _start_process(command:'anylist', env:'any_', log_path:'str', cwd:'str | None'=None) -> 'any_':
    """ Starts a process in its own session, so that its whole tree can be stopped, with its output in a file.
    """
    log_file = open(log_path, 'wb')

    out = subprocess.Popen(
        command,
        env=env,
        cwd=cwd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    return out

# ################################################################################################################################

def _read_log_tail(log_path:'str') -> 'str':
    """ Returns the end of a component's log, for the message of a component that did not become ready.
    """
    with open(log_path, 'rb') as log_file:
        data = log_file.read()

    data = data[-_Log_Tail_Size:]

    out = data.decode('utf-8', errors='replace')
    return out

# ################################################################################################################################

def _wait_for_tcp_port(port:'int') -> 'None':
    """ Polls a TCP port until it accepts connections.
    """
    deadline = time.monotonic() + _Ready_Timeout

    while time.monotonic() < deadline:
        try:
            with socket.create_connection((_Host, port), timeout=1):
                return
        except OSError:
            time.sleep(_Poll_Interval)

    raise Exception(f'Port {port} did not accept connections within {_Ready_Timeout}s')

# ################################################################################################################################

def _wait_for_http(port:'int', path:'str', log_path:'str') -> 'None':
    """ Polls an HTTP endpoint until it answers with OK or a redirect.
    """
    url = f'http://{_Host}:{port}{path}'
    deadline = time.monotonic() + _Ready_Timeout

    while time.monotonic() < deadline:
        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=_Request_Timeout) as response:
                if response.status in (OK, FOUND):
                    return
        except Exception:
            pass

        time.sleep(_Poll_Interval)

    log_tail = _read_log_tail(log_path)
    raise Exception(f'{url} did not respond within {_Ready_Timeout}s, the log ends with:\n{log_tail}')

# ################################################################################################################################

def _create_quickstart(temporary_dir:'str', password:'str') -> 'None':
    """ Creates a quickstart environment with a server and a dashboard in the given directory.
    """
    env = os.environ.copy()
    _ = env.pop('COVERAGE_PROCESS_START', None)

    command = [
        _Zato_Bin, 'quickstart', 'create', temporary_dir,
        '--password', password,
        '--server-api-client-for-scheduler-password', password,
        '--no-scheduler',
    ]

    result = subprocess.run(command, capture_output=True, text=True, timeout=_Quickstart_Timeout, env=env)

    if result.returncode != 0:
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

# ################################################################################################################################

def _set_server_port(server_dir:'str', server_port:'int') -> 'None':
    """ Points the bind address of the server at its assigned port.
    """
    config_path = os.path.join(server_dir, 'config', 'repo', 'server.conf')

    with open(config_path, 'r') as config_file:
        config = config_file.read()

    config = re.sub(r'^(bind\s*=\s*)\S+', f'\\g<1>0.0.0.0:{server_port}', config, flags=re.MULTILINE)

    with open(config_path, 'w') as config_file:
        _ = config_file.write(config)

# ################################################################################################################################

def _set_dashboard_port(dashboard_dir:'str', dashboard_port:'int') -> 'None':
    """ Points the dashboard at its assigned port.
    """
    config_path = os.path.join(dashboard_dir, 'config', 'repo', 'web-admin.conf')

    with open(config_path, 'r') as config_file:
        config = json.loads(config_file.read())

    config['host'] = _Host
    config['port'] = dashboard_port

    with open(config_path, 'w') as config_file:
        _ = config_file.write(json.dumps(config))

# ################################################################################################################################

def start_environment() -> 'Environment':
    """ Creates a quickstart environment in a temporary directory and starts its server and dashboard,
    each on a port the operating system assigned, along with a Redis of its own for the queue bridge,
    so that nothing else running on this machine is used or affected.
    """
    out = Environment()
    out.processes = []

    out.temporary_dir = tempfile.mkdtemp(prefix='zato_dashboard_access_test_')

    server_dir = os.path.join(out.temporary_dir, 'server1')
    out.dashboard_dir = os.path.join(out.temporary_dir, 'web-admin')

    server_port = _find_free_port()
    dashboard_port = _find_free_port()
    broker_port = _find_free_port()
    mllp_port = _find_free_port()
    redis_port = _find_free_port()

    password = 'test.dashboard.' + CryptoManager.generate_hex_string()

    try:

        # The queue bridge of the server uses a Redis of its own ..
        redis_log_path = os.path.join(out.temporary_dir, 'redis.log')
        redis_command = ['redis-server', '--port', str(redis_port), '--save', '', '--appendonly', 'no']

        redis_process = _start_process(redis_command, os.environ.copy(), redis_log_path)
        out.processes.append(redis_process)

        _wait_for_tcp_port(redis_port)

        # .. the environment is created and pointed at its ports ..
        _create_quickstart(out.temporary_dir, password)
        _set_server_port(server_dir, server_port)
        _set_dashboard_port(out.dashboard_dir, dashboard_port)

        # .. the server is started ..
        server_env = os.environ.copy()
        _ = server_env.pop('COVERAGE_PROCESS_START', None)

        server_env['Zato_Config_Bind_Port'] = str(server_port)
        server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
        server_env['Zato_Queue_Bridge_Redis_Port'] = str(redis_port)
        server_env['Zato_HL7_MLLP_Port'] = str(mllp_port)
        server_env['Zato_PubSub_DB_Path'] = os.path.join(server_dir, 'pubsub.db')

        server_log_path = os.path.join(out.temporary_dir, 'server.log')
        server_process = _start_process([_Zato_Bin, 'start', server_dir, '--fg'], server_env, server_log_path)
        out.processes.append(server_process)

        # .. the dashboard is started against that server ..
        dashboard_env = os.environ.copy()
        _ = dashboard_env.pop('COVERAGE_PROCESS_START', None)

        dashboard_env['Zato_Server_Address'] = f'http://{_Host}:{server_port}'

        dashboard_log_path = os.path.join(out.temporary_dir, 'dashboard.log')
        dashboard_command = [_Zato_Bin, 'start', out.dashboard_dir, '--fg']

        dashboard_process = _start_process(dashboard_command, dashboard_env, dashboard_log_path)
        out.processes.append(dashboard_process)

        # .. and both are waited for.
        _wait_for_http(server_port, '/zato/ping', server_log_path)
        _wait_for_http(dashboard_port, '/accounts/login/', dashboard_log_path)

    except Exception:
        stop_environment(out)
        raise

    out.dashboard_address = f'http://{_Host}:{dashboard_port}'
    return out

# ################################################################################################################################

def stop_environment(environment:'Environment') -> 'None':
    """ Stops every process of the environment and removes its directory.
    """
    for process in reversed(environment.processes):
        kill_process_tree(process)

    shutil.rmtree(environment.temporary_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
