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
import yaml
from logging import basicConfig, getLogger, WARN
from unittest import main, TestCase

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_time_dependent_fields = frozenset(['start_date'])
_random_fields = frozenset(['password', 'username'])
_skip_sections = frozenset(['pubsub_permission', 'pubsub_subscription'])

_ZATO_BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_ZATO_BIN = os.path.join(_ZATO_BASE, 'bin', 'zato')
_PASSWORD = 'test.enmasse.cli.' + os.urandom(8).hex()

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

atexit.register(_cleanup)

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_server(host, port, password, timeout=60):
    from urllib.request import Request, urlopen
    from base64 import b64encode

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

def _get_sort_key(item):
    if 'name' in item:
        return ('name',)
    if 'security' in item:
        return ('security',)
    return None

def _normalize_for_comparison(data, skip_fields=None):
    skip_fields = skip_fields or set()

    if isinstance(data, dict):
        return {
            k: '<SKIPPED>' if k in skip_fields else _normalize_for_comparison(v, skip_fields)
            for k, v in sorted(data.items())
        }

    elif isinstance(data, list):
        normalized = [_normalize_for_comparison(item, skip_fields) for item in data]
        if normalized and isinstance(normalized[0], dict):
            sort_key = _get_sort_key(normalized[0])
            if sort_key:
                normalized.sort(key=lambda x: tuple(str(x.get(k, '')) for k in sort_key))
        return normalized

    else:
        return data

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseCLI(TestCase):

    server_dir = None
    port = None

    @classmethod
    def setUpClass(cls):
        from unittest import SkipTest
        global _server_proc, _tmpdir

        if not os.path.isfile(_ZATO_BIN):
            raise SkipTest(f'ZATO ENMASSE CLI TESTS SKIPPED - zato binary not found at {_ZATO_BIN}')

        cls.port = _find_free_port()
        _tmpdir = tempfile.mkdtemp(prefix='zato_enmasse_cli_test_')

        qs_env = os.environ.copy()
        qs_env.pop('COVERAGE_PROCESS_START', None)

        qs_cmd = [
            _ZATO_BIN, 'quickstart', 'create', _tmpdir,
            '--servers', '1',
            '--server-api-client-for-scheduler-password', _PASSWORD,
            '--no-scheduler',
        ]

        result = subprocess.run(qs_cmd, capture_output=True, text=True, timeout=120, env=qs_env)
        if result.returncode != 0:
            shutil.rmtree(_tmpdir, ignore_errors=True)
            _tmpdir = None
            raise SkipTest(
                f'ZATO ENMASSE CLI TESTS SKIPPED - quickstart create failed:\n{result.stdout}\n{result.stderr}')

        cls.server_dir = os.path.join(_tmpdir, 'server1')
        repo_location = os.path.join(cls.server_dir, 'config', 'repo')

        from zato.common.util.config import get_config_object, update_config_file
        config = get_config_object(repo_location, 'server.conf')
        config['main']['port'] = str(cls.port)
        update_config_file(config, repo_location, 'server.conf')

        broker_port = _find_free_port()

        env = os.environ.copy()
        env['Zato_Config_Bind_Port'] = str(cls.port)
        env['Zato_Broker_HTTP_Port'] = str(broker_port)
        env.pop('COVERAGE_PROCESS_START', None)

        _server_proc = subprocess.Popen(
            [_ZATO_BIN, 'start', cls.server_dir, '--fg'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        cls._server_output_lines = []

        def _capture():
            for line in iter(_server_proc.stdout.readline, b''):
                text = line.decode('utf-8', errors='replace').rstrip()
                cls._server_output_lines.append(text)

        cls._stdout_thread = threading.Thread(target=_capture, daemon=True)
        cls._stdout_thread.start()

        try:
            _wait_for_server('127.0.0.1', cls.port, _PASSWORD, timeout=60)
        except Exception:
            print('\n--- Server did not become ready, output: ---', file=sys.stderr)
            for line in cls._server_output_lines:
                print(line, file=sys.stderr)
            print('--- End of server output ---\n', file=sys.stderr)

            server_log = os.path.join(repo_location, '..', '..', 'logs', 'server.log')
            if os.path.isfile(server_log):
                print(f'\n--- server.log ({server_log}): ---', file=sys.stderr)
                with open(server_log) as f:
                    for line in f.readlines()[-50:]:
                        print(line.rstrip(), file=sys.stderr)
                print('--- End of server.log ---\n', file=sys.stderr)

            _kill_server()
            raise

    @classmethod
    def tearDownClass(cls):
        global _tmpdir
        _kill_server()
        if _tmpdir and os.path.isdir(_tmpdir):
            shutil.rmtree(_tmpdir, ignore_errors=True)
        _tmpdir = None

# ################################################################################################################################

    def _invoke_enmasse(self, *extra_args):
        result = subprocess.run(
            [_ZATO_BIN, 'enmasse', self.server_dir, '--verbose'] + list(extra_args),
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            self.fail(f'enmasse failed (exit {result.returncode}):\n{result.stdout[:500]}')
        return result

    def _import_file(self, path):
        return self._invoke_enmasse('--import', '--input', path)

    def _export_file(self, path):
        return self._invoke_enmasse('--export', '--output', path)

    def _read_yaml(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f.read())

# ################################################################################################################################

    def test_cli_roundtrip(self):
        """ Import via CLI, export, re-import the export, re-export, compare.
        Then do it once more and compare again.
        """
        from zato.common.test.enmasse_._template_complex_01 import template_complex_01

        tmp_dir = tempfile.gettempdir()
        input_path = os.path.join(tmp_dir, 'zato-enmasse-cli-input.yaml')
        export_1_path = os.path.join(tmp_dir, 'zato-enmasse-cli-export-1.yaml')
        export_2_path = os.path.join(tmp_dir, 'zato-enmasse-cli-export-2.yaml')
        export_3_path = os.path.join(tmp_dir, 'zato-enmasse-cli-export-3.yaml')

        skip_fields = _time_dependent_fields | _random_fields

        try:

            with open(input_path, 'w') as f:
                _ = f.write(template_complex_01)

            # Round 1: import original, export
            self._import_file(input_path)
            self._export_file(export_1_path)

            data_1 = self._read_yaml(export_1_path)
            self.assertTrue(data_1, 'Round 1 export is empty')

            original_sections = set(yaml.safe_load(template_complex_01).keys())
            for section in original_sections - _skip_sections:
                self.assertIn(section, data_1, f'Section "{section}" missing from export')

            # Round 2: re-import the export, re-export
            self._import_file(export_1_path)
            self._export_file(export_2_path)

            data_2 = self._read_yaml(export_2_path)
            self.assertTrue(data_2, 'Round 2 export is empty')

            data_1_filtered = {k: v for k, v in data_1.items() if k not in _skip_sections}
            data_2_filtered = {k: v for k, v in data_2.items() if k not in _skip_sections}

            norm_1 = _normalize_for_comparison(data_1_filtered, skip_fields)
            norm_2 = _normalize_for_comparison(data_2_filtered, skip_fields)

            self.assertEqual(norm_1, norm_2, 'Round 2 export differs from round 1 (not idempotent)')

            # Round 3: re-import again, re-export again
            self._import_file(export_2_path)
            self._export_file(export_3_path)

            data_3 = self._read_yaml(export_3_path)
            data_3_filtered = {k: v for k, v in data_3.items() if k not in _skip_sections}

            norm_3 = _normalize_for_comparison(data_3_filtered, skip_fields)

            self.assertEqual(norm_2, norm_3, 'Round 3 export differs from round 2 (unstable)')

        finally:
            for p in (input_path, export_1_path, export_2_path, export_3_path):
                if os.path.exists(p):
                    os.remove(p)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
