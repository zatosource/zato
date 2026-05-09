# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

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

sys.path.insert(0, os.path.dirname(__file__))

# PyPI
import pytest

# Zato
from zato.common.util.config import get_config_object, update_config_file

def pytest_addoption(parser):
    parser.addoption('--with-coverage', action='store_true', default=False,
                     help='Enable coverage collection on the Zato server subprocess')

_ZATO_BASE = '/home/dsuch/projects/zatosource-zato/4.1'
_ZATO_BIN = os.path.join(_ZATO_BASE, 'code', 'bin', 'zato')
_ZATO_PY = os.path.join(_ZATO_BASE, 'code', 'bin', 'python')

_PASSWORD = 'test.invoke.' + os.urandom(8).hex()

_REPORTS_DIR = os.path.join(_ZATO_BASE, 'code', 'tests', 'python', 'zato-server', 'config_store', 'reports')

_COVERAGE_SOURCE = os.path.join(
    _ZATO_BASE, 'code', 'zato-server', 'src', 'zato', 'server', 'service', 'internal')

_server_proc = None
_tmpdir = None

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

def _cleanup():
    _kill_server()
    global _tmpdir
    if _tmpdir and os.path.isdir(_tmpdir):
        shutil.rmtree(_tmpdir, ignore_errors=True)
    _tmpdir = None

atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host, port, timeout=60):
    from urllib.request import Request, urlopen

    url = f'http://{host}:{port}/zato/ping'
    t0 = time.monotonic()
    deadline = t0 + timeout
    attempt = 0

    while time.monotonic() < deadline:
        attempt += 1
        elapsed = time.monotonic() - t0
        try:
            req = Request(url, method='GET')
            with urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    print(f'[TIMING] ping OK after {elapsed:.1f}s (attempt {attempt})')
                    return
        except Exception as e:
            err = str(e)[:80]
            print(f'[TIMING] ping attempt {attempt} at {elapsed:.1f}s: {err}')
        time.sleep(0.5)

    raise RuntimeError(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _setup_coverage(tmpdir):
    """Set up .coveragerc for subprocess instrumentation via the installed a1_coverage.pth."""

    cov_data_dir = os.path.join(tmpdir, 'coverage')
    os.makedirs(cov_data_dir, exist_ok=True)

    coveragerc_path = os.path.join(cov_data_dir, '.coveragerc')
    with open(coveragerc_path, 'w') as f:
        f.write(f"""\
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
title = ConfigStore REST Test Coverage
""")

    return coveragerc_path, cov_data_dir

# ################################################################################################################################
# ################################################################################################################################

def _generate_coverage_report(cov_data_dir, coveragerc_path):
    """Combine coverage data and generate the HTML report."""

    os.makedirs(_REPORTS_DIR, exist_ok=True)

    subprocess.run(
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
def zato_server(request):
    global _server_proc, _tmpdir

    use_coverage = request.config.getoption('--with-coverage')

    t0 = time.monotonic()

    port = _find_free_port()
    _tmpdir = tempfile.mkdtemp(prefix='zato_test_')

    # 1) Create quickstart (with a clean env to avoid stale COVERAGE_PROCESS_START interference)
    qs_env = os.environ.copy()
    qs_env.pop('COVERAGE_PROCESS_START', None)

    qs_cmd = [
        _ZATO_BIN, 'quickstart', 'create', _tmpdir,
        '--servers', '1',
        '--password', _PASSWORD,
        '--server-api-client-for-scheduler-password', _PASSWORD,
        '--no-scheduler',
    ]
    result = subprocess.run(qs_cmd, capture_output=True, text=True, timeout=120, env=qs_env)
    if result.returncode != 0:
        raise RuntimeError(f'quickstart create failed:\nstdout: {result.stdout}\nstderr: {result.stderr}')

    t1 = time.monotonic()
    print(f'\n[TIMING] quickstart create: {t1 - t0:.1f}s')

    # 2) Patch server.conf to use our port via Zato's own ConfigObj utilities
    server_dir = os.path.join(_tmpdir, 'server1')
    repo_location = os.path.join(server_dir, 'config', 'repo')

    config = get_config_object(repo_location, 'server.conf')
    config['main']['port'] = str(port)
    update_config_file(config, repo_location, 'server.conf')

    t2 = time.monotonic()
    print(f'[TIMING] config patch: {t2 - t1:.1f}s')

    # 3) Optionally set up coverage instrumentation
    coveragerc_path = None
    cov_data_dir = None
    if use_coverage:
        coveragerc_path, cov_data_dir = _setup_coverage(_tmpdir)

    # 4) Start the server in foreground mode
    broker_port = _find_free_port()

    env = os.environ.copy()
    env['Zato_Config_Bind_Port'] = str(port)
    env['Zato_Broker_HTTP_Port'] = str(broker_port)
    env.pop('COVERAGE_PROCESS_START', None)
    if use_coverage:
        env['COVERAGE_PROCESS_START'] = coveragerc_path

    _server_proc = subprocess.Popen(
        [_ZATO_BIN, 'start', server_dir, '--fg'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    t3 = time.monotonic()
    print(f'[TIMING] Popen started: {t3 - t2:.1f}s')

    # 5) Stream server stdout in a background thread so we can see what it's doing
    import threading

    def _stream_server_output():
        for line in iter(_server_proc.stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            elapsed = time.monotonic() - t3
            print(f'[SERVER {elapsed:6.1f}s] {text}')

    _stdout_thread = threading.Thread(target=_stream_server_output, daemon=True)
    _stdout_thread.start()

    # 6) Wait for the server to come up
    host = '127.0.0.1'
    try:
        _wait_for_server(host, port)
        t4 = time.monotonic()
        print(f'[TIMING] server ready: {t4 - t3:.1f}s')
        print(f'[TIMING] total setup: {t4 - t0:.1f}s')
    except Exception:
        print('\n--- Server did not become ready, stdout was streamed above ---\n')
        _kill_server()
        raise

    yield {
        'host': host,
        'port': port,
        'password': _PASSWORD,
        'server_dir': server_dir,
        'tmpdir': _tmpdir,
    }

    # 6) Teardown: stop server, optionally generate coverage report
    _kill_server()

    if use_coverage and cov_data_dir and coveragerc_path:
        time.sleep(2)
        _generate_coverage_report(cov_data_dir, coveragerc_path)

    if _tmpdir and os.path.isdir(_tmpdir):
        shutil.rmtree(_tmpdir, ignore_errors=True)
    _tmpdir = None

# ################################################################################################################################
# ################################################################################################################################
