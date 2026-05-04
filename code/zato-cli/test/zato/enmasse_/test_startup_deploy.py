# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

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
from base64 import b64encode
from logging import basicConfig, getLogger, WARN
from unittest import main, TestCase

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_ZATO_BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_ZATO_BIN = os.path.join(_ZATO_BASE, 'bin', 'zato')
_PASSWORD = 'test.startup.deploy.' + os.urandom(8).hex()

_procs_to_kill = []

def _cleanup_all():
    for proc in _procs_to_kill:
        _kill_proc(proc)

atexit.register(_cleanup_all)

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

# ################################################################################################################################
# ################################################################################################################################

def _kill_proc(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host, port, password, timeout=60):
    from urllib.request import Request, urlopen

    creds = b64encode(f'admin.invoke:{password}'.encode()).decode()
    url = f'http://{host}:{port}/zato/api/invoke/demo.ping'
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            req = Request(url, method='GET')
            req.add_header('Authorization', f'Basic {creds}')
            with urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    return
        except Exception:
            pass
        time.sleep(0.5)

    raise Exception(f'Server at {host}:{port} did not respond within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

def _read_server_log(server_dir):
    import re
    server_log = os.path.join(server_dir, 'logs', 'server.log')
    if os.path.isfile(server_log):
        with open(server_log) as f:
            raw = f.read()
        return re.sub(r'\x1b\[[0-9;]*m', '', raw)
    return ''

# ################################################################################################################################
# ################################################################################################################################

def _dump_debug(server_dir, server_output_lines):
    print('\n--- Server stdout: ---', file=sys.stderr)
    for line in server_output_lines[-50:]:
        print(line, file=sys.stderr)
    print('--- End of server stdout ---\n', file=sys.stderr)

    server_log = os.path.join(server_dir, 'logs', 'server.log')
    if os.path.isfile(server_log):
        print(f'\n--- server.log tail: ---', file=sys.stderr)
        with open(server_log) as f:
            for line in f.readlines()[-50:]:
                print(line.rstrip(), file=sys.stderr)
        print('--- End of server.log ---\n', file=sys.stderr)

# ################################################################################################################################
# ################################################################################################################################

def _create_quickstart(tmpdir, password):
    qs_dir = os.path.join(tmpdir, 'qs')
    os.makedirs(qs_dir)

    qs_env = os.environ.copy()
    qs_env.pop('COVERAGE_PROCESS_START', None)

    qs_cmd = [
        _ZATO_BIN, 'quickstart', 'create', qs_dir,
        '--servers', '1',
        '--server-api-client-for-scheduler-password', password,
        '--no-scheduler',
    ]

    result = subprocess.run(qs_cmd, capture_output=True, text=True, timeout=120, env=qs_env)
    if result.returncode != 0:
        return None, f'quickstart create failed:\n{result.stdout}\n{result.stderr}'

    return os.path.join(qs_dir, 'server1'), None

# ################################################################################################################################
# ################################################################################################################################

def _start_server(server_dir, port, broker_port, extra_env=None, extra_args=None):

    repo_location = os.path.join(server_dir, 'config', 'repo')

    from zato.common.util.config import get_config_object, update_config_file
    config = get_config_object(repo_location, 'server.conf')
    config['main']['port'] = str(port)
    update_config_file(config, repo_location, 'server.conf')

    env = os.environ.copy()
    env['Zato_Config_Bind_Port'] = str(port)
    env['Zato_Broker_HTTP_Port'] = str(broker_port)
    env.pop('COVERAGE_PROCESS_START', None)

    if extra_env:
        env.update(extra_env)

    cmd = [_ZATO_BIN, 'start', server_dir, '--fg']
    if extra_args:
        cmd.extend(extra_args)

    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    output_lines = []

    def _capture():
        for line in iter(proc.stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').rstrip()
            output_lines.append(text)

    thread = threading.Thread(target=_capture, daemon=True)
    thread.start()

    return proc, output_lines, thread

# ################################################################################################################################
# ################################################################################################################################

def _make_service_code(token, service_name, expected):
    return f'''\
# -*- coding: utf-8 -*-
from zato.server.service import Service

class TestSvc{token[:8].title()}(Service):
    name = '{service_name}'

    def handle(self):
        self.response.payload = '{expected}'
'''

# ################################################################################################################################
# ################################################################################################################################

class TestDockerPostStartEnmasseImport(TestCase):
    """Docker entrypoint.sh lines 315-326:
      zato enmasse <server> --import --input /tmp/enmasse.yaml --env-file /tmp/env.ini
    Simulates the post-start CLI enmasse import with env variable resolution.
    """

    @classmethod
    def setUpClass(cls):
        from unittest import SkipTest

        if not os.path.isfile(_ZATO_BIN):
            raise SkipTest('ZATO STARTUP DEPLOY TESTS SKIPPED - zato binary not found')

        cls._tmpdir = tempfile.mkdtemp(prefix='zato_docker_enmasse_test_')
        cls.port = _find_free_port()
        cls.broker_port = _find_free_port()

        cls.server_dir, err = _create_quickstart(cls._tmpdir, _PASSWORD)
        if err:
            shutil.rmtree(cls._tmpdir, ignore_errors=True)
            raise SkipTest(f'ZATO STARTUP DEPLOY TESTS SKIPPED - {err}')

        cls._token = os.urandom(12).hex()
        cls._service_name = f'test.docker.enmasse.{cls._token[:8]}'
        cls._expected = f'docker-enmasse-{cls._token}'
        cls._url_path = f'/test/docker/enmasse/{cls._token[:8]}'
        cls._channel_name = f'test.docker.enmasse.ch.{cls._token[:8]}'

        pickup_dir = os.path.join(cls.server_dir, 'pickup', 'incoming', 'services')
        with open(os.path.join(pickup_dir, f'docker_svc_{cls._token[:8]}.py'), 'w') as f:
            f.write(_make_service_code(cls._token, cls._service_name, cls._expected))

        cls._enmasse_file = os.path.join(cls._tmpdir, 'enmasse.yaml')
        cls._env_ini_file = os.path.join(cls._tmpdir, 'env.ini')

        env_var_name = f'ENMASSE_SVC_{cls._token[:8]}'
        enmasse_yaml = f'''\
channel_rest:
  - name: {cls._channel_name}
    service: ${{{env_var_name}}}
    url_path: {cls._url_path}
    is_active: true
'''
        with open(cls._enmasse_file, 'w') as f:
            f.write(enmasse_yaml)

        with open(cls._env_ini_file, 'w') as f:
            f.write(f'[env]\n{env_var_name}={cls._service_name}\n')

        cls._proc, cls._output_lines, cls._thread = _start_server(
            cls.server_dir, cls.port, cls.broker_port)
        _procs_to_kill.append(cls._proc)

        try:
            _wait_for_server('127.0.0.1', cls.port, _PASSWORD, timeout=60)
        except Exception:
            _dump_debug(cls.server_dir, cls._output_lines)
            _kill_proc(cls._proc)
            raise

        enmasse_env = os.environ.copy()
        enmasse_env.pop('COVERAGE_PROCESS_START', None)

        result = subprocess.run([
            _ZATO_BIN, 'enmasse', cls.server_dir, '--import',
            '--input', cls._enmasse_file,
            '--env-file', cls._env_ini_file,
        ], capture_output=True, text=True, timeout=60, env=enmasse_env)

        cls._enmasse_result = result
        cls._enmasse_import_ok = result.returncode == 0

    @classmethod
    def tearDownClass(cls):
        _kill_proc(cls._proc)
        if cls._tmpdir and os.path.isdir(cls._tmpdir):
            shutil.rmtree(cls._tmpdir, ignore_errors=True)

    def test_import_succeeded(self):
        self.assertTrue(self._enmasse_import_ok,
            f'enmasse import failed: {self._enmasse_result.stdout}\n{self._enmasse_result.stderr}')

    def test_channel_available(self):
        import requests as req_lib

        self.assertTrue(self._enmasse_import_ok, 'Skipping - enmasse import failed')

        url = f'http://127.0.0.1:{self.port}{self._url_path}'

        deadline = time.monotonic() + 15
        last_resp = None
        while time.monotonic() < deadline:
            try:
                resp = req_lib.get(url, timeout=5)
                last_resp = resp
                if resp.status_code == 200 and self._expected in resp.text:
                    return
            except Exception:
                pass
            time.sleep(1)

        status = last_resp.status_code if last_resp else 'no response'
        body = last_resp.text[:300] if last_resp else ''
        self.fail(f'Channel invoke failed after retries: {status} {body}')

    def test_env_variable_resolved(self):
        """The ${{ENV_VAR}} in the enmasse YAML should have been resolved via --env-file."""
        import requests as req_lib

        self.assertTrue(self._enmasse_import_ok, 'Skipping - enmasse import failed')

        creds = b64encode(f'admin.invoke:{_PASSWORD}'.encode()).decode()
        url = f'http://127.0.0.1:{self.port}/zato/api/invoke/{self._service_name}'
        resp = req_lib.get(url, headers={'Authorization': f'Basic {creds}'}, timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self._expected, resp.text)

# ################################################################################################################################
# ################################################################################################################################

class TestDockerProjectRootFileListener(TestCase):
    """Docker entrypoint.sh lines 792-807:
      File transfer listener started for each Zato_Project_Root* env var.
    Now handled by the in-process file listener via Zato_Project_Root.
    The service .py is placed directly in the project root (visit_py_source
    only scans the immediate directory). Enmasse is imported post-start via CLI,
    matching how Docker's perform_post_server_operations works.
    """

    @classmethod
    def setUpClass(cls):
        from unittest import SkipTest

        if not os.path.isfile(_ZATO_BIN):
            raise SkipTest('ZATO STARTUP DEPLOY TESTS SKIPPED - zato binary not found')

        cls._tmpdir = tempfile.mkdtemp(prefix='zato_docker_projroot_test_')
        cls.port = _find_free_port()
        cls.broker_port = _find_free_port()

        cls.server_dir, err = _create_quickstart(cls._tmpdir, _PASSWORD)
        if err:
            shutil.rmtree(cls._tmpdir, ignore_errors=True)
            raise SkipTest(f'ZATO STARTUP DEPLOY TESTS SKIPPED - {err}')

        cls._token = os.urandom(12).hex()
        cls._service_name = f'test.docker.projroot.{cls._token[:8]}'
        cls._expected = f'docker-projroot-{cls._token}'
        cls._url_path = f'/test/docker/projroot/{cls._token[:8]}'
        cls._channel_name = f'test.docker.projroot.ch.{cls._token[:8]}'

        cls._project_root = os.path.join(cls._tmpdir, 'project_root')
        os.makedirs(cls._project_root)

        with open(os.path.join(cls._project_root, f'projroot_svc_{cls._token[:8]}.py'), 'w') as f:
            f.write(_make_service_code(cls._token, cls._service_name, cls._expected))

        cls._enmasse_file = os.path.join(cls._tmpdir, 'projroot_enmasse.yaml')
        enmasse_yaml = f'''\
channel_rest:
  - name: {cls._channel_name}
    service: {cls._service_name}
    url_path: {cls._url_path}
    is_active: true
'''
        with open(cls._enmasse_file, 'w') as f:
            f.write(enmasse_yaml)

        cls._proc, cls._output_lines, cls._thread = _start_server(
            cls.server_dir, cls.port, cls.broker_port,
            extra_env={'Zato_Project_Root': cls._project_root})
        _procs_to_kill.append(cls._proc)

        try:
            _wait_for_server('127.0.0.1', cls.port, _PASSWORD, timeout=60)
        except Exception:
            _dump_debug(cls.server_dir, cls._output_lines)
            _kill_proc(cls._proc)
            raise

        enmasse_env = os.environ.copy()
        enmasse_env.pop('COVERAGE_PROCESS_START', None)

        result = subprocess.run([
            _ZATO_BIN, 'enmasse', cls.server_dir, '--import',
            '--input', cls._enmasse_file,
        ], capture_output=True, text=True, timeout=60, env=enmasse_env)
        cls._enmasse_import_ok = result.returncode == 0
        cls._enmasse_result = result

    @classmethod
    def tearDownClass(cls):
        _kill_proc(cls._proc)
        if cls._tmpdir and os.path.isdir(cls._tmpdir):
            shutil.rmtree(cls._tmpdir, ignore_errors=True)

    def test_service_deployed_from_project_root(self):
        import requests as req_lib

        creds = b64encode(f'admin.invoke:{_PASSWORD}'.encode()).decode()
        url = f'http://127.0.0.1:{self.port}/zato/api/invoke/{self._service_name}'

        resp = req_lib.get(url, headers={'Authorization': f'Basic {creds}'}, timeout=10)
        self.assertEqual(resp.status_code, 200,
            f'Service invoke failed: {resp.status_code} {resp.text[:300]}')
        self.assertIn(self._expected, resp.text)

    def test_enmasse_channel_from_project_root(self):
        import requests as req_lib

        self.assertTrue(self._enmasse_import_ok,
            f'enmasse import failed: {self._enmasse_result.stdout}\n{self._enmasse_result.stderr}')

        url = f'http://127.0.0.1:{self.port}{self._url_path}'

        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            try:
                resp = req_lib.get(url, timeout=5)
                if resp.status_code == 200 and self._expected in resp.text:
                    return
            except Exception:
                pass
            time.sleep(1)

        _dump_debug(self.server_dir, self._output_lines)
        self.fail(f'Channel at {self._url_path} not available within 15s via Zato_Project_Root')

    def test_log_reflects_project_root(self):
        log_content = _read_server_log(self.server_dir)
        self.assertIn('Zato_Project_Root', log_content,
            'server.log does not mention Zato_Project_Root')

# ################################################################################################################################
# ################################################################################################################################

class TestDockerProjectRootFromEnvIni(TestCase):
    """Docker entrypoint.sh lines 809-830:
      Reads env.ini for Zato_Project_Root* keys and starts listeners for each.
    We simulate this by passing the same env var the entrypoint would set
    after parsing env.ini.
    """

    @classmethod
    def setUpClass(cls):
        from unittest import SkipTest

        if not os.path.isfile(_ZATO_BIN):
            raise SkipTest('ZATO STARTUP DEPLOY TESTS SKIPPED - zato binary not found')

        cls._tmpdir = tempfile.mkdtemp(prefix='zato_docker_envini_projroot_test_')
        cls.port = _find_free_port()
        cls.broker_port = _find_free_port()

        cls.server_dir, err = _create_quickstart(cls._tmpdir, _PASSWORD)
        if err:
            shutil.rmtree(cls._tmpdir, ignore_errors=True)
            raise SkipTest(f'ZATO STARTUP DEPLOY TESTS SKIPPED - {err}')

        cls._token = os.urandom(12).hex()
        cls._service_name = f'test.docker.envini.{cls._token[:8]}'
        cls._expected = f'docker-envini-{cls._token}'

        cls._project_root = os.path.join(cls._tmpdir, 'project_root_envini')
        os.makedirs(cls._project_root)

        with open(os.path.join(cls._project_root, f'envini_svc_{cls._token[:8]}.py'), 'w') as f:
            f.write(_make_service_code(cls._token, cls._service_name, cls._expected))

        cls._proc, cls._output_lines, cls._thread = _start_server(
            cls.server_dir, cls.port, cls.broker_port,
            extra_env={'Zato_Project_Root_MyApp': cls._project_root})
        _procs_to_kill.append(cls._proc)

        try:
            _wait_for_server('127.0.0.1', cls.port, _PASSWORD, timeout=60)
        except Exception:
            _dump_debug(cls.server_dir, cls._output_lines)
            _kill_proc(cls._proc)
            raise

    @classmethod
    def tearDownClass(cls):
        _kill_proc(cls._proc)
        if cls._tmpdir and os.path.isdir(cls._tmpdir):
            shutil.rmtree(cls._tmpdir, ignore_errors=True)

    def test_service_deployed_from_suffixed_project_root(self):
        import requests as req_lib

        creds = b64encode(f'admin.invoke:{_PASSWORD}'.encode()).decode()
        url = f'http://127.0.0.1:{self.port}/zato/api/invoke/{self._service_name}'

        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            try:
                resp = req_lib.get(url, headers={'Authorization': f'Basic {creds}'}, timeout=5)
                if resp.status_code == 200 and self._expected in resp.text:
                    return
            except Exception:
                pass
            time.sleep(1)

        _dump_debug(self.server_dir, self._output_lines)
        self.fail(f'Service {self._service_name} not available within 30s via Zato_Project_Root_MyApp')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
