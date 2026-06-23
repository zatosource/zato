# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import subprocess
import tempfile
import threading
import time
from logging import basicConfig, getLogger, WARN
from unittest import main, TestCase

# Zato
from zato.common.test import get_free_tcp_port
from zato.common.test.mcp_ import make_jsonrpc_initialize, wait_for_mcp_channel

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_ZATO_BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_ZATO_BIN = os.path.join(_ZATO_BASE, 'bin', 'zato')

# Credentials for the Basic Auth sec def that will be in the security group
_SEC_DEF_USERNAME = 'test.mcp.group.member'
_SEC_DEF_PASSWORD = 'test-mcp-password-' + os.urandom(4).hex()

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################


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

class TestMCPAuth(TestCase):

    @classmethod
    def setUpClass(cls):

        if not os.path.isfile(_ZATO_BIN):
            raise Exception(f'zato binary not found at {_ZATO_BIN}')

        os.environ.pop('Zato_Needs_Config_Reload', None)

        cls._password = 'test.mcp_auth.' + os.urandom(8).hex()
        cls._port = get_free_tcp_port()
        cls._broker_port = get_free_tcp_port()
        cls._tmpdir = tempfile.mkdtemp(prefix='zato_mcp_auth_test_')
        cls._server_proc = None
        cls._server_output_lines = []

        logger.warning('[MCP-AUTH setUpClass] port=%d broker_port=%d tmpdir=%s',
            cls._port, cls._broker_port, cls._tmpdir)

        # Quickstart ..
        qs_dir = os.path.join(cls._tmpdir, 'qs')
        os.makedirs(qs_dir)

        qs_env = os.environ.copy()
        qs_env.pop('COVERAGE_PROCESS_START', None)

        qs_cmd = [
            _ZATO_BIN, 'quickstart', 'create', qs_dir,
            '--servers', '1',
            '--server-api-client-for-scheduler-password', cls._password,
            '--no-scheduler',
        ]

        logger.warning('[MCP-AUTH setUpClass] Running quickstart create in %s', qs_dir)
        result = subprocess.run(qs_cmd, capture_output=True, text=True, timeout=120, env=qs_env)
        if result.returncode != 0:
            logger.warning('[MCP-AUTH setUpClass] quickstart FAILED: stdout=%s stderr=%s',
                result.stdout[-500:], result.stderr[-500:])
            shutil.rmtree(cls._tmpdir, ignore_errors=True)
            raise Exception(f'quickstart create failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}')

        logger.warning('[MCP-AUTH setUpClass] quickstart OK')

        cls._server_dir = os.path.join(qs_dir, 'server1')
        repo_location = os.path.join(cls._server_dir, 'config', 'repo')

        from zato.common.util.config import get_config_object, update_config_file
        config = get_config_object(repo_location, 'server.conf')
        config['main']['port'] = str(cls._port)
        config['main']['bind'] = f'0.0.0.0:{cls._port}'
        update_config_file(config, repo_location, 'server.conf')

        env = os.environ.copy()
        env['Zato_Config_Bind_Port'] = str(cls._port)
        env['Zato_Broker_HTTP_Port'] = str(cls._broker_port)
        env.pop('COVERAGE_PROCESS_START', None)

        logger.warning('[MCP-AUTH setUpClass] Starting server on port %d', cls._port)
        cls._server_proc = subprocess.Popen(
            [_ZATO_BIN, 'start', cls._server_dir, '--fg'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        logger.warning('[MCP-AUTH setUpClass] Server PID=%d', cls._server_proc.pid)

        def _capture_server():
            for line in iter(cls._server_proc.stdout.readline, b''):
                text = line.decode('utf-8', errors='replace').rstrip()
                cls._server_output_lines.append(text)

        cls._server_thread = threading.Thread(target=_capture_server, daemon=True)
        cls._server_thread.start()

        # Use `zato wait` to block until the server is ready ..
        logger.warning('[MCP-AUTH setUpClass] Running zato wait --path %s', cls._server_dir)
        wait_result = subprocess.run(
            [_ZATO_BIN, 'wait', '--path', cls._server_dir, '--timeout', '60'],
            capture_output=True, text=True, timeout=70,
        )
        if wait_result.returncode != 0:
            logger.warning('[MCP-AUTH setUpClass] zato wait failed: %s %s', wait_result.stdout, wait_result.stderr)
            cls._dump_debug()
            _kill_proc(cls._server_proc)
            raise Exception(f'zato wait failed (exit {wait_result.returncode})')

        logger.warning('[MCP-AUTH setUpClass] Server is ready')

        # Deploy the MCP channel with security group via enmasse ..
        token = os.urandom(4).hex()
        cls._sec_def_name = f'test.mcp.auth.{token}'
        cls._group_name = f'mcp.test-auth-group.{token}'
        cls._channel_name = f'test.mcp.auth-channel.{token}'
        cls._url_path = f'/mcp/test-auth/{token}'

        enmasse_yaml = f'''\
security:
  - name: {cls._sec_def_name}
    type: basic_auth
    username: {_SEC_DEF_USERNAME}
    password: "{_SEC_DEF_PASSWORD}"

groups:
  - name: {cls._group_name}
    members:
      - {cls._sec_def_name}

channel_mcp:
  - name: {cls._channel_name}
    is_active: true
    url_path: {cls._url_path}
    security_groups:
      - {cls._group_name}
'''

        tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-mcp-auth-{os.getpid()}.yaml')
        try:
            with open(tmp_yaml, 'w') as f:
                f.write(enmasse_yaml)

            logger.warning('[MCP-AUTH setUpClass] Running enmasse --import')
            enmasse_result = subprocess.run(
                [_ZATO_BIN, 'enmasse', cls._server_dir, '--verbose', '--import', '--input', tmp_yaml,
                 '--missing-wait-time', '15'],
                capture_output=True, text=True, timeout=60,
            )
            logger.warning('[MCP-AUTH setUpClass] enmasse exit_code=%d', enmasse_result.returncode)
            if enmasse_result.returncode != 0:
                logger.warning('[MCP-AUTH setUpClass] enmasse stdout:\n%s', enmasse_result.stdout[-2000:])
                logger.warning('[MCP-AUTH setUpClass] enmasse stderr:\n%s', enmasse_result.stderr[-2000:])
                cls._dump_debug()
                raise Exception(f'Enmasse import failed (exit {enmasse_result.returncode})')
        finally:
            if os.path.exists(tmp_yaml):
                os.remove(tmp_yaml)

        logger.warning('[MCP-AUTH setUpClass] Enmasse import complete, waiting for channel')

        # Wait until the channel responds (any status other than 404 means it exists) ..
        cls._wait_for_channel_ready()
        logger.warning('[MCP-AUTH setUpClass] Channel is ready at %s', cls._url_path)

    @classmethod
    def _wait_for_channel_ready(cls, timeout=45):
        wait_for_mcp_channel(cls._port, cls._url_path, timeout)

    @classmethod
    def _dump_debug(cls):
        logger.warning('--- Server stdout at failure: ---')
        for line in cls._server_output_lines[-40:]:
            logger.warning(line)
        logger.warning('--- End of server stdout ---')

        server_log = os.path.join(cls._server_dir, 'logs', 'server.log')
        if os.path.isfile(server_log):
            logger.warning('--- server.log tail: ---')
            with open(server_log) as f:
                for line in f.readlines()[-50:]:
                    logger.warning(line.rstrip())
            logger.warning('--- End of server.log ---')

    @classmethod
    def tearDownClass(cls):
        logger.warning('[MCP-AUTH tearDownClass] Stopping server')
        _kill_proc(cls._server_proc)
        cls._server_proc = None
        if cls._tmpdir and os.path.isdir(cls._tmpdir):
            shutil.rmtree(cls._tmpdir, ignore_errors=True)
        cls._tmpdir = None
        logger.warning('[MCP-AUTH tearDownClass] Cleanup complete')

# ################################################################################################################################

    def test_06_group_member_allowed(self):
        """POST JSON-RPC initialize with credentials of a sec def that IS in the channel's security group -> 200."""
        import requests as req_lib

        url = f'http://127.0.0.1:{self._port}{self._url_path}'
        creds = (_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD)

        resp = req_lib.post(
            url,
            data=make_jsonrpc_initialize(),
            headers={'Content-Type': 'application/json'},
            auth=creds,
            timeout=10,
        )

        logger.warning('[test_06] POST %s -> status=%d body=%s', url, resp.status_code, resp.text[:300])

        self.assertEqual(resp.status_code, 200,
            f'Expected 200 for group member, got {resp.status_code}: {resp.text[:500]}')

        body = resp.json()
        self.assertEqual(body['jsonrpc'], '2.0')
        self.assertIn('result', body)
        self.assertIn('serverInfo', body['result'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
