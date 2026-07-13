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

# Zato
from zato.common.test.process_util import kill_process_tree

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_ZATO_BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_ZATO_BIN = os.path.join(_ZATO_BASE, 'bin', 'zato')
_PYTHON_BIN = os.path.join(_ZATO_BASE, 'bin', 'py')
_LISTENER_PATH = os.path.join(_ZATO_BASE, 'zato-common', 'src', 'zato', 'common', 'file_transfer', 'listener.py')
_PASSWORD = 'test.enmasse.pickup.' + os.urandom(8).hex()

_server_proc = None
_listener_proc = None
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
    kill_process_tree(proc)

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

        # We will use the server's own pickup directory for enmasse files.
        # The file listener watches this directory and processes enmasse YAML files
        # via the server's REST API, just like in production.

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
        cls.pickup_dir = os.path.join(cls.server_dir, 'pickup', 'incoming', 'services')
        repo_location = os.path.join(cls.server_dir, 'config', 'repo')

        from zato.common.util.config import get_config_object, update_config_file
        config = get_config_object(repo_location, 'server.conf')
        config['main']['port'] = str(cls.port)
        config['main']['bind'] = f'0.0.0.0:{cls.port}'
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
            start_new_session=True,
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

        # .. start the file listener for the pickup directory ..
        global _listener_proc

        listener_env = os.environ.copy()
        listener_env['Zato_Config_Bind_Port'] = str(cls.port)
        listener_env['Zato_Web_Admin_Repo_Dir'] = os.path.join(qs_dir, 'web-admin', 'config', 'repo')
        listener_env.pop('COVERAGE_PROCESS_START', None)

        _listener_proc = subprocess.Popen(
            [_PYTHON_BIN, _LISTENER_PATH, cls.pickup_dir],
            env=listener_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

        # .. give the listener time to initialize.
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        global _tmpdir, _server_proc, _listener_proc

        # Stop the listener and close its stdout pipe - nothing reads it, so it can be closed right away ..
        _kill_proc(_listener_proc)
        _listener_proc.stdout.close()
        _listener_proc = None

        # .. stop the server, wait for the capture thread to drain the pipe and only then close it,
        # .. otherwise close() could block on the buffered reader's lock held by the thread ..
        _kill_proc(_server_proc)
        cls._server_thread.join(timeout=5)
        _server_proc.stdout.close()
        _server_proc = None

        # .. and remove the temporary directory.
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

    def _wait_for_named_item(self, section_name, item_name, timeout=30):
        """ Polls the export until a specific named item appears in a section.
        """
        deadline = time.monotonic() + timeout
        last_data = {}
        while time.monotonic() < deadline:
            last_data = self._export_to_dict()
            items = last_data.get(section_name, [])
            names = [item['name'] for item in items if isinstance(item, dict) and 'name' in item]
            if item_name in names:
                return last_data
            time.sleep(2)

        print('\n--- Server stdout at time of failure: ---', file=sys.stderr)
        for line in self._server_output_lines[-30:]:
            print(line, file=sys.stderr)
        print('--- End of server stdout ---\n', file=sys.stderr)

        server_log = os.path.join(self.server_dir, 'logs', 'server.log')
        if os.path.isfile(server_log):
            print('\n--- server.log tail: ---', file=sys.stderr)
            with open(server_log) as f:
                for line in f.readlines()[-30:]:
                    print(line.rstrip(), file=sys.stderr)
            print('--- End of server.log ---\n', file=sys.stderr)

        print(f'\n--- Pickup directory {self.pickup_dir}: ---', file=sys.stderr)
        for item in os.listdir(self.pickup_dir):
            print(f'  {item}', file=sys.stderr)
        print('--- End of pickup directory ---\n', file=sys.stderr)

        self.fail(
            f'Timeout waiting for item "{item_name}" in section "{section_name}". '
            f'Current data sections: {list(last_data.keys())}')

# ################################################################################################################################

    def test_pickup_incremental_and_edit(self):
        """ Test the full pickup lifecycle:
        1. Export from empty server - should be empty (or just defaults)
        2. Place a single enmasse file, verify all sections are picked up
        3. Place a modified version to trigger Edit, verify changes are visible
        """
        from zato.common.test.enmasse_._template_complex_01 import template_complex_01

        skip_sections = frozenset(['pubsub_permission', 'pubsub_subscription'])

        # Step 1: baseline export from empty server
        _ = self._export_to_dict()

        # Step 2: place the full template as a single enmasse file
        self._place_enmasse_file('enmasse.yaml', template_complex_01)

        # .. parse the template to know what sections to expect ..
        template_data = yaml.safe_load(template_complex_01)
        section_names = [name for name in template_data.keys() if name not in skip_sections]

        # .. wait for channel_rest.4 which depends on security groups,
        # so if it's there, everything before it succeeded too ..
        data = self._wait_for_named_item('channel_rest', 'enmasse.channel.rest.4', timeout=30)

        # .. verify all sections are present ..
        for section_name in section_names:
            self.assertIn(section_name, data, f'Section "{section_name}" missing from export')

        # Step 3: place a modified version to trigger edits
        modified_data = {}

        for section_name, items in template_data.items():
            if section_name in skip_sections:
                modified_data[section_name] = items
                continue

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
                elif section_name in ('security', 'groups'):
                    pass
                else:
                    item['is_active'] = not item.get('is_active', True)
                modified_items.append(item)
            modified_data[section_name] = modified_items

        modified_yaml = yaml.dump(modified_data, default_flow_style=False, sort_keys=True)
        self._place_enmasse_file('enmasse.yaml', modified_yaml)

        # .. wait for edits to be picked up ..
        time.sleep(15)

        full_data_round2 = self._export_to_dict()
        self.assertTrue(full_data_round2, 'Full export after edits is empty')

        # .. verify edits took effect for verifiable sections ..
        for item in full_data_round2['elastic_search']:
            self.assertGreaterEqual(item['timeout'], 100,
                f'elastic_search timeout should have been edited to >= 100, got {item["timeout"]}')

        edited_timeouts = [item['timeout'] for item in full_data_round2['outgoing_rest']
                           if item['timeout'] > 100]
        self.assertTrue(len(edited_timeouts) > 0,
            'Expected at least one outgoing_rest with edited timeout > 100')

        for section_name in section_names:
            self.assertIn(section_name, full_data_round2,
                f'Section "{section_name}" missing after edits')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
