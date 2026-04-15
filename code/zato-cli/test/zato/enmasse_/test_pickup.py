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

_ZATO_BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_ZATO_BIN = os.path.join(_ZATO_BASE, 'bin', 'zato')
_PASSWORD = 'test.enmasse.pickup.' + os.urandom(8).hex()

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

def _export_via_cli(zato_bin, server_dir, output_path):
    result = subprocess.run(
        [zato_bin, 'enmasse', server_dir, '--verbose', '--export', '--output', output_path],
        capture_output=True, text=True, timeout=30,
    )
    return result

# ################################################################################################################################
# ################################################################################################################################

def _split_yaml_into_sections(yaml_string):
    data = yaml.safe_load(yaml_string)
    if not data:
        return {}
    out = {}
    for section_name, items in data.items():
        out[section_name] = yaml.dump({section_name: items}, default_flow_style=False, sort_keys=True)
    return out

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

class TestEnmassePickup(TestCase):

    server_dir = None
    port = None
    pickup_dir = None

    @classmethod
    def setUpClass(cls):
        from unittest import SkipTest
        global _server_proc, _tmpdir

        if not os.path.isfile(_ZATO_BIN):
            raise SkipTest(f'ZATO ENMASSE PICKUP TESTS SKIPPED - zato binary not found at {_ZATO_BIN}')

        cls.port = _find_free_port()
        broker_port = _find_free_port()
        _tmpdir = tempfile.mkdtemp(prefix='zato_enmasse_pickup_test_')

        # Quickstart needs an empty directory
        qs_dir = os.path.join(_tmpdir, 'qs')
        os.makedirs(qs_dir)

        # Create the pickup directory. The server's file listener thread will watch
        # directories from the Zato_Hot_Deploy_Dir env var. We point it at this dir.
        cls.pickup_dir = os.path.join(_tmpdir, 'pickup')
        os.makedirs(cls.pickup_dir)

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
                f'ZATO ENMASSE PICKUP TESTS SKIPPED - quickstart create failed:\n{result.stdout}\n{result.stderr}')

        cls.server_dir = os.path.join(qs_dir, 'server1')
        repo_location = os.path.join(cls.server_dir, 'config', 'repo')

        from zato.common.util.config import get_config_object, update_config_file
        config = get_config_object(repo_location, 'server.conf')
        config['main']['port'] = str(cls.port)
        update_config_file(config, repo_location, 'server.conf')

        # Start the server with the pickup directory exposed via Zato_Hot_Deploy_Dir.
        # The server's in-process file listener thread will pick it up automatically.
        env = os.environ.copy()
        env['Zato_Config_Bind_Port'] = str(cls.port)
        env['Zato_Broker_HTTP_Port'] = str(broker_port)
        env['Zato_Hot_Deploy_Dir'] = cls.pickup_dir
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

            _kill_proc(_server_proc)
            raise

    @classmethod
    def tearDownClass(cls):
        global _tmpdir, _server_proc
        _kill_proc(_server_proc)
        _server_proc = None
        if _tmpdir and os.path.isdir(_tmpdir):
            shutil.rmtree(_tmpdir, ignore_errors=True)
        _tmpdir = None

# ################################################################################################################################

    def _export_to_dict(self):
        export_path = os.path.join(tempfile.gettempdir(), f'zato-pickup-export-{os.getpid()}.yaml')
        try:
            result = _export_via_cli(_ZATO_BIN, self.server_dir, export_path)
            self.assertEqual(result.returncode, 0, f'Export failed:\n{result.stdout}\n{result.stderr}')
            if not os.path.isfile(export_path):
                return {}
            with open(export_path) as f:
                content = f.read().strip()
            if not content:
                return {}
            return yaml.safe_load(content) or {}
        finally:
            if os.path.exists(export_path):
                os.remove(export_path)

    def _place_enmasse_file(self, file_name, yaml_content):
        path = os.path.join(self.pickup_dir, file_name)
        with open(path, 'w') as f:
            f.write(yaml_content)
        return path

    def _wait_for_section(self, section_name, expected_count, timeout=30):
        deadline = time.monotonic() + timeout
        last_data = {}
        while time.monotonic() < deadline:
            last_data = self._export_to_dict()
            items = last_data.get(section_name, [])
            if isinstance(items, list) and len(items) >= expected_count:
                return last_data
            time.sleep(2)
        current_count = len(last_data.get(section_name, []))

        print('\n--- Server stdout at time of failure: ---', file=sys.stderr)
        for line in self._server_output_lines[-30:]:
            print(line, file=sys.stderr)
        print('--- End of server stdout ---\n', file=sys.stderr)

        server_log = os.path.join(self.server_dir, 'logs', 'server.log')
        if os.path.isfile(server_log):
            print(f'\n--- server.log tail: ---', file=sys.stderr)
            with open(server_log) as f:
                for line in f.readlines()[-30:]:
                    print(line.rstrip(), file=sys.stderr)
            print('--- End of server.log ---\n', file=sys.stderr)

        print(f'\n--- Pickup directory {self.pickup_dir}: ---', file=sys.stderr)
        for item in os.listdir(self.pickup_dir):
            print(f'  {item}', file=sys.stderr)
        print('--- End of pickup directory ---\n', file=sys.stderr)

        self.fail(
            f'Timeout waiting for section "{section_name}" to have {expected_count} items, '
            f'got {current_count}. Current data sections: {list(last_data.keys())}')

# ################################################################################################################################

    def test_pickup_incremental_and_edit(self):
        """ Test the full pickup lifecycle:
        1. Export from empty server - should be empty (or just defaults)
        2. Place enmasse files one by one, verify each is picked up incrementally
        3. Place modified versions to trigger Edit, verify changes are visible
        """
        from zato.common.test.enmasse_._template_complex_01 import template_complex_01

        skip_fields = _time_dependent_fields | _random_fields
        skip_sections = frozenset(['pubsub_permission', 'pubsub_subscription'])

        # Step 1: baseline export from empty server
        baseline = self._export_to_dict()

        # Step 2: split the big template into per-section YAML files and place them one by one.
        # Security must come first because other sections reference it.
        sections = _split_yaml_into_sections(template_complex_01)

        section_order = []
        if 'security' in sections:
            section_order.append('security')
        if 'groups' in sections:
            section_order.append('groups')
        for name in sorted(sections.keys()):
            if name not in section_order:
                section_order.append(name)

        cumulative_sections = set()

        for section_name in section_order:
            yaml_content = sections[section_name]
            original_data = yaml.safe_load(yaml_content)
            expected_count = len(original_data[section_name])

            file_name = f'enmasse-{section_name}.yaml'
            self._place_enmasse_file(file_name, yaml_content)

            cumulative_sections.add(section_name)

            data = self._wait_for_section(section_name, expected_count, timeout=30)

            for prev_section in cumulative_sections:
                if prev_section in skip_sections:
                    continue
                self.assertIn(prev_section, data,
                    f'Section "{prev_section}" disappeared after placing "{section_name}"')

        # Step 3: full export after all files placed
        full_data_round1 = self._export_to_dict()
        self.assertTrue(full_data_round1, 'Full export after all files placed is empty')

        for section_name in section_order:
            if section_name in skip_sections:
                continue
            self.assertIn(section_name, full_data_round1,
                f'Section "{section_name}" missing from full export')

        # Step 4: place modified versions to trigger edits
        for section_name in section_order:
            if section_name in skip_sections:
                continue

            yaml_content = sections[section_name]
            original_data = yaml.safe_load(yaml_content)
            items = original_data[section_name]

            modified_items = []
            for item in items:
                item = dict(item)
                if 'description' in item:
                    item['description'] = item['description'] + '-edited'
                elif section_name == 'elastic_search':
                    item['timeout'] = item.get('timeout', 30) + 100
                elif section_name in ('outgoing_rest', 'outgoing_soap'):
                    item['timeout'] = item.get('timeout', 10) + 100
                elif section_name == 'sql':
                    item['pool_size'] = item.get('pool_size', 10) + 5
                elif section_name == 'cache':
                    item['extend_expiry_on_get'] = not item.get('extend_expiry_on_get', True)
                elif section_name in ('security', 'groups'):
                    pass
                else:
                    item['is_active'] = not item.get('is_active', True)
                modified_items.append(item)

            modified_yaml = yaml.dump({section_name: modified_items}, default_flow_style=False, sort_keys=True)
            file_name = f'enmasse-{section_name}.yaml'
            self._place_enmasse_file(file_name, modified_yaml)

        # Wait for edits to be picked up
        time.sleep(15)

        full_data_round2 = self._export_to_dict()
        self.assertTrue(full_data_round2, 'Full export after edits is empty')

        # Verify edits took effect for verifiable sections
        if 'elastic_search' in full_data_round2:
            for item in full_data_round2['elastic_search']:
                timeout = item.get('timeout', 0)
                self.assertGreaterEqual(timeout, 100,
                    f'elastic_search timeout should have been edited to >= 100, got {timeout}')

        if 'outgoing_rest' in full_data_round2:
            edited_timeouts = [item.get('timeout', 0) for item in full_data_round2['outgoing_rest']
                               if item.get('timeout', 0) > 100]
            self.assertTrue(len(edited_timeouts) > 0,
                'Expected at least one outgoing_rest with edited timeout > 100')

        for section_name in section_order:
            if section_name in skip_sections:
                continue
            self.assertIn(section_name, full_data_round2,
                f'Section "{section_name}" missing after edits')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
