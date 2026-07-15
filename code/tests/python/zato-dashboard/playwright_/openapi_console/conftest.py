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
import sys
import tempfile
import threading
import time
from http.client import FOUND, OK
from urllib.request import Request, urlopen

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.json_internal import dumps, loads
from zato.common.test.process_util import kill_process_tree

# The parent directory's helpers - the same lib the main Playwright conftest uses
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from cleanup_refs import cleanup_refs as _cleanup_refs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.test.playwright.openapi_console')

_Zato_Base = os.environ['ZATO_TEST_BASE_DIR']
_Zato_Bin  = os.path.join(_Zato_Base, 'code', 'bin', 'zato')
_Zato_Py   = os.path.join(_Zato_Base, 'code', 'bin', 'py')

_Password = 'test.dashboard.openapi.' + CryptoManager.generate_hex_string()

_Server_Wait_Timeout = 120
_Quickstart_Timeout  = 180
_Ping_Poll_Interval  = 0.5
_Kill_Timeout        = 5

# The auto-channel environment the server under test boots with - the include family is split
# across two variables on purpose, so the tests prove that all the family members are collected.
_Auto_Channel_Env = {
    'Zato_Auto_REST_Channel_Enabled': 'True',
    'Zato_Auto_REST_Channel_Include': \
        'api.test.openapi.typed.{operation}, api.test.openapi.untyped.{operation}; api.test.openapi.methods.{operation}',
    'Zato_Auto_REST_Channel_Include_01': \
        'api.test.openapi.prestarted.{operation}, api.test.openapi.excluded.{operation}, ' + \
        'api.test.openapi.diffing.{operation}',
    'Zato_Auto_REST_Channel_Exclude': 'api.test.openapi.excluded.{operation}',
    'Zato_Auto_REST_Channel_Active': 'api.test.openapi.prestarted.{operation}',
    'Zato_Auto_REST_Channel_Prefix': '/api/',
}

# The tests build on one another's environment state - the auto-created channels are asserted
# in their boot state first, then activated and secured one by one, and finally mutated
# by hot-deployments, which is why the modules must run in this exact order, never the alphabetical one.
_Module_Order = [
    'test_openapi_console_auto_create',
    'test_openapi_console_activation_access',
    'test_openapi_console_admin_view',
    'test_openapi_console_untyped_schema',
    'test_openapi_console_methods',
    'test_openapi_console_typed_schema',
    'test_openapi_console_signin_types',
    'test_openapi_console_recreate_after_delete',
    'test_openapi_console_contract_diffing',
]

# Every process spawned by the fixture registers here so the atexit hook below can kill
# them all even if Ctrl-C arrives in the middle of setup, before the fixture's own teardown runs.
_processes_to_kill:'list' = []

def _cleanup_at_exit() -> 'None':
    for process in _processes_to_kill:
        kill_process_tree(process)

_ = atexit.register(_cleanup_at_exit)

# ################################################################################################################################
# ################################################################################################################################

def _module_rank(item:'any_') -> 'int':
    """ Returns the position of a test item's module in the declared module order,
    with modules outside the list sorting after all the declared ones.
    """
    module_path = str(item.fspath)
    file_name = os.path.basename(module_path)
    module_name = os.path.splitext(file_name)[0]

    if module_name in _Module_Order:
        out = _Module_Order.index(module_name)
    else:
        out = len(_Module_Order)

    return out

# ################################################################################################################################

def pytest_collection_modifyitems(config:'any_', items:'anylist') -> 'None':
    """ Reorders this directory's tests to follow the suite's state buildup instead of the file name
    order, leaving the tests from all the other directories exactly where they were collected.
    """
    suite_dir = os.path.dirname(__file__)

    # Find this suite's items and remember where the first one was collected ..
    suite_items = []
    insert_at = 0

    for index, item in enumerate(items):
        item_dir = os.path.dirname(str(item.fspath))
        if item_dir == suite_dir:
            if not suite_items:
                insert_at = index
            suite_items.append(item)

    if not suite_items:
        return

    # .. sort them by the declared module order, keeping the in-module order stable ..
    suite_items.sort(key=_module_rank)

    # .. and put them back, as one block, where the first of them originally sat.
    remaining = []

    for item in items:
        if item not in suite_items:
            remaining.append(item)

    items[:] = remaining[:insert_at] + suite_items + remaining[insert_at:]

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to an ephemeral port and returns its number.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind(('127.0.0.1', 0))
        address = tcp_socket.getsockname()
        out = address[1]

    return out

# ################################################################################################################################

def _wait_for_tcp(port:'int') -> 'None':
    """ Polls a TCP port until it accepts connections, or raises after timeout.
    """
    deadline = time.monotonic() + _Server_Wait_Timeout

    while time.monotonic() < deadline:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                return
        except OSError:
            time.sleep(_Ping_Poll_Interval)

    raise Exception(f'Port {port} did not accept connections within {_Server_Wait_Timeout}s')

# ################################################################################################################################

def _wait_for_http(url:'str') -> 'None':
    """ Polls an HTTP endpoint until it returns 200 or 302, or raises after timeout.
    """
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

    raise Exception(f'{url} did not respond within {_Server_Wait_Timeout}s')

# ################################################################################################################################

def _stream_output(process:'any_', label:'str', time_reference:'float') -> 'None':
    """ Streams subprocess stdout to the test console with timing information.
    """
    for line in iter(process.stdout.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()
        elapsed = time.monotonic() - time_reference
        logger.info(f'[{label} {elapsed:6.1f}s] {text}')

# ################################################################################################################################

def _start_streaming(process:'any_', label:'str', time_reference:'float') -> 'None':
    """ Starts a daemon thread that streams a subprocess's output with the given label.
    """
    thread = threading.Thread(target=_stream_output, args=(process, label, time_reference), daemon=True)
    thread.start()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_dashboard() -> 'any_':
    """ Session-scoped fixture with a self-contained quickstart environment - server, dashboard,
    a dedicated Redis and the OpenAPI console process, with the server booted under
    the Zato_Auto_REST_Channel_* variables that drive auto-created channels.
    This overrides the fixture of the same name from the parent directory's conftest
    for the tests in this directory.
    """
    time_start = time.monotonic()

    server_port    = _find_free_port()
    dashboard_port = _find_free_port()
    broker_port    = _find_free_port()
    redis_port     = _find_free_port()
    console_port   = _find_free_port()

    temporary_dir = tempfile.mkdtemp(prefix='zato_playwright_openapi_console_test_')

    # The console and the server exchange messages over Redis Streams under this prefix -
    # both processes must read the same value, so it is computed once here.
    stream_prefix = 'zato:openapi:test:' + CryptoManager.generate_hex_string()

    # .. 0) start a dedicated Redis instance on its own port so the console streams never cross
    # paths with any other environment on this machine, and wait until it accepts connections ..

    redis_process = subprocess.Popen(
        ['redis-server', '--port', str(redis_port), '--save', '', '--appendonly', 'no'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    _processes_to_kill.append(redis_process)

    _wait_for_tcp(redis_port)
    logger.info(f'[TIMING] redis ready: {time.monotonic() - time_start:.1f}s')

    # .. 1) create a quickstart environment with both server and dashboard, pointing
    # it at our Redis so the server-side console listener connects there too ..

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
        raise Exception(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

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

    # .. 4) copy this suite's fixture services into the pickup directory so they deploy during
    # server boot and their auto channels are created by the startup pass, with no hot-deployment wait ..

    fixtures_services_dir = os.path.join(os.path.dirname(__file__), 'fixtures', 'services')
    pickup_services_dir = os.path.join(server_dir, 'pickup', 'incoming', 'services')

    os.makedirs(pickup_services_dir, exist_ok=True)

    for file_name in os.listdir(fixtures_services_dir):
        if file_name.endswith('.py'):
            source_path = os.path.join(fixtures_services_dir, file_name)
            _ = shutil.copy(source_path, pickup_services_dir)
            logger.info('[FIXTURES] copied %s to %s', file_name, pickup_services_dir)

    # .. 5) start the server with the auto-channel and console stream environment ..

    server_env = os.environ.copy()
    server_env['Zato_Config_Bind_Port'] = str(server_port)
    server_env['Zato_Broker_HTTP_Port'] = str(broker_port)

    # The queue bridge listeners must use this session's dedicated Redis too - otherwise they poll
    # the shared default one, where any other session's quickstart create wipes the zato:* keys.
    server_env['Zato_Queue_Bridge_Redis_Port'] = str(redis_port)

    server_env['Zato_OpenAPI_Stream_Prefix'] = stream_prefix
    server_env.update(_Auto_Channel_Env)
    server_env.pop('COVERAGE_PROCESS_START', None)

    server_process = subprocess.Popen(
        [_Zato_Bin, 'start', server_dir, '--fg'],
        env=server_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    _processes_to_kill.append(server_process)

    time_after_server_start = time.monotonic()
    _start_streaming(server_process, 'SERVER', time_after_server_start)

    # .. 6) start the dashboard ..

    dashboard_env = os.environ.copy()
    dashboard_env.pop('COVERAGE_PROCESS_START', None)
    dashboard_env['Zato_Server_Address'] = f'http://127.0.0.1:{server_port}'
    dashboard_env['Zato_Server_Dir'] = server_dir

    dashboard_process = subprocess.Popen(
        [_Zato_Bin, 'start', dashboard_dir, '--fg'],
        env=dashboard_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    _processes_to_kill.append(dashboard_process)

    _start_streaming(dashboard_process, 'DASHBOARD', time_after_server_start)

    # .. 7) start the OpenAPI console, pointing it at the same Redis and stream prefix as the server ..

    console_env = os.environ.copy()
    console_env.pop('COVERAGE_PROCESS_START', None)
    console_env['Zato_OpenAPI_Console_Host'] = '127.0.0.1'
    console_env['Zato_OpenAPI_Console_Port'] = str(console_port)
    console_env['Zato_OpenAPI_Redis_Host'] = '127.0.0.1'
    console_env['Zato_OpenAPI_Redis_Port'] = str(redis_port)
    console_env['Zato_OpenAPI_Stream_Prefix'] = stream_prefix

    console_process = subprocess.Popen(
        [_Zato_Py, '-m', 'zato.openapi.app.run'],
        env=console_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    _processes_to_kill.append(console_process)

    _start_streaming(console_process, 'CONSOLE', time_after_server_start)

    # .. 8) wait for everything to be ready ..

    host = '127.0.0.1'

    try:
        _wait_for_http(f'http://{host}:{server_port}/zato/ping')
        logger.info(f'[TIMING] server ready: {time.monotonic() - time_after_server_start:.1f}s')

        _wait_for_http(f'http://{host}:{dashboard_port}/accounts/login/')
        logger.info(f'[TIMING] dashboard ready: {time.monotonic() - time_after_server_start:.1f}s')

        _wait_for_http(f'http://{host}:{console_port}/openapi/console/login')
        logger.info(f'[TIMING] console ready: {time.monotonic() - time_after_server_start:.1f}s')

    except Exception:
        logger.error('Components did not become ready, stdout was streamed above')
        kill_process_tree(server_process)
        kill_process_tree(dashboard_process)
        kill_process_tree(console_process)
        kill_process_tree(redis_process)
        raise

    # .. 9) start the file pickup listener so hot-deployments through the pickup directory work ..

    listener_env = os.environ.copy()
    listener_env['Zato_Config_Bind_Port'] = str(server_port)
    listener_env['Zato_Web_Admin_Repo_Dir'] = os.path.join(dashboard_dir, 'config', 'repo')
    listener_env['Zato_Server_Dir'] = server_dir
    listener_env.pop('COVERAGE_PROCESS_START', None)

    listener_process = subprocess.Popen(
        ['make', 'listener'],
        cwd=_Zato_Base,
        env=listener_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    _processes_to_kill.append(listener_process)

    _start_streaming(listener_process, 'LISTENER', time_after_server_start)

    yield {
        'host': host,
        'server_port': server_port,
        'dashboard_port': dashboard_port,
        'dashboard_url': f'http://{host}:{dashboard_port}',
        'console_port': console_port,
        'console_url': f'http://{host}:{console_port}',
        'password': _Password,
        'server_dir': server_dir,
        'dashboard_dir': dashboard_dir,
        'temporary_dir': temporary_dir,
        'server_process': server_process,
        'dashboard_process': dashboard_process,
        'console_process': console_process,
        'listener_process': listener_process,
        'redis_process': redis_process,
        'redis_port': redis_port,
    }

    # .. teardown: stop everything ..
    kill_process_tree(listener_process)
    kill_process_tree(console_process)
    kill_process_tree(server_process)
    kill_process_tree(dashboard_process)
    kill_process_tree(redis_process)

    # .. and remove the temporary directory only if all tests passed.
    if _cleanup_refs.get('has_failures'):
        logger.info('[TEARDOWN] Keeping temporary directory for debugging: %s', temporary_dir)
    elif os.path.isdir(temporary_dir):
        shutil.rmtree(temporary_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################
