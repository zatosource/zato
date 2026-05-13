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

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

_ZATO_BASE = '/home/dsuch/projects/zatosource-zato/4.1'
_ZATO_BIN = os.path.join(_ZATO_BASE, 'code', 'bin', 'zato')

_PASSWORD = 'test.invoke.' + os.urandom(8).hex()

_ENMASSE_PATH = os.path.join(
    _ZATO_BASE, 'code', 'zato-server', 'src', 'zato', 'server', 'service', 'internal', 'pubsub', 'enmasse.yaml')

_server_proc = None
_tmpdir = None

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]

# ################################################################################################################################
# ################################################################################################################################

def _kill_server() -> 'None':
    global _server_proc
    if _server_proc and _server_proc.poll() is None:
        _server_proc.terminate()
        try:
            _server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _server_proc.kill()
            _server_proc.wait(timeout=5)
    _server_proc = None

# ################################################################################################################################
# ################################################################################################################################

def _cleanup() -> 'None':
    _kill_server()
    global _tmpdir
    if _tmpdir and os.path.isdir(_tmpdir):
        shutil.rmtree(_tmpdir, ignore_errors=True)
    _tmpdir = None

atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'str', port:'int', timeout:'int'=60) -> 'None':
    from urllib.request import Request, urlopen

    url = f'http://{host}:{port}/zato/ping'
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            req = Request(url, method='GET')
            with urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.5)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def zato_server() -> 'None':
    global _server_proc, _tmpdir

    from config import TestConfig

    port = _find_free_port()
    _tmpdir = tempfile.mkdtemp(prefix='zato_pubsub_test_')

    # .. quickstart create
    qs_env = os.environ.copy()
    qs_env.pop('COVERAGE_PROCESS_START', None)

    qs_cmd = [
        _ZATO_BIN, 'quickstart', 'create', _tmpdir,
        '--force',
        '--password', _PASSWORD,
        '--servers', '1',
        '--server-api-client-for-scheduler-password', _PASSWORD,
        '--no-scheduler',
    ]
    result = subprocess.run(qs_cmd, capture_output=True, text=True, timeout=180, env=qs_env)
    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    server_dir = os.path.join(_tmpdir, 'server1')

    # .. import the existing enmasse YAML with test users, topics and permissions.
    # The enmasse command may return non-zero because it tries to reload_config
    # on a running server, but no server is running yet. The ODB import itself
    # succeeds and the server will read from the ODB on startup.
    _ = subprocess.run(
        [_ZATO_BIN, 'enmasse', server_dir, '--verbose', '--import', '--input', _ENMASSE_PATH],
        capture_output=True, text=True, timeout=60, env=qs_env,
    )

    # .. start the server in foreground mode
    broker_port = _find_free_port()

    env = os.environ.copy()
    env['Zato_Config_Bind_Port'] = str(port)
    env['Zato_Broker_HTTP_Port'] = str(broker_port)
    env.pop('COVERAGE_PROCESS_START', None)

    _server_proc = subprocess.Popen(
        [_ZATO_BIN, 'start', server_dir, '--fg'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    start_time = time.monotonic()
    server_output_lines = []

    def _capture_server_output() -> 'None':
        for line in iter(_server_proc.stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - start_time
            server_output_lines.append(f'[SERVER {elapsed:6.1f}s] {text}')

    stdout_thread = threading.Thread(target=_capture_server_output, daemon=True)
    stdout_thread.start()

    host = '127.0.0.1'
    try:
        _wait_for_server(host, port)
    except Exception:
        print('\n--- Server did not become ready, captured output: ---')
        for line in server_output_lines:
            print(line)
        print('--- End of server output ---\n')
        _kill_server()
        raise

    # .. update the config so tests use the dynamically allocated port
    TestConfig.base_url = f'http://{host}:{port}'

    yield

    _kill_server()

    if _tmpdir and os.path.isdir(_tmpdir):
        shutil.rmtree(_tmpdir, ignore_errors=True)
    _tmpdir = None

# ################################################################################################################################
# ################################################################################################################################
