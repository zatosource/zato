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
import sys
import tempfile
import time
import shutil

# This directory must stay first so `import conftest` in test modules resolves to this very file,
# not to the conftest of the config_store suite added below.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'zato-server', 'config_store'))
sys.path.insert(0, os.path.dirname(__file__))

# Pytest imports this file under a package-qualified name, while test modules do `import conftest`.
# Alias this very module instance under that plain name so both refer to the same object
# and the service files test modules register below are seen by the zato_server fixture.
sys.modules['conftest'] = sys.modules[__name__]

# PyPI
import pytest

# Zato
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.crypto.api import CryptoManager
from zato.common.test.process_util import kill_process_tree
from zato.common.util.config import get_config_object, update_config_file
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

def pytest_addoption(parser:'any_'):
    parser.addoption('--with-coverage', action='store_true', default=False,
                     help='Enable coverage collection on the Zato server subprocess')

_ZATO_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_ZATO_BIN = os.path.join(_ZATO_BASE, 'code', 'bin', 'zato')
_ZATO_PY = os.path.join(_ZATO_BASE, 'code', 'bin', 'python')

_PASSWORD = 'test.invoke.' + CryptoManager.generate_hex_string()

# A per-session Redis stream prefix so the server and scheduler started here never exchange
# fire events or commands with any other Zato environment sharing the same Redis instance.
_STREAM_PREFIX = 'zato:scheduler:test-' + CryptoManager.generate_hex_string()

_REPORTS_DIR = os.path.join(_ZATO_BASE, 'code', 'tests', 'python', 'zato-scheduler', 'reports')

_COVERAGE_SOURCE = os.path.join(
    _ZATO_BASE, 'code', 'zato-server', 'src', 'zato', 'server', 'service', 'internal')

_server_proc = None
_scheduler_proc = None
_tmpdir = None
_pre_start_service_files = []

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

# ################################################################################################################################
# ################################################################################################################################

def _kill_server():
    global _server_proc
    kill_process_tree(_server_proc)
    _server_proc = None

# ################################################################################################################################
# ################################################################################################################################

def _find_scheduler_binary():
    """ Locates the Rust scheduler binary, preferring the release build.
    """
    candidates = [
        os.path.join(_ZATO_BASE, 'code', 'zato-rust', 'zato_scheduler_core', 'target', 'release', '_zato_scheduler'),
        os.path.join(_ZATO_BASE, 'code', 'zato-rust', 'zato_scheduler_core', 'target', 'debug', '_zato_scheduler'),
    ]

    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    raise RuntimeError('Could not find the Rust scheduler binary, looked in: {}'.format(', '.join(candidates)))

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_scheduler_api(port:'any_', timeout:'any_' = 30):
    """ Polls the scheduler's HTTP query API until it answers, proving the scheduler
    completed its initial job reload handshake with the server.
    """
    from urllib.request import urlopen

    url = f'http://127.0.0.1:{port}/metrics'
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=5) as response:
                if response.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.5)

    raise RuntimeError(f'Scheduler HTTP API at {url} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _kill_scheduler():
    global _scheduler_proc
    kill_process_tree(_scheduler_proc)
    _scheduler_proc = None

# ################################################################################################################################
# ################################################################################################################################

def _delete_stream_keys():
    """ Removes this session's namespaced scheduler streams from Redis so they do not accumulate across sessions.
    """
    from redis import Redis

    redis_conn = Redis(host='localhost', port=6379, decode_responses=True)

    try:
        keys = cast_('anylist', redis_conn.keys(_STREAM_PREFIX + ':stream:*'))
        if keys:
            _ = redis_conn.delete(*keys)
    except Exception:
        pass

# ################################################################################################################################
# ################################################################################################################################

def _cleanup():
    _kill_server()
    _kill_scheduler()
    _delete_stream_keys()
    global _tmpdir
    if _tmpdir and os.path.isdir(_tmpdir):
        shutil.rmtree(_tmpdir, ignore_errors=True)
    _tmpdir = None

_ = atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host:'any_', port:'any_', password:'any_', timeout:'any_' = 60):
    from base64 import b64encode
    from urllib.request import Request, urlopen

    creds = b64encode(f'admin.invoke:{password}'.encode()).decode()
    url = f'http://{host}:{port}/zato/api/invoke/demo.ping'
    t0 = time.monotonic()
    deadline = t0 + timeout
    attempt = 0

    while time.monotonic() < deadline:
        attempt += 1
        try:
            req = Request(url, method='GET')
            req.add_header('Authorization', f'Basic {creds}')
            with urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.5)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _setup_coverage(tmpdir:'any_'):
    cov_data_dir = os.path.join(tmpdir, 'coverage')
    os.makedirs(cov_data_dir, exist_ok=True)

    coveragerc_path = os.path.join(cov_data_dir, '.coveragerc')
    with open(coveragerc_path, 'w') as f:
        _ = f.write(f"""\
[run]
source = {_COVERAGE_SOURCE}
data_file = {cov_data_dir}/.coverage
parallel = true
sigterm = true

[report]
omit =
    */test_*
    *conftest*

[html]
directory = {_REPORTS_DIR}
title = Scheduler REST Test Coverage
""")

    return coveragerc_path, cov_data_dir

# ################################################################################################################################
# ################################################################################################################################

def _generate_coverage_report(cov_data_dir:'any_', coveragerc_path:'any_'):
    os.makedirs(_REPORTS_DIR, exist_ok=True)

    _ = subprocess.run(
        [_ZATO_PY, '-m', 'coverage', 'combine', '--rcfile', coveragerc_path, cov_data_dir],
        capture_output=True,
        timeout=30,
    )

    result = subprocess.run(
        [_ZATO_PY, '-m', 'coverage', 'html', '--rcfile', coveragerc_path],
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.returncode == 0:
        print(f'\n=== Coverage HTML report: file://{_REPORTS_DIR}/index.html ===\n')
    else:
        print(f'\n=== Coverage report generation failed: {result.stderr} ===\n')

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session')
def zato_server(request:'any_'):
    global _server_proc, _tmpdir

    use_coverage = request.config.getoption('--with-coverage')

    port = _find_free_port()
    _tmpdir = tempfile.mkdtemp(prefix='zato_sched_test_')

    qs_env = os.environ.copy()
    _ = qs_env.pop('COVERAGE_PROCESS_START', None)

    qs_cmd = [
        _ZATO_BIN, 'quickstart', 'create', _tmpdir,
        '--force',
        '--servers', '1',
        '--server-api-client-for-scheduler-password', _PASSWORD,
    ]
    result = subprocess.run(qs_cmd, capture_output=True, text=True, timeout=120, env=qs_env)
    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    server_dir = os.path.join(_tmpdir, 'server1')
    repo_location = os.path.join(server_dir, 'config', 'repo')

    config = cast_('any_', get_config_object(repo_location, 'server.conf'))
    config['main']['bind'] = f'0.0.0.0:{port}'
    update_config_file(config, repo_location, 'server.conf')

    if _pre_start_service_files:
        services_dir = os.path.join(server_dir, 'pickup', 'incoming', 'services')
        os.makedirs(services_dir, exist_ok=True)
        for filename, content in _pre_start_service_files:
            with open(os.path.join(services_dir, filename), 'w') as f:
                _ = f.write(content)

    coveragerc_path = None
    cov_data_dir = None
    if use_coverage:
        coveragerc_path, cov_data_dir = _setup_coverage(_tmpdir)

    broker_port = _find_free_port()

    # A per-session port for the scheduler's HTTP query API so this session never binds to
    # or answers through the port of any other scheduler running on the same host.
    scheduler_http_port = _find_free_port()

    # A fresh audit database per session, with the audit log explicitly enabled -
    # job execution history lives there and the history tests read it back through
    # the server's own services.
    audit_db_path = os.path.join(_tmpdir, 'audit.db')

    env = os.environ.copy()
    env['Zato_Config_Bind_Port'] = str(port)
    env['Zato_Broker_HTTP_Port'] = str(broker_port)
    env['Zato_Scheduler_Stream_Prefix'] = _STREAM_PREFIX
    env['Zato_Scheduler_HTTP_Port'] = str(scheduler_http_port)
    env[AuditLogCtx.Env_Enabled] = 'True'
    env[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    env[AuditLogCtx.Env_Name] = audit_db_path
    _ = env.pop('COVERAGE_PROCESS_START', None)
    if coveragerc_path:
        env['COVERAGE_PROCESS_START'] = coveragerc_path

    _server_proc = subprocess.Popen(
        [_ZATO_BIN, 'start', server_dir, '--fg'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    t3 = time.monotonic()

    import threading

    _server_output_lines = []

    def _capture_server_output():
        for line in iter(cast_('any_', _server_proc).stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - t3
            _server_output_lines.append(f'[SERVER {elapsed:6.1f}s] {text}')

    _stdout_thread = threading.Thread(target=_capture_server_output, daemon=True)
    _stdout_thread.start()

    host = '127.0.0.1'
    try:
        _wait_for_server(host, port, _PASSWORD)
    except Exception:
        print('\n--- Server did not become ready, captured output: ---')
        for line in _server_output_lines:
            print(line)
        print('--- End of server output ---\n')
        _kill_server()
        raise

    # Start the scheduler component now that the server can answer its initial job request.
    # The Rust binary is run directly, not through `zato start`, so that terminating it
    # actually stops the scheduler instead of leaving it behind as a reparented child.
    global _scheduler_proc

    scheduler_dir = os.path.join(_tmpdir, 'scheduler')
    scheduler_env = os.environ.copy()
    scheduler_env['Zato_Scheduler_Stream_Prefix'] = _STREAM_PREFIX
    scheduler_env['Zato_Scheduler_HTTP_Port'] = str(scheduler_http_port)
    _ = scheduler_env.pop('COVERAGE_PROCESS_START', None)

    _scheduler_proc = subprocess.Popen(
        [_find_scheduler_binary()],
        env=scheduler_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    _scheduler_output_lines = []

    def _capture_scheduler_output():
        for line in iter(cast_('any_', _scheduler_proc).stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            _scheduler_output_lines.append(f'[SCHEDULER] {text}')

    _scheduler_stdout_thread = threading.Thread(target=_capture_scheduler_output, daemon=True)
    _scheduler_stdout_thread.start()

    try:
        _wait_for_scheduler_api(scheduler_http_port)
    except Exception:
        print('\n--- Scheduler did not become ready, captured output: ---')
        for line in _scheduler_output_lines:
            print(line)
        print('--- End of scheduler output ---\n')
        _kill_server()
        _kill_scheduler()
        raise

    server_info = {
        'host': host,
        'port': port,
        'base_url': f'http://{host}:{port}',
        'password': _PASSWORD,
        'server_dir': server_dir,
        'scheduler_dir': scheduler_dir,
        'tmpdir': _tmpdir,
    }

    yield server_info

    _kill_server()
    _kill_scheduler()
    _delete_stream_keys()

    if use_coverage and cov_data_dir and coveragerc_path:
        time.sleep(2)
        _generate_coverage_report(cov_data_dir, coveragerc_path)

    if _tmpdir and os.path.isdir(_tmpdir):
        shutil.rmtree(_tmpdir, ignore_errors=True)
    _tmpdir = None

# ################################################################################################################################
# ################################################################################################################################
