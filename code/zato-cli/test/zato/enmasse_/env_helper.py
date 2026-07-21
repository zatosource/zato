# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import os
import socket
import subprocess
import tempfile
import time
from shutil import rmtree
from typing import NamedTuple

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.test.process_util import kill_process_tree

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The zato binary of the checkout the tests run from
_zato_base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_zato_bin = os.path.join(_zato_base, 'bin', 'zato')

# The Python binary and the file listener that deploys files dropped into the pickup directory
_python_bin = os.path.join(_zato_base, 'bin', 'python')
_listener_path = os.path.join(_zato_base, 'zato-common', 'src', 'zato', 'common', 'file_transfer', 'listener.py')

# How long quickstart create may take, in seconds
_create_timeout = 120

# How long the server may take to start responding, in seconds
_server_start_timeout = 120

# ################################################################################################################################
# ################################################################################################################################

class TestEnvironment(NamedTuple):
    base_dir: str
    server_dir: str
    server_process: 'any_' = None
    listener_process: 'any_' = None

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('127.0.0.1', 0))
        out = server_socket.getsockname()[1]

    return out

# ################################################################################################################################

def _wait_for_server(port:'int', password:'str') -> 'None':
    """ Waits until the server responds to demo.ping, which also means its internal
    and demo services have been deployed into the environment's database.
    """
    # stdlib
    from base64 import b64encode
    from urllib.request import Request, urlopen

    credentials = b64encode(f'admin.invoke:{password}'.encode()).decode()
    url = f'http://127.0.0.1:{port}/zato/api/invoke/demo.ping'
    deadline = time.monotonic() + _server_start_timeout

    while time.monotonic() < deadline:
        try:
            request = Request(url, method='GET')
            request.add_header('Authorization', f'Basic {credentials}')
            with urlopen(request, timeout=5) as response:
                if response.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.5)

    raise Exception(f'Server at 127.0.0.1:{port} did not respond within {_server_start_timeout}s')

# ################################################################################################################################

def _start_server(base_dir:'str', server_dir:'str', password:'str') -> 'tuple':
    """ Starts the environment's server along with the file listener watching its pickup directory.
    """
    # Zato
    from zato.common.util.config import get_config_object, update_config_file

    port = _find_free_port()
    broker_port = _find_free_port()

    # Point the server at the port chosen for it ..
    repo_location = os.path.join(server_dir, 'config', 'repo')
    config = get_config_object(repo_location, 'server.conf')
    config['main']['port'] = str(port)
    config['main']['bind'] = f'0.0.0.0:{port}'
    update_config_file(config, repo_location, 'server.conf')

    # .. build the server's environment ..
    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env.pop('COVERAGE_PROCESS_START', None)

    # .. start the server in its own process group so the whole tree can be stopped later ..
    server_process = subprocess.Popen(
        [_zato_bin, 'start', server_dir, '--fg'],
        env=server_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    # .. wait until it is ready, which also populates the database with services ..
    try:
        _wait_for_server(port, password)
    except Exception:
        kill_process_tree(server_process)
        raise

    # .. start the file listener watching the server's pickup directory ..
    pickup_dir = os.path.join(server_dir, 'pickup', 'incoming', 'services')
    web_admin_repo = os.path.join(base_dir, 'web-admin', 'config', 'repo')

    listener_env = os.environ.copy()
    listener_env['Zato_Config_Bind_Port'] = str(port)
    listener_env['Zato_Web_Admin_Repo_Dir'] = web_admin_repo
    listener_env.pop('COVERAGE_PROCESS_START', None)

    listener_process = subprocess.Popen(
        [_python_bin, _listener_path, pickup_dir],
        env=listener_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    # .. and hand both processes back to the caller.
    out = server_process, listener_process

    return out

# ################################################################################################################################

def create_environment(prefix:'str', needs_server:'bool'=False) -> 'TestEnvironment':
    """ Creates a throwaway quickstart environment so tests never depend on any pre-existing one.
    With needs_server, the environment's server and file listener are started too, which deploys
    all the internal and demo services into the environment's database.
    """
    base_dir = tempfile.mkdtemp(prefix=prefix)
    password = 'test.enmasse.' + CryptoManager.generate_hex_string()

    command = [
        _zato_bin, 'quickstart', 'create', base_dir,
        '--servers', '1',
        '--no-scheduler',
        '--server-api-client-for-scheduler-password', password,
    ]

    create_env = os.environ.copy()
    create_env.pop('COVERAGE_PROCESS_START', None)

    result = subprocess.run(command, capture_output=True, text=True, timeout=_create_timeout, env=create_env)
    if result.returncode != 0:
        rmtree(base_dir, ignore_errors=True)
        raise Exception(f'quickstart create failed:\n{result.stdout}\n{result.stderr}')

    server_dir = os.path.join(base_dir, 'server1')

    server_process = None
    listener_process = None

    # Start the server and the listener if the caller needs the environment's database
    # to contain all the services a running server deploys.
    if needs_server:
        try:
            server_process, listener_process = _start_server(base_dir, server_dir, password)
        except Exception:
            rmtree(base_dir, ignore_errors=True)
            raise

    out = TestEnvironment(
        base_dir=base_dir,
        server_dir=server_dir,
        server_process=server_process,
        listener_process=listener_process,
    )
    return out

# ################################################################################################################################

def delete_environment(environment:'TestEnvironment') -> 'None':
    """ Stops the environment's processes, if any, and removes it along with its embedded ODB.
    """
    kill_process_tree(environment.listener_process)
    kill_process_tree(environment.server_process)
    rmtree(environment.base_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

# The environment shared by all the tests in a single test process
_shared_environment:'TestEnvironment | None' = None

# ################################################################################################################################

def get_shared_environment() -> 'TestEnvironment':
    """ Returns a process-wide throwaway environment, creating it on first use and deleting it when the process exits.
    """
    global _shared_environment

    if _shared_environment is None:
        _shared_environment = create_environment('zato-enmasse-shared-', needs_server=True)
        _ = atexit.register(delete_environment, _shared_environment)

    return _shared_environment

# ################################################################################################################################
# ################################################################################################################################
