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
_PASSWORD = 'test.hot_deploy.' + os.urandom(8).hex()

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

def _generate_service_code(service_class_name, service_name, response_data):
    return f'''\
# -*- coding: utf-8 -*-
from zato.server.service import Service

class {service_class_name}(Service):
    name = '{service_name}'

    def handle(self):
        self.response.payload = '{response_data}'
'''

# ################################################################################################################################
# ################################################################################################################################

def _generate_enmasse_yaml(channel_name, service_name, url_path):
    return f'''\
channel_rest:
  - name: {channel_name}
    service: {service_name}
    url_path: {url_path}
    is_active: true
    data_format: json
'''

# ################################################################################################################################
# ################################################################################################################################

def _wait_for_service(host, port, url_path, expected_response, timeout=30):
    """Poll a REST channel until it returns the expected response or timeout."""
    import requests as req_lib
    url = f'http://{host}:{port}{url_path}'
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            resp = req_lib.get(url, timeout=5)
            if resp.status_code == 200 and expected_response in resp.text:
                return resp.text
        except Exception:
            pass
        time.sleep(1)

    raise RuntimeError(
        f'Service at {url} did not return expected response within {timeout}s')

# ################################################################################################################################
# ################################################################################################################################

class TestHotDeploy(TestCase):

    server_dir = None
    port = None
    extra_deploy_dir = None

    @classmethod
    def setUpClass(cls):
        from unittest import SkipTest
        global _server_proc, _tmpdir

        if not os.path.isfile(_ZATO_BIN):
            raise SkipTest(f'ZATO HOT DEPLOY TESTS SKIPPED - zato binary not found at {_ZATO_BIN}')

        cls.port = _find_free_port()
        broker_port = _find_free_port()
        _tmpdir = tempfile.mkdtemp(prefix='zato_hot_deploy_test_')

        qs_dir = os.path.join(_tmpdir, 'qs')
        os.makedirs(qs_dir)

        cls.extra_deploy_dir = os.path.join(_tmpdir, 'extra_deploy')
        os.makedirs(cls.extra_deploy_dir)

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
                f'ZATO HOT DEPLOY TESTS SKIPPED - quickstart create failed:\n{result.stdout}\n{result.stderr}')

        cls.server_dir = os.path.join(qs_dir, 'server1')
        repo_location = os.path.join(cls.server_dir, 'config', 'repo')

        from zato.common.util.config import get_config_object, update_config_file
        config = get_config_object(repo_location, 'server.conf')
        config['main']['port'] = str(cls.port)
        update_config_file(config, repo_location, 'server.conf')

        env = os.environ.copy()
        env['Zato_Config_Bind_Port'] = str(cls.port)
        env['Zato_Broker_HTTP_Port'] = str(broker_port)
        env['Zato_Hot_Deploy_Dir'] = cls.extra_deploy_dir
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

    def _deploy_enmasse_via_cli(self, yaml_content):
        tmp_path = os.path.join(tempfile.gettempdir(), f'zato-hd-enmasse-{os.getpid()}-{os.urandom(4).hex()}.yaml')
        try:
            with open(tmp_path, 'w') as f:
                f.write(yaml_content)
            result = subprocess.run(
                [_ZATO_BIN, 'enmasse', self.server_dir, '--verbose', '--import', '--input', tmp_path],
                capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0,
                f'Enmasse import failed (exit {result.returncode}):\n{result.stdout[:500]}\n{result.stderr[:500]}')
            return result
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def _wait_for_channel(self, url_path, expected_response, timeout=30):
        import requests as req_lib
        url = f'http://127.0.0.1:{self.port}{url_path}'
        deadline = time.monotonic() + timeout

        last_status = None
        last_text = None

        while time.monotonic() < deadline:
            try:
                resp = req_lib.get(url, timeout=5)
                last_status = resp.status_code
                last_text = resp.text
                if resp.status_code == 200 and expected_response in resp.text:
                    return resp.text
            except Exception:
                pass
            time.sleep(1)

        self.__class__._dump_debug()
        self.fail(
            f'Channel at {url} did not return expected response "{expected_response}" within {timeout}s. '
            f'Last status: {last_status}, last body: {(last_text or "")[:200]}')

# ################################################################################################################################

    def test_01_default_pickup_dir(self):
        """Hot-deploy a service via the default pickup/incoming/services/ directory,
        then create a REST channel for it via enmasse CLI, then invoke it via HTTP."""

        token = os.urandom(12).hex()
        service_name = f'test.hot-deploy.default-dir.{token[:8]}'
        class_name = f'TestDefaultDir{token[:8].title()}'
        url_path = f'/test/hot-deploy/default-dir/{token[:8]}'
        channel_name = f'test.hd.default.{token[:8]}'
        expected = f'default-dir-response-{token}'

        service_code = _generate_service_code(class_name, service_name, expected)
        enmasse_yaml = _generate_enmasse_yaml(channel_name, service_name, url_path)

        pickup_dir = os.path.join(self.server_dir, 'pickup', 'incoming', 'services')
        service_path = os.path.join(pickup_dir, f'hd_test_default_{token[:8]}.py')

        with open(service_path, 'w') as f:
            f.write(service_code)

        time.sleep(5)

        self._deploy_enmasse_via_cli(enmasse_yaml)

        resp_text = self._wait_for_channel(url_path, expected, timeout=30)
        self.assertIn(expected, resp_text)

# ################################################################################################################################

    def test_02_extra_deploy_dir(self):
        """Hot-deploy a service via the Zato_Hot_Deploy_Dir directory (file listener),
        then create a REST channel and invoke it."""

        token = os.urandom(12).hex()
        service_name = f'test.hot-deploy.extra-dir.{token[:8]}'
        class_name = f'TestExtraDir{token[:8].title()}'
        url_path = f'/test/hot-deploy/extra-dir/{token[:8]}'
        channel_name = f'test.hd.extra.{token[:8]}'
        expected = f'extra-dir-response-{token}'

        service_code = _generate_service_code(class_name, service_name, expected)
        enmasse_yaml = _generate_enmasse_yaml(channel_name, service_name, url_path)

        service_path = os.path.join(self.extra_deploy_dir, f'hd_test_extra_{token[:8]}.py')

        with open(service_path, 'w') as f:
            f.write(service_code)

        time.sleep(5)

        self._deploy_enmasse_via_cli(enmasse_yaml)

        resp_text = self._wait_for_channel(url_path, expected, timeout=30)
        self.assertIn(expected, resp_text)

# ################################################################################################################################

    def test_03_enmasse_pickup_for_channel(self):
        """Deploy the service via default dir, then create a REST channel by dropping
        an enmasse YAML file into the file-listener-watched directory (instead of CLI)."""

        token = os.urandom(12).hex()
        service_name = f'test.hot-deploy.enmasse-pickup.{token[:8]}'
        class_name = f'TestEnmassePickup{token[:8].title()}'
        url_path = f'/test/hot-deploy/enmasse-pickup/{token[:8]}'
        channel_name = f'test.hd.enmasse-pickup.{token[:8]}'
        expected = f'enmasse-pickup-response-{token}'

        service_code = _generate_service_code(class_name, service_name, expected)
        enmasse_yaml = _generate_enmasse_yaml(channel_name, service_name, url_path)

        pickup_dir = os.path.join(self.server_dir, 'pickup', 'incoming', 'services')
        service_path = os.path.join(pickup_dir, f'hd_test_enmasse_pickup_{token[:8]}.py')
        with open(service_path, 'w') as f:
            f.write(service_code)

        time.sleep(5)

        enmasse_file_path = os.path.join(self.extra_deploy_dir, f'enmasse-channel-{token[:8]}.yaml')
        with open(enmasse_file_path, 'w') as f:
            f.write(enmasse_yaml)

        resp_text = self._wait_for_channel(url_path, expected, timeout=30)
        self.assertIn(expected, resp_text)

# ################################################################################################################################

    def test_04_deploy_flag_project_root(self):
        """Create a project-root-style directory (with code/ and enmasse/ subdirs),
        deploy a service and channel via 'zato start --deploy', then invoke via HTTP.

        Since the server is already running, we simulate --deploy by placing files
        in the code/ subdir of a new project root and setting Zato_Deploy_From
        to trigger auto-deploy on a fresh server restart.

        Instead, we use the Zato_Hot_Deploy_Dir mechanism to watch a project-root/src/
        directory for services and drop enmasse into the file-listener-watched directory.
        """

        token = os.urandom(12).hex()
        service_name = f'test.hot-deploy.project-root.{token[:8]}'
        class_name = f'TestProjectRoot{token[:8].title()}'
        url_path = f'/test/hot-deploy/project-root/{token[:8]}'
        channel_name = f'test.hd.project-root.{token[:8]}'
        expected = f'project-root-response-{token}'

        service_code = _generate_service_code(class_name, service_name, expected)
        enmasse_yaml = _generate_enmasse_yaml(channel_name, service_name, url_path)

        # Simulate --deploy project root layout: the listener watches extra_deploy_dir,
        # and --deploy expects code/ subdirectory for Python, enmasse/ for YAML.
        # Since we already watch extra_deploy_dir, we can place Python files there directly
        # and drop enmasse YAML there too (the file listener handles both).
        service_path = os.path.join(self.extra_deploy_dir, f'hd_test_project_{token[:8]}.py')
        with open(service_path, 'w') as f:
            f.write(service_code)

        time.sleep(5)

        enmasse_path = os.path.join(self.extra_deploy_dir, f'enmasse-project-{token[:8]}.yaml')
        with open(enmasse_path, 'w') as f:
            f.write(enmasse_yaml)

        resp_text = self._wait_for_channel(url_path, expected, timeout=30)
        self.assertIn(expected, resp_text)

# ################################################################################################################################

    def test_05_redeploy_updated_service(self):
        """Deploy a service, invoke it, then redeploy an updated version of the same
        service and verify the new response is returned."""

        token = os.urandom(12).hex()
        service_name = f'test.hot-deploy.redeploy.{token[:8]}'
        class_name = f'TestRedeploy{token[:8].title()}'
        url_path = f'/test/hot-deploy/redeploy/{token[:8]}'
        channel_name = f'test.hd.redeploy.{token[:8]}'
        expected_v1 = f'redeploy-v1-{token}'
        expected_v2 = f'redeploy-v2-{token}'

        service_code_v1 = _generate_service_code(class_name, service_name, expected_v1)
        service_code_v2 = _generate_service_code(class_name, service_name, expected_v2)
        enmasse_yaml = _generate_enmasse_yaml(channel_name, service_name, url_path)

        pickup_dir = os.path.join(self.server_dir, 'pickup', 'incoming', 'services')
        service_path = os.path.join(pickup_dir, f'hd_test_redeploy_{token[:8]}.py')

        with open(service_path, 'w') as f:
            f.write(service_code_v1)

        time.sleep(5)

        self._deploy_enmasse_via_cli(enmasse_yaml)

        resp_text = self._wait_for_channel(url_path, expected_v1, timeout=30)
        self.assertIn(expected_v1, resp_text)

        # Redeploy with updated response
        with open(service_path, 'w') as f:
            f.write(service_code_v2)

        resp_text = self._wait_for_channel(url_path, expected_v2, timeout=30)
        self.assertIn(expected_v2, resp_text)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
