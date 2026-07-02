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
from http.client import FORBIDDEN, OK
from logging import basicConfig, getLogger, INFO
from unittest import main, TestCase

# requests
import requests

# Zato
from zato.common.test import get_free_tcp_port
from zato.common.test.mcp_ import make_jsonrpc_initialize, wait_for_mcp_channel
from zato.common.util.config import get_config_object, update_config_file

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_ZATO_BASE = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_ZATO_BIN = os.path.join(_ZATO_BASE, 'bin', 'zato')

_SEC_DEF_USERNAME = 'test.mcp.group.member'
_SEC_DEF_PASSWORD = 'test-mcp-password-' + os.urandom(4).hex()

_NON_MEMBER_USERNAME = 'test.mcp.non.member'
_NON_MEMBER_PASSWORD = 'test-mcp-outsider-' + os.urandom(4).hex()

_GROUP2_MEMBER_USERNAME = 'test.mcp.group2.member'
_GROUP2_MEMBER_PASSWORD = 'test-mcp-group2-' + os.urandom(4).hex()

# ################################################################################################################################
# ################################################################################################################################

def _kill_proc(proc:'any_') -> 'None':
    if proc:
        if proc.poll() is None:
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
    def setUpClass(cls) -> 'None':

        if not os.path.isfile(_ZATO_BIN):
            raise Exception(f'zato binary not found at {_ZATO_BIN}')

        os.environ.pop('Zato_Needs_Config_Reload', None)

        cls._password = 'test.mcp_auth.' + os.urandom(8).hex()
        cls._port = get_free_tcp_port()
        cls._broker_port = get_free_tcp_port()
        cls._tmpdir = tempfile.mkdtemp(prefix='zato_mcp_auth_test_')
        cls._server_proc = None
        cls._server_output_lines = []

        logger.info('[MCP-AUTH setUpClass] port=%d broker_port=%d tmpdir=%s',
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

        logger.info('[MCP-AUTH setUpClass] Running quickstart create in %s', qs_dir)
        result = subprocess.run(qs_cmd, capture_output=True, text=True, timeout=120, env=qs_env)

        if result.returncode != 0:
            logger.info('[MCP-AUTH setUpClass] quickstart FAILED: stdout=%s stderr=%s',
                result.stdout, result.stderr)
            shutil.rmtree(cls._tmpdir, ignore_errors=True)
            raise Exception(f'quickstart create failed:\n{result.stdout}\n{result.stderr}')

        logger.info('[MCP-AUTH setUpClass] quickstart OK')

        # .. configure the server port ..
        cls._server_dir = os.path.join(qs_dir, 'server1')
        repo_location = os.path.join(cls._server_dir, 'config', 'repo')

        config = get_config_object(repo_location, 'server.conf')
        config['main']['port'] = str(cls._port)
        config['main']['bind'] = f'0.0.0.0:{cls._port}'
        update_config_file(config, repo_location, 'server.conf')

        env = os.environ.copy()
        env['Zato_Config_Bind_Port'] = str(cls._port)
        env['Zato_Broker_HTTP_Port'] = str(cls._broker_port)
        env.pop('COVERAGE_PROCESS_START', None)

        # .. start the server in foreground ..
        logger.info('[MCP-AUTH setUpClass] Starting server on port %d', cls._port)
        cls._server_proc = subprocess.Popen(
            [_ZATO_BIN, 'start', cls._server_dir, '--fg'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        logger.info('[MCP-AUTH setUpClass] Server PID=%d', cls._server_proc.pid)

        def _capture_server() -> 'None':
            for line in iter(cls._server_proc.stdout.readline, b''):
                text = line.decode('utf-8', errors='replace').rstrip()
                cls._server_output_lines.append(text)

        cls._server_thread = threading.Thread(target=_capture_server, daemon=True)
        cls._server_thread.start()

        # .. use `zato wait` to block until the server is ready ..
        logger.info('[MCP-AUTH setUpClass] Running zato wait --path %s', cls._server_dir)
        wait_result = subprocess.run(
            [_ZATO_BIN, 'wait', '--path', cls._server_dir, '--timeout', '60'],
            capture_output=True, text=True, timeout=70,
        )

        if wait_result.returncode != 0:
            logger.info('[MCP-AUTH setUpClass] zato wait failed: %s %s', wait_result.stdout, wait_result.stderr)
            cls._dump_debug()
            _kill_proc(cls._server_proc)
            raise Exception(f'zato wait failed (exit {wait_result.returncode})')

        logger.info('[MCP-AUTH setUpClass] Server is ready')

        # .. deploy MCP channels via enmasse ..
        token = os.urandom(4).hex()
        cls._sec_def_name = f'test.mcp.auth.{token}'
        cls._group_name = f'mcp.test-auth-group.{token}'
        cls._channel_name = f'test.mcp.auth-channel.{token}'
        cls._url_path = f'/mcp/test-auth/{token}'

        # .. a second sec def that is NOT in any group ..
        cls._non_member_sec_def_name = f'test.mcp.outsider.{token}'

        # .. a third sec def in a second group ..
        cls._group2_sec_def_name = f'test.mcp.group2member.{token}'
        cls._group2_name = f'mcp.test-auth-group2.{token}'

        # .. a channel with two security groups ..
        cls._multi_group_channel_name = f'test.mcp.multi-group.{token}'
        cls._multi_group_url_path = f'/mcp/test-multi-group/{token}'

        # .. a channel with no security groups at all ..
        cls._no_group_channel_name = f'test.mcp.no-group.{token}'
        cls._no_group_url_path = f'/mcp/test-no-group/{token}'

        # .. a channel dedicated to the membership update test ..
        cls._update_channel_name = f'test.mcp.update.{token}'
        cls._update_url_path = f'/mcp/test-update/{token}'
        cls._update_group_name = f'mcp.test-update-group.{token}'

        # .. a deactivated channel with its own group ..
        cls._inactive_channel_name = f'test.mcp.inactive.{token}'
        cls._inactive_url_path = f'/mcp/test-inactive/{token}'
        cls._inactive_group_name = f'mcp.test-inactive-group.{token}'

        # .. a channel dedicated to the rename test ..
        cls._rename_channel_name = f'test.mcp.rename.{token}'
        cls._rename_url_path = f'/mcp/test-rename/{token}'
        cls._rename_new_url_path = f'/mcp/test-rename-new/{token}'
        cls._rename_group_name = f'mcp.test-rename-group.{token}'

        # .. a channel dedicated to the delete test ..
        cls._delete_channel_name = f'test.mcp.delete.{token}'
        cls._delete_url_path = f'/mcp/test-delete/{token}'
        cls._delete_group_name = f'mcp.test-delete-group.{token}'

        # .. a path that does not correspond to any channel ..
        cls._nonexistent_url_path = f'/mcp/test-nonexistent/{token}'

        enmasse_yaml = f'''\
security:
  - name: {cls._sec_def_name}
    type: basic_auth
    username: {_SEC_DEF_USERNAME}
    password: "{_SEC_DEF_PASSWORD}"

  - name: {cls._non_member_sec_def_name}
    type: basic_auth
    username: {_NON_MEMBER_USERNAME}
    password: "{_NON_MEMBER_PASSWORD}"

  - name: {cls._group2_sec_def_name}
    type: basic_auth
    username: {_GROUP2_MEMBER_USERNAME}
    password: "{_GROUP2_MEMBER_PASSWORD}"

groups:
  - name: {cls._group_name}
    members:
      - {cls._sec_def_name}

  - name: {cls._group2_name}
    members:
      - {cls._group2_sec_def_name}

  - name: {cls._inactive_group_name}
    members:
      - {cls._sec_def_name}

  - name: {cls._update_group_name}
    members:
      - {cls._sec_def_name}

  - name: {cls._rename_group_name}
    members:
      - {cls._sec_def_name}

  - name: {cls._delete_group_name}
    members:
      - {cls._sec_def_name}

channel_mcp:
  - name: {cls._channel_name}
    is_active: true
    url_path: {cls._url_path}
    security_groups:
      - {cls._group_name}

  - name: {cls._multi_group_channel_name}
    is_active: true
    url_path: {cls._multi_group_url_path}
    security_groups:
      - {cls._group_name}
      - {cls._group2_name}

  - name: {cls._no_group_channel_name}
    is_active: true
    url_path: {cls._no_group_url_path}

  - name: {cls._update_channel_name}
    is_active: true
    url_path: {cls._update_url_path}
    security_groups:
      - {cls._update_group_name}

  - name: {cls._rename_channel_name}
    is_active: true
    url_path: {cls._rename_url_path}
    security_groups:
      - {cls._rename_group_name}

  - name: {cls._delete_channel_name}
    is_active: true
    url_path: {cls._delete_url_path}
    security_groups:
      - {cls._delete_group_name}

  - name: {cls._inactive_channel_name}
    is_active: false
    url_path: {cls._inactive_url_path}
    security_groups:
      - {cls._inactive_group_name}
'''

        tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-mcp-auth-{os.getpid()}.yaml')

        try:
            with open(tmp_yaml, 'w') as yaml_file:
                yaml_file.write(enmasse_yaml)

            logger.info('[MCP-AUTH setUpClass] Running enmasse --import')
            enmasse_result = subprocess.run(
                [_ZATO_BIN, 'enmasse', cls._server_dir, '--verbose', '--import', '--input', tmp_yaml,
                 '--missing-wait-time', '15'],
                capture_output=True, text=True, timeout=60,
            )
            logger.info('[MCP-AUTH setUpClass] enmasse exit_code=%d', enmasse_result.returncode)

            if enmasse_result.returncode != 0:
                logger.info('[MCP-AUTH setUpClass] enmasse stdout:\n%s', enmasse_result.stdout)
                logger.info('[MCP-AUTH setUpClass] enmasse stderr:\n%s', enmasse_result.stderr)
                cls._dump_debug()
                raise Exception(f'Enmasse import failed (exit {enmasse_result.returncode})')

        finally:
            if os.path.exists(tmp_yaml):
                os.remove(tmp_yaml)

        logger.info('[MCP-AUTH setUpClass] Enmasse import complete, waiting for channels')

        # .. wait until all channels respond.
        wait_for_mcp_channel(cls._port, cls._url_path)
        logger.info('[MCP-AUTH setUpClass] Secured channel is ready at %s', cls._url_path)

        wait_for_mcp_channel(cls._port, cls._multi_group_url_path)
        logger.info('[MCP-AUTH setUpClass] Multi-group channel is ready at %s', cls._multi_group_url_path)

        wait_for_mcp_channel(cls._port, cls._no_group_url_path)
        logger.info('[MCP-AUTH setUpClass] No-group channel is ready at %s', cls._no_group_url_path)

        wait_for_mcp_channel(cls._port, cls._update_url_path)
        logger.info('[MCP-AUTH setUpClass] Update channel is ready at %s', cls._update_url_path)

        wait_for_mcp_channel(cls._port, cls._rename_url_path)
        logger.info('[MCP-AUTH setUpClass] Rename channel is ready at %s', cls._rename_url_path)

        wait_for_mcp_channel(cls._port, cls._delete_url_path)
        logger.info('[MCP-AUTH setUpClass] Delete channel is ready at %s', cls._delete_url_path)

# ################################################################################################################################

    @classmethod
    def _dump_debug(cls) -> 'None':
        logger.info('--- Server stdout at failure: ---')

        for line in cls._server_output_lines[-40:]:
            logger.info(line)

        logger.info('--- End of server stdout ---')

        server_log = os.path.join(cls._server_dir, 'logs', 'server.log')

        if os.path.isfile(server_log):
            logger.info('--- server.log tail: ---')
            with open(server_log) as log_file:
                for line in log_file.readlines()[-50:]:
                    logger.info(line.rstrip())
            logger.info('--- End of server.log ---')

# ################################################################################################################################

    @classmethod
    def tearDownClass(cls) -> 'None':
        logger.info('[MCP-AUTH tearDownClass] Stopping server')
        _kill_proc(cls._server_proc)
        cls._server_proc = None

        if cls._tmpdir:
            if os.path.isdir(cls._tmpdir):
                shutil.rmtree(cls._tmpdir, ignore_errors=True)

        cls._tmpdir = None
        logger.info('[MCP-AUTH tearDownClass] Cleanup complete')

# ################################################################################################################################

    def _post_mcp(self, url_path:'str', auth:'tuple | None'=None) -> 'requests.Response':
        """ Posts a JSON-RPC initialize request to the given MCP URL path.
        """
        url = f'http://127.0.0.1:{self._port}{url_path}'
        data = make_jsonrpc_initialize()
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, data=data, headers=headers, auth=auth, timeout=10)

        logger.info('[_post_mcp] POST %s auth=%s -> status=%d', url_path, auth[0] if auth else None,
            response.status_code)

        return response

# ################################################################################################################################

    def _run_enmasse(self, yaml_content:'str') -> 'None':
        """ Runs enmasse --import with the given YAML content against the test server.
        """
        tmp_yaml = os.path.join(tempfile.gettempdir(), f'zato-mcp-auth-mid-{os.getpid()}-{os.urandom(4).hex()}.yaml')

        try:
            with open(tmp_yaml, 'w') as yaml_file:
                yaml_file.write(yaml_content)

            result = subprocess.run(
                [_ZATO_BIN, 'enmasse', self._server_dir, '--verbose', '--import', '--input', tmp_yaml,
                 '--missing-wait-time', '15'],
                capture_output=True, text=True, timeout=60,
            )
            logger.info('[_run_enmasse] exit_code=%d', result.returncode)

            if result.returncode != 0:
                logger.info('[_run_enmasse] stdout:\n%s', result.stdout)
                logger.info('[_run_enmasse] stderr:\n%s', result.stderr)
                self.fail(f'Enmasse import failed (exit {result.returncode})')

        finally:
            if os.path.exists(tmp_yaml):
                os.remove(tmp_yaml)

# ################################################################################################################################

    def _invoke_service(self, service_name:'str', payload:'dict') -> 'any_':
        """ Invokes a Zato service via the admin API and returns the response data.
        """
        import json

        url = f'http://127.0.0.1:{self._port}/zato/api/invoke/{service_name}'
        auth = ('admin.invoke', self._password)
        headers = {'Content-Type': 'application/json'}
        data = json.dumps(payload)

        response = requests.post(url, data=data, headers=headers, auth=auth, timeout=10)

        logger.info('[_invoke_service] %s -> status=%d body_len=%d', service_name, response.status_code,
            len(response.content))

        self.assertEqual(response.status_code, OK,
            f'Service {service_name} failed: {response.status_code} {response.text}')

        if response.content:
            try:
                return response.json()
            except Exception:
                return response.text

        return None

# ################################################################################################################################

    def _get_generic_conn(self, channel_name:'str') -> 'dict':
        """ Looks up a GenericConn by name via the API, returns the full item dict.
        """
        from zato.common.api import GENERIC

        response_data = self._invoke_service('zato.generic.connection.get-list', {
            'cluster_id': 1,
            'type_': GENERIC.CONNECTION.TYPE.CHANNEL_MCP,
            'query': channel_name,
        })

        for item in response_data:
            if item['name'] == channel_name:
                return item

        self.fail(f'GenericConn not found: {channel_name}')

# ################################################################################################################################

    def test_group_member_allowed(self) -> 'None':
        """ POST JSON-RPC initialize with credentials of a sec def that IS in the channel's security group -> 200.
        """
        response = self._post_mcp(self._url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))

        self.assertEqual(response.status_code, OK,
            f'Expected OK for group member, got {response.status_code}: {response.text}')

        body = response.json()
        self.assertEqual(body['jsonrpc'], '2.0')
        self.assertIn('result', body)
        self.assertIn('serverInfo', body['result'])

# ################################################################################################################################

    def test_non_member_rejected(self) -> 'None':
        """ POST JSON-RPC initialize with creds of a sec def NOT in the channel's group -> 403.
        """
        response = self._post_mcp(self._url_path, auth=(_NON_MEMBER_USERNAME, _NON_MEMBER_PASSWORD))

        self.assertEqual(response.status_code, FORBIDDEN,
            f'Expected FORBIDDEN for non-member, got {response.status_code}: {response.text}')

# ################################################################################################################################

    def test_multiple_groups(self) -> 'None':
        """ Channel with two security groups - member of either group can access.
        """

        # .. member of group 1 should get through ..
        response = self._post_mcp(self._multi_group_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))

        self.assertEqual(response.status_code, OK,
            f'Expected OK for group1 member, got {response.status_code}: {response.text}')

        # .. member of group 2 should also get through ..
        response = self._post_mcp(self._multi_group_url_path, auth=(_GROUP2_MEMBER_USERNAME, _GROUP2_MEMBER_PASSWORD))

        self.assertEqual(response.status_code, OK,
            f'Expected OK for group2 member, got {response.status_code}: {response.text}')

        # .. non-member should be rejected ..
        response = self._post_mcp(self._multi_group_url_path, auth=(_NON_MEMBER_USERNAME, _NON_MEMBER_PASSWORD))

        self.assertEqual(response.status_code, FORBIDDEN,
            f'Expected FORBIDDEN for non-member, got {response.status_code}: {response.text}')

# ################################################################################################################################

    def test_no_group_rejects_all(self) -> 'None':
        """ POST JSON-RPC initialize to a channel with no security groups -> 403.
        """
        response = self._post_mcp(self._no_group_url_path)

        self.assertEqual(response.status_code, FORBIDDEN,
            f'Expected FORBIDDEN for no-group channel, got {response.status_code}: {response.text}')

# ################################################################################################################################

    def test_update_group_membership(self) -> 'None':
        """ Remove sec def A from group, add sec def B. Old creds (A) -> 403, new creds (B) -> 200.
        """

        # .. first confirm member A can access the dedicated update channel ..
        response = self._post_mcp(self._update_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))
        self.assertEqual(response.status_code, OK)

        # .. now update the group: remove A, add B ..
        updated_yaml = f'''\
security:
  - name: {self._sec_def_name}
    type: basic_auth
    username: {_SEC_DEF_USERNAME}
    password: "{_SEC_DEF_PASSWORD}"

  - name: {self._non_member_sec_def_name}
    type: basic_auth
    username: {_NON_MEMBER_USERNAME}
    password: "{_NON_MEMBER_PASSWORD}"

groups:
  - name: {self._update_group_name}
    members:
      - {self._non_member_sec_def_name}

channel_mcp:
  - name: {self._update_channel_name}
    is_active: true
    url_path: {self._update_url_path}
    security_groups:
      - {self._update_group_name}
'''
        self._run_enmasse(updated_yaml)

        # .. give the server time to pick up the config change after reload_config ..
        time.sleep(5)

        # .. old member A should now be rejected ..
        response = self._post_mcp(self._update_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))
        self.assertEqual(response.status_code, FORBIDDEN,
            f'Expected FORBIDDEN for removed member, got {response.status_code}: {response.text}')

        # .. new member B should now be allowed ..
        response = self._post_mcp(self._update_url_path, auth=(_NON_MEMBER_USERNAME, _NON_MEMBER_PASSWORD))
        self.assertEqual(response.status_code, OK,
            f'Expected OK for new member, got {response.status_code}: {response.text}')

# ################################################################################################################################

    def test_deactivated_channel_rejects_all(self) -> 'None':
        """ POST to a deactivated channel and a non-existent path both return the same status,
        ensuring no information leakage between inactive and non-existent channels.
        """

        # .. POST to the deactivated channel with valid credentials ..
        response_inactive = self._post_mcp(self._inactive_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))

        # .. POST to a completely non-existent path ..
        response_nonexistent = self._post_mcp(self._nonexistent_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))

        # .. both must return the same status code ..
        expected_status = response_nonexistent.status_code

        self.assertEqual(response_inactive.status_code, expected_status,
            f'Deactivated channel status ({response_inactive.status_code}) differs from '
            f'non-existent path status ({expected_status}) - information leakage')

# ################################################################################################################################

    def test_reactivate_channel(self) -> 'None':
        """ Deactivate a channel then reactivate it, verify it serves again with group member creds.
        """
        from http.client import NOT_FOUND

        # .. first confirm the inactive channel is indeed not reachable ..
        response = self._post_mcp(self._inactive_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))
        self.assertEqual(response.status_code, NOT_FOUND)

        # .. reactivate it via enmasse using the inactive channel's own dedicated group ..
        reactivate_yaml = f'''\
security:
  - name: {self._sec_def_name}
    type: basic_auth
    username: {_SEC_DEF_USERNAME}
    password: "{_SEC_DEF_PASSWORD}"

groups:
  - name: {self._inactive_group_name}
    members:
      - {self._sec_def_name}

channel_mcp:
  - name: {self._inactive_channel_name}
    is_active: true
    url_path: {self._inactive_url_path}
    security_groups:
      - {self._inactive_group_name}
'''
        self._run_enmasse(reactivate_yaml)
        time.sleep(5)

        # .. now the channel should serve requests with valid creds ..
        response = self._post_mcp(self._inactive_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))
        self.assertEqual(response.status_code, OK,
            f'Expected OK after reactivation, got {response.status_code}: {response.text}')

# ################################################################################################################################

    def test_channel_rename_preserves_group(self) -> 'None':
        """ Rename a channel via API edit, new URL enforces same group, old URL -> 404.
        """
        from http.client import NOT_FOUND
        from zato.common.api import GENERIC

        # .. confirm channel works at old URL ..
        response = self._post_mcp(self._rename_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))
        self.assertEqual(response.status_code, OK)

        # .. get the GenericConn details ..
        conn = self._get_generic_conn(self._rename_channel_name)

        # .. rename the channel (new name and new URL path), preserving security_groups ..
        new_name = self._rename_channel_name + '.renamed'

        self._invoke_service('zato.generic.connection.edit', {
            'id': conn['id'],
            'cluster_id': 1,
            'name': new_name,
            'type_': GENERIC.CONNECTION.TYPE.CHANNEL_MCP,
            'is_active': True,
            'is_internal': False,
            'is_channel': True,
            'is_outconn': False,
            'url_path': self._rename_new_url_path,
            'security_groups': conn['security_groups'],
        })

        # .. trigger a config reload so HTTP routing picks up the HTTPSOAP changes ..
        self._invoke_service('zato.server.invoker', {'func_name': 'reload_config'})
        time.sleep(5)

        # .. old URL should return 404 ..
        response = self._post_mcp(self._rename_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))
        self.assertEqual(response.status_code, NOT_FOUND,
            f'Expected NOT_FOUND at old URL after rename, got {response.status_code}: {response.text}')

        # .. new URL should work with the same group member creds ..
        response = self._post_mcp(self._rename_new_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))
        self.assertEqual(response.status_code, OK,
            f'Expected OK at new URL after rename, got {response.status_code}: {response.text}')

        # .. non-member should still be rejected at new URL ..
        response = self._post_mcp(self._rename_new_url_path, auth=(_NON_MEMBER_USERNAME, _NON_MEMBER_PASSWORD))
        self.assertEqual(response.status_code, FORBIDDEN,
            f'Expected FORBIDDEN for non-member at new URL, got {response.status_code}: {response.text}')

# ################################################################################################################################

    def test_delete_channel_cleans_up(self) -> 'None':
        """ Delete a channel via API, URL -> 404.
        """
        from http.client import NOT_FOUND

        # .. confirm channel works before deletion ..
        response = self._post_mcp(self._delete_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))
        self.assertEqual(response.status_code, OK)

        # .. get the GenericConn details ..
        conn = self._get_generic_conn(self._delete_channel_name)

        # .. delete it ..
        self._invoke_service('zato.generic.connection.delete', {
            'id': conn['id'],
        })

        # .. trigger a config reload so HTTP routing picks up the HTTPSOAP removal ..
        self._invoke_service('zato.server.invoker', {'func_name': 'reload_config'})
        time.sleep(5)

        # .. URL should now return 404 ..
        response = self._post_mcp(self._delete_url_path, auth=(_SEC_DEF_USERNAME, _SEC_DEF_PASSWORD))
        self.assertEqual(response.status_code, NOT_FOUND,
            f'Expected NOT_FOUND after deletion, got {response.status_code}: {response.text}')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
