# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import dumps, loads

# The parent directory's helpers - the same lib the main Playwright conftest uses
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.playwright.declarative')

_Zato_Base = os.environ['ZATO_TEST_BASE_DIR']
_Zato_Bin  = os.path.join(_Zato_Base, 'code', 'bin', 'zato')

_Password = 'test.dashboard.declarative.' + CryptoManager.generate_hex_string()

_Server_Wait_Timeout = 120
_Quickstart_Timeout  = 180
_Ping_Poll_Interval  = 0.5
_Kill_Timeout        = 5

# The scheduler's HTTP query API always binds on this fixed port
_Scheduler_API_Port = 35100

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to an ephemeral port and returns its number.
    """
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        out = tcp_socket.getsockname()[1]

    return out

# ################################################################################################################################

def _kill_process(process:'any_') -> 'None':
    """ Terminates a subprocess, escalating to kill if it does not exit in time.
    """
    if process and process.poll() is None:
        process.terminate()
        try:
            _ = process.wait(timeout=_Kill_Timeout)
        except subprocess.TimeoutExpired:
            process.kill()

# ################################################################################################################################

def _wait_for_tcp(port:'int') -> 'None':
    """ Polls a TCP port until it accepts connections, or raises after timeout.
    """
    import socket

    deadline = time.monotonic() + _Server_Wait_Timeout

    while time.monotonic() < deadline:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                return
        except OSError:
            time.sleep(_Ping_Poll_Interval)

    raise RuntimeError(f'Port {port} did not accept connections within {_Server_Wait_Timeout}s')

# ################################################################################################################################

def _wait_for_http(url:'str') -> 'None':
    """ Polls an HTTP endpoint until it returns 200 or 302, or raises after timeout.
    """
    from http.client import FOUND, OK
    from urllib.request import Request, urlopen

    deadline = time.monotonic() + _Server_Wait_Timeout

    while time.monotonic() < deadline:
        try:
            request = Request(url, method='GET')
            with urlopen(request, timeout=_Kill_Timeout) as response:
                if response.status in (OK, FOUND):
                    return
        except Exception:
            pass

        time.sleep(_Ping_Poll_Interval)

    raise RuntimeError(f'{url} did not respond within {_Server_Wait_Timeout}s')

# ################################################################################################################################

def _stream_output(process:'any_', label:'str', time_reference:'float') -> 'None':
    """ Streams subprocess stdout to the test console with timing information.
    """
    for line in iter(process.stdout.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()
        elapsed = time.monotonic() - time_reference
        logger.debug(f'[{label} {elapsed:6.1f}s] {text}')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_dashboard() -> 'any_':
    """ Session-scoped fixture with a self-contained quickstart environment - server, dashboard,
    a dedicated Redis and the Rust scheduler binary, so scheduled jobs really fire during tests.
    This overrides the fixture of the same name from the parent directory's conftest
    for the tests in this directory.
    """
    time_start = time.monotonic()

    server_port    = _find_free_port()
    dashboard_port = _find_free_port()
    broker_port    = _find_free_port()
    redis_port     = _find_free_port()

    temporary_dir = tempfile.mkdtemp(prefix='zato_playwright_declarative_test_')

    # .. 0) start a dedicated Redis instance on its own port so tests never share
    # scheduler streams with any other environment on this machine, and wait until
    # it accepts connections - the scheduler binary exits if Redis is not up yet ..

    redis_process = subprocess.Popen(
        ['redis-server', '--port', str(redis_port), '--save', '', '--appendonly', 'no'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    _wait_for_tcp(redis_port)
    logger.info(f'[TIMING] redis ready: {time.monotonic() - time_start:.1f}s')

    # All components that talk to the scheduler's Redis get these variables
    scheduler_redis_env = {
        'Zato_Scheduler_Redis_Host': '127.0.0.1',
        'Zato_Scheduler_Redis_Port': str(redis_port),
    }

    # .. 1) create a quickstart environment with both server and dashboard, pointing
    # it at our Redis so it wipes the scheduler keys there and not anywhere else ..

    quickstart_env = os.environ.copy()
    quickstart_env.pop('COVERAGE_PROCESS_START', None)

    quickstart_command = [
        _Zato_Bin, 'quickstart', 'create', temporary_dir,
        '--servers', '1',
        '--password', _Password,
        '--server-api-client-for-scheduler-password', _Password,
        '--no-scheduler',
        '--redis-host', '127.0.0.1',
        '--redis-port', str(redis_port),
    ]

    result = subprocess.run(quickstart_command, capture_output=True, text=True,
        timeout=_Quickstart_Timeout, env=quickstart_env)

    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    logger.info(f'[TIMING] quickstart create: {time.monotonic() - time_start:.1f}s')

    # .. 2) patch server.conf to bind on our dynamic port ..

    server_dir = os.path.join(temporary_dir, 'server1')
    server_config_path = os.path.join(server_dir, 'config', 'repo', 'server.conf')

    with open(server_config_path, 'r') as server_config_file:
        server_config_content = server_config_file.read()

    server_config_content = re.sub(
        r'^(bind\s*=\s*)\S+',
        f'\\g<1>0.0.0.0:{server_port}',
        server_config_content,
        flags=re.MULTILINE,
    )

    with open(server_config_path, 'w') as server_config_file:
        _ = server_config_file.write(server_config_content)

    # .. 3) patch web-admin.conf to use our dashboard port ..

    dashboard_dir = os.path.join(temporary_dir, 'web-admin')
    dashboard_config_path = os.path.join(dashboard_dir, 'config', 'repo', 'web-admin.conf')

    with open(dashboard_config_path, 'r') as config_file:
        dashboard_config = loads(config_file.read())

    dashboard_config['host'] = '127.0.0.1'
    dashboard_config['port'] = dashboard_port

    with open(dashboard_config_path, 'w') as config_file:
        _ = config_file.write(dumps(dashboard_config))

    # .. 3b) copy fixture services into the pickup directory so they deploy during
    # server boot, with no hot-deployment wait ..

    fixtures_services_dir = os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'services')
    pickup_services_dir = os.path.join(server_dir, 'pickup', 'incoming', 'services')

    os.makedirs(pickup_services_dir, exist_ok=True)
    for file_name in os.listdir(fixtures_services_dir):
        if file_name.endswith('.py'):
            source_path = os.path.join(fixtures_services_dir, file_name)
            _ = shutil.copy(source_path, pickup_services_dir)

    # .. 4) start the server, pointing it at the scheduler's Redis ..

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(server_port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)
    server_env.update(scheduler_redis_env)
    server_env.pop('COVERAGE_PROCESS_START', None)

    server_process = subprocess.Popen(
        [_Zato_Bin, 'start', server_dir, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    time_after_server_start = time.monotonic()

    server_thread = threading.Thread(
        target=_stream_output, args=(server_process, 'SERVER', time_after_server_start), daemon=True)
    server_thread.start()

    # .. 4b) start the Rust scheduler binary against that Redis - the server talks to it
    # over Redis Streams, which is how scheduled jobs really fire during tests. Redis is
    # already up and its keys were wiped by quickstart, so the start order is safe ..

    scheduler_binary = os.path.join(_Zato_Base, 'code', 'bin', '_zato_scheduler')

    scheduler_env = os.environ.copy()
    scheduler_env.update(scheduler_redis_env)

    scheduler_process = subprocess.Popen(
        [scheduler_binary],
        env=scheduler_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    scheduler_thread = threading.Thread(
        target=_stream_output, args=(scheduler_process, 'SCHEDULER', time_after_server_start), daemon=True)
    scheduler_thread.start()

    # .. 5) start the dashboard ..

    dashboard_env = os.environ.copy()
    dashboard_env.pop('COVERAGE_PROCESS_START', None)
    dashboard_env['Zato_Server_Address'] = f'http://127.0.0.1:{server_port}'
    dashboard_env['Zato_Server_Dir'] = server_dir

    dashboard_process = subprocess.Popen(
        [_Zato_Bin, 'start', dashboard_dir, '--fg'],
        env=dashboard_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    dashboard_thread = threading.Thread(
        target=_stream_output, args=(dashboard_process, 'DASHBOARD', time_after_server_start), daemon=True)
    dashboard_thread.start()

    # .. 6) wait for everything to be ready ..

    host = '127.0.0.1'

    try:
        _wait_for_http(f'http://{host}:{server_port}/zato/ping')
        logger.info(f'[TIMING] server ready: {time.monotonic() - time_after_server_start:.1f}s')

        # The scheduler binds its HTTP query API only once it has received the initial
        # job reload from the server, so this wait must follow the server's.
        _wait_for_http(f'http://{host}:{_Scheduler_API_Port}/api/get_job_summaries')
        logger.info(f'[TIMING] scheduler ready: {time.monotonic() - time_after_server_start:.1f}s')

        _wait_for_http(f'http://{host}:{dashboard_port}/accounts/login/')
        logger.info(f'[TIMING] dashboard ready: {time.monotonic() - time_after_server_start:.1f}s')

    except Exception:
        logger.error('Components did not become ready')
        _kill_process(server_process)
        _kill_process(dashboard_process)
        _kill_process(scheduler_process)
        _kill_process(redis_process)
        raise

    yield {
        'host': host,
        'server_port': server_port,
        'dashboard_port': dashboard_port,
        'dashboard_url': f'http://{host}:{dashboard_port}',
        'password': _Password,
        'server_dir': server_dir,
        'dashboard_dir': dashboard_dir,
        'temporary_dir': temporary_dir,
        'server_process': server_process,
        'dashboard_process': dashboard_process,
        'scheduler_process': scheduler_process,
        'redis_process': redis_process,
        'redis_port': redis_port,
    }

    # .. teardown: stop everything and remove the environment.
    _kill_process(scheduler_process)
    _kill_process(server_process)
    _kill_process(dashboard_process)
    _kill_process(redis_process)

    shutil.rmtree(temporary_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
