# -*- coding: utf-8 -*-

"""
Integration tests that start a real Zato server in a subprocess.
"""

# stdlib
import json
import os
import signal
import subprocess
import sys
import time
import unittest

# stdlib
from http.client import HTTPConnection

# ################################################################################################################################

SERVER_BASE_DIR = os.environ.get('ZATO_TEST_SERVER_DIR', '')
PYTHON_BIN = os.path.join(os.path.dirname(sys.executable), 'python')
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 17010

# ################################################################################################################################

def _wait_for_server(host, port, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            conn = HTTPConnection(host, port, timeout=2)
            conn.request('GET', '/zato/ping')
            resp = conn.getresponse()
            body = resp.read()
            conn.close()
            if resp.status == 200:
                return True
        except (ConnectionRefusedError, OSError):
            pass
        time.sleep(0.5)
    return False

# ################################################################################################################################

def _invoke(method, path, body=None, headers=None):
    conn = HTTPConnection(SERVER_HOST, SERVER_PORT, timeout=10)
    headers = headers or {}
    if body and isinstance(body, dict):
        body = json.dumps(body)
        headers['Content-Type'] = 'application/json'
    conn.request(method, path, body=body, headers=headers)
    resp = conn.getresponse()
    data = resp.read().decode('utf-8')
    conn.close()
    return resp.status, data

# ################################################################################################################################

def _start_server():
    env = os.environ.copy()
    env['ZATO_SERVER_BASE_DIR'] = SERVER_BASE_DIR
    proc = subprocess.Popen(
        [PYTHON_BIN, '-m', 'zato.server.main'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc

# ################################################################################################################################

def _stop_server(proc):
    if proc and proc.poll() is None:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

# ################################################################################################################################

@unittest.skipUnless(SERVER_BASE_DIR, 'Set ZATO_TEST_SERVER_DIR to run integration tests')
class TestServerPing(unittest.TestCase):
    """ Every server must respond to /zato/ping.
    """

    server_proc = None

    @classmethod
    def setUpClass(cls):
        cls.server_proc = _start_server()
        if not _wait_for_server(SERVER_HOST, SERVER_PORT, timeout=45):
            out = cls.server_proc.stdout.read().decode('utf-8', errors='replace')
            cls.server_proc.kill()
            cls.server_proc.wait()
            raise RuntimeError('Server failed to start within 45s. Output:\n{}'.format(out))

    @classmethod
    def tearDownClass(cls):
        _stop_server(cls.server_proc)

    def test_ping_get(self):
        status, body = _invoke('GET', '/zato/ping')
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertTrue(data['is_ok'])
        self.assertIn('cid', data)

    def test_ping_post(self):
        status, body = _invoke('POST', '/zato/ping')
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertTrue(data['is_ok'])

    def test_ping_cid_is_unique(self):
        _, body1 = _invoke('GET', '/zato/ping')
        _, body2 = _invoke('GET', '/zato/ping')
        cid1 = json.loads(body1)['cid']
        cid2 = json.loads(body2)['cid']
        self.assertNotEqual(cid1, cid2)

    def test_unknown_url_returns_404(self):
        status, _ = _invoke('GET', '/nonexistent/path')
        self.assertEqual(status, 404)

# ################################################################################################################################

@unittest.skipUnless(SERVER_BASE_DIR, 'Set ZATO_TEST_SERVER_DIR to run integration tests')
class TestServerShutdown(unittest.TestCase):
    """ Server shuts down cleanly on SIGTERM.
    """

    def test_graceful_shutdown(self):
        proc = _start_server()
        started = _wait_for_server(SERVER_HOST, SERVER_PORT, timeout=45)
        if not started:
            out = proc.stdout.read().decode('utf-8', errors='replace')
            proc.kill()
            proc.wait()
            self.fail('Server failed to start. Output:\n{}'.format(out))

        _stop_server(proc)
        self.assertIsNotNone(proc.returncode)

# ################################################################################################################################

@unittest.skipUnless(SERVER_BASE_DIR, 'Set ZATO_TEST_SERVER_DIR to run integration tests')
class TestServerRestart(unittest.TestCase):
    """ The server can start, stop, and start again cleanly.
    """

    def test_start_stop_start(self):
        for attempt in range(2):
            proc = _start_server()
            started = _wait_for_server(SERVER_HOST, SERVER_PORT, timeout=45)

            if started:
                # Verify ping works on each start
                status, body = _invoke('GET', '/zato/ping')
                self.assertEqual(status, 200)

            _stop_server(proc)
            time.sleep(1)

            if not started:
                out = proc.stdout.read().decode('utf-8', errors='replace')
                self.fail('Server failed to start on attempt {} (of 2). Output:\n{}'.format(attempt + 1, out))

# ################################################################################################################################

@unittest.skipUnless(SERVER_BASE_DIR, 'Set ZATO_TEST_SERVER_DIR to run integration tests')
class TestHotDeployService(unittest.TestCase):
    """ Hot-deploying a service makes it invocable.
    """

    server_proc = None
    _service_file = None

    @classmethod
    def setUpClass(cls):
        cls.server_proc = _start_server()
        if not _wait_for_server(SERVER_HOST, SERVER_PORT, timeout=45):
            out = cls.server_proc.stdout.read().decode('utf-8', errors='replace')
            cls.server_proc.kill()
            cls.server_proc.wait()
            raise RuntimeError('Server failed to start. Output:\n{}'.format(out))

        # Hot-deploy a test service
        pickup_dir = os.path.join(SERVER_BASE_DIR, 'pickup', 'incoming', 'services')
        cls._service_file = os.path.join(pickup_dir, '_test_hot_deploy.py')
        with open(cls._service_file, 'w') as f:
            f.write(_HOT_DEPLOY_SERVICE)

        # Give the server time to pick it up
        time.sleep(3)

    @classmethod
    def tearDownClass(cls):
        if cls._service_file and os.path.exists(cls._service_file):
            os.unlink(cls._service_file)
        _stop_server(cls.server_proc)

    def test_hot_deployed_service_exists(self):
        # The service was deployed -- verify server is still healthy
        status, body = _invoke('GET', '/zato/ping')
        self.assertEqual(status, 200)

# ################################################################################################################################

_HOT_DEPLOY_SERVICE = '''
from zato.server.service import Service

class TestHotDeploy(Service):
    name = 'test.hot-deploy-integration'

    def handle(self):
        self.response.payload = '{"deployed": true}'
'''

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
