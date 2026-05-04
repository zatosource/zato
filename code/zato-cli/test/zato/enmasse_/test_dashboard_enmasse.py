# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import atexit
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import yaml
from base64 import b64encode
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
_PASSWORD = 'test.dashboard.enmasse.' + os.urandom(8).hex()

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

def _cleanup():
    global _server_proc
    _kill_proc(_server_proc)
    _server_proc = None

atexit.register(_cleanup)

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

class TestDashboardEnmasse(TestCase):
    """Test the server endpoints that the web-admin dashboard uses
    for enmasse export and import (POST /zato/api/invoke/zato.server.invoker)."""

    server_dir = None
    port = None

    @classmethod
    def setUpClass(cls):
        from unittest import SkipTest
        global _server_proc, _tmpdir

        if not os.path.isfile(_ZATO_BIN):
            raise SkipTest(f'ZATO DASHBOARD ENMASSE TESTS SKIPPED - zato binary not found at {_ZATO_BIN}')

        cls.port = _find_free_port()
        broker_port = _find_free_port()
        _tmpdir = tempfile.mkdtemp(prefix='zato_dashboard_enmasse_test_')

        qs_dir = os.path.join(_tmpdir, 'qs')
        os.makedirs(qs_dir)

        qs_env = os.environ.copy()
        qs_env.pop('COVERAGE_PROCESS_START', None)

        qs_cmd = [
            _ZATO_BIN, 'quickstart', 'create', qs_dir,
            '--servers', '1',
            '--server-api-client-for-scheduler-password', _PASSWORD,
            '--no-scheduler',
        ]

        result = subprocess.run(qs_cmd, capture_output=True, text=True, timeout=120, env=qs_env)
        if result.returncode != 0:
            shutil.rmtree(_tmpdir, ignore_errors=True)
            _tmpdir = None
            raise SkipTest(
                f'ZATO DASHBOARD ENMASSE TESTS SKIPPED - quickstart create failed:\n'
                f'{result.stdout}\n{result.stderr}')

        cls.server_dir = os.path.join(qs_dir, 'server1')
        repo_location = os.path.join(cls.server_dir, 'config', 'repo')

        from zato.common.util.config import get_config_object, update_config_file
        config = get_config_object(repo_location, 'server.conf')
        config['main']['port'] = str(cls.port)
        update_config_file(config, repo_location, 'server.conf')

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

        def _capture_server():
            for line in iter(_server_proc.stdout.readline, b''):
                text = line.decode('utf-8', errors='replace').rstrip()
                cls._server_output_lines.append(text)

        cls._server_thread = threading.Thread(target=_capture_server, daemon=True)
        cls._server_thread.start()

        try:
            _wait_for_server('127.0.0.1', cls.port, _PASSWORD, timeout=5)
        except Exception:
            cls._dump_debug(repo_location)
            _kill_proc(_server_proc)
            raise

    @classmethod
    def _dump_debug(cls, repo_location=None):
        print('\n--- Server stdout at time of failure: ---', file=sys.stderr)
        for line in cls._server_output_lines[-40:]:
            print(line, file=sys.stderr)
        print('--- End of server stdout ---\n', file=sys.stderr)

        if repo_location:
            server_log = os.path.join(repo_location, '..', '..', 'logs', 'server.log')
        else:
            server_log = os.path.join(cls.server_dir, 'logs', 'server.log')

        if os.path.isfile(server_log):
            print(f'\n--- server.log tail: ---', file=sys.stderr)
            with open(server_log) as f:
                for line in f.readlines()[-50:]:
                    print(line.rstrip(), file=sys.stderr)
            print('--- End of server.log ---\n', file=sys.stderr)

    @classmethod
    def tearDownClass(cls):
        global _tmpdir, _server_proc
        _kill_proc(_server_proc)
        _server_proc = None
        if _tmpdir and os.path.isdir(_tmpdir):
            shutil.rmtree(_tmpdir, ignore_errors=True)
        _tmpdir = None

# ################################################################################################################################

    def _invoke_server(self, payload):
        """POST to /zato/api/invoke/zato.server.invoker - the same endpoint the dashboard uses."""
        import requests as req_lib

        url = f'http://127.0.0.1:{self.port}/zato/api/invoke/zato.server.invoker'
        creds = b64encode(f'admin.invoke:{_PASSWORD}'.encode()).decode()

        resp = req_lib.post(
            url,
            json=payload,
            headers={'Authorization': f'Basic {creds}'},
            timeout=15,
        )
        return resp

    def _dashboard_export(self):
        """Call export_enmasse via the dashboard endpoint.
        The ServiceInvoker JSON-encodes the inner service's response,
        so the HTTP body is a JSON string containing YAML text."""
        resp = self._invoke_server({'func_name': 'export_enmasse'})
        self.assertEqual(resp.status_code, 200,
            f'Dashboard export failed with status {resp.status_code}: {resp.text[:300]}')
        raw = resp.text
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            pass
        if isinstance(raw, str):
            return raw
        return str(raw)

    def _dashboard_import(self, yaml_content, file_name='enmasse.yaml'):
        """Call import_enmasse via the dashboard endpoint.
        The inner service returns a JSON string, and ServiceInvoker JSON-encodes it again,
        so the HTTP body is a double-JSON-encoded dict."""
        resp = self._invoke_server({
            'func_name': 'import_enmasse',
            'file_content': yaml_content,
            'file_name': file_name,
        })
        self.assertEqual(resp.status_code, 200,
            f'Dashboard import failed with status {resp.status_code}: {resp.text[:300]}')

        raw = resp.text
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            data = raw

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                pass

        if isinstance(data, dict):
            self.assertTrue(data.get('is_ok', False),
                f'Dashboard import returned is_ok=false: {data.get("stderr", "")[:300]}')

        return data

# ################################################################################################################################

    def test_01_empty_export(self):
        """Export from a fresh server via the dashboard endpoint.
        Should return either empty string or valid YAML, never Bunch()."""
        raw = self._dashboard_export()
        self.assertNotIn('Bunch()', raw, 'Dashboard export returned Bunch() for empty config')

    def test_02_import_then_export(self):
        """Import config via the dashboard endpoint, then export it back and verify."""
        from zato.common.test.enmasse_._template_complex_01 import template_complex_01

        self._dashboard_import(template_complex_01)

        raw_export = self._dashboard_export()
        self.assertTrue(raw_export.strip(), 'Dashboard export is empty after import')

        exported_data = yaml.safe_load(raw_export)
        self.assertIsInstance(exported_data, dict, 'Dashboard export is not a valid YAML dict')

        original_sections = set(yaml.safe_load(template_complex_01).keys())
        for section in original_sections - _skip_sections:
            self.assertIn(section, exported_data,
                f'Section "{section}" missing from dashboard export')

    def test_03_roundtrip_via_dashboard(self):
        """Import via dashboard, export, re-import the export, re-export, compare.
        This is the same roundtrip logic as test_server_cli but going through the
        HTTP endpoint the dashboard uses."""
        from zato.common.test.enmasse_._template_complex_01 import template_complex_01

        skip_fields = _time_dependent_fields | _random_fields

        # Round 1: import original, export
        self._dashboard_import(template_complex_01)
        raw_1 = self._dashboard_export()
        data_1 = yaml.safe_load(raw_1)
        self.assertTrue(data_1, 'Round 1 dashboard export is empty')

        # Round 2: re-import the export, re-export
        self._dashboard_import(raw_1)
        raw_2 = self._dashboard_export()
        data_2 = yaml.safe_load(raw_2)
        self.assertTrue(data_2, 'Round 2 dashboard export is empty')

        data_1_filtered = {k: v for k, v in data_1.items() if k not in _skip_sections}
        data_2_filtered = {k: v for k, v in data_2.items() if k not in _skip_sections}

        norm_1 = _normalize_for_comparison(data_1_filtered, skip_fields)
        norm_2 = _normalize_for_comparison(data_2_filtered, skip_fields)

        self.assertEqual(norm_1, norm_2, 'Dashboard roundtrip is not idempotent (round 2 differs from round 1)')

        # Round 3: one more re-import + re-export for stability
        self._dashboard_import(raw_2)
        raw_3 = self._dashboard_export()
        data_3 = yaml.safe_load(raw_3)
        data_3_filtered = {k: v for k, v in data_3.items() if k not in _skip_sections}
        norm_3 = _normalize_for_comparison(data_3_filtered, skip_fields)

        self.assertEqual(norm_2, norm_3, 'Dashboard roundtrip unstable (round 3 differs from round 2)')

    def test_04_cli_import_dashboard_export(self):
        """Import via CLI, export via dashboard endpoint - cross-method consistency."""
        from zato.common.test.enmasse_._template_complex_01 import template_complex_01

        skip_fields = _time_dependent_fields | _random_fields

        tmp_path = os.path.join(tempfile.gettempdir(), f'zato-dash-cli-{os.getpid()}.yaml')
        try:
            with open(tmp_path, 'w') as f:
                f.write(template_complex_01)

            result = subprocess.run(
                [_ZATO_BIN, 'enmasse', self.server_dir, '--verbose', '--import', '--input', tmp_path],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0,
                f'CLI import failed: {result.stdout[:300]}\n{result.stderr[:300]}')
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        raw_dashboard = self._dashboard_export()
        data_dashboard = yaml.safe_load(raw_dashboard)
        self.assertTrue(data_dashboard, 'Dashboard export is empty after CLI import')

        original_sections = set(yaml.safe_load(template_complex_01).keys())
        for section in original_sections - _skip_sections:
            self.assertIn(section, data_dashboard,
                f'Section "{section}" missing from dashboard export after CLI import')

    def test_05_dashboard_import_cli_export(self):
        """Import via dashboard endpoint, export via CLI - cross-method consistency."""
        from zato.common.test.enmasse_._template_complex_01 import template_complex_01

        skip_fields = _time_dependent_fields | _random_fields

        self._dashboard_import(template_complex_01)

        export_path = os.path.join(tempfile.gettempdir(), f'zato-dash-cli-export-{os.getpid()}.yaml')
        try:
            result = subprocess.run(
                [_ZATO_BIN, 'enmasse', self.server_dir, '--verbose', '--export', '--output', export_path],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0,
                f'CLI export failed: {result.stdout[:300]}\n{result.stderr[:300]}')

            with open(export_path) as f:
                data_cli = yaml.safe_load(f.read())
        finally:
            if os.path.exists(export_path):
                os.remove(export_path)

        self.assertTrue(data_cli, 'CLI export is empty after dashboard import')

        raw_dashboard = self._dashboard_export()
        data_dashboard = yaml.safe_load(raw_dashboard)

        cli_filtered = {k: v for k, v in data_cli.items() if k not in _skip_sections}
        dash_filtered = {k: v for k, v in data_dashboard.items() if k not in _skip_sections}

        norm_cli = _normalize_for_comparison(cli_filtered, skip_fields)
        norm_dash = _normalize_for_comparison(dash_filtered, skip_fields)

        self.assertEqual(norm_cli, norm_dash,
            'CLI export and dashboard export differ after dashboard import')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
