# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import subprocess
import sys
import tempfile
from logging import basicConfig, getLogger, WARN
from unittest import main, TestCase

# The directory with the throwaway test environment helpers
_this_directory = os.path.dirname(__file__)
sys.path.insert(0, _this_directory)

# PyYAML
import yaml  # noqa: E402

# Zato
from env_helper import create_environment, delete_environment  # noqa: E402
from zato.common.test import rand_string, rand_unicode  # noqa: E402
from zato.common.util.open_ import open_w  # noqa: E402

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from env_helper import TestEnvironment
    TestEnvironment = TestEnvironment

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The zato binary of the checkout the tests run from
_zato_base = os.path.normpath(os.path.join(_this_directory, '..', '..', '..', '..'))
_zato_bin = os.path.join(_zato_base, 'bin', 'zato')

# How long a single enmasse invocation may take, in seconds
_enmasse_timeout = 120

# ################################################################################################################################
# ################################################################################################################################

# The YAML below deploys inbound-enabled bearer token definitions - one static, one JWT -
# a group containing both, an MCP gateway using the group and a REST channel
# with the JWT definition assigned directly.
template_bearer_inbound = """
security:
  - name: enmasse.bearer.static.{test_suffix}
    type: bearer_token
    static_token: enmasse-static-token-{test_suffix}

  - name: enmasse.bearer.jwt.{test_suffix}
    type: bearer_token
    username: enmasse-client-id
    password: enmasse-client-secret
    auth_endpoint: http://localhost:8480/realms/zato-test/protocol/openid-connect/token
    issuer: http://localhost:8480/realms/zato-test
    jwks_url: http://localhost:8480/realms/zato-test/protocol/openid-connect/certs
    audience: zato-test-audience
    claims:
      - department=Accounting

groups:
  - name: enmasse.bearer.group.{test_suffix}
    members:
      - enmasse.bearer.static.{test_suffix}
      - enmasse.bearer.jwt.{test_suffix}

mcp_gateway:
  - name: enmasse.bearer.mcp.{test_suffix}
    is_active: true
    url_path: /enmasse/bearer/mcp/{test_suffix}
    security_groups:
      - enmasse.bearer.group.{test_suffix}

channel_rest:
  - name: enmasse.bearer.channel.{test_suffix}
    service: demo.ping
    url_path: /enmasse/bearer/rest/{test_suffix}
    security: enmasse.bearer.jwt.{test_suffix}
"""

# ################################################################################################################################
# ################################################################################################################################

class EnmasseBearerInboundTestCase(TestCase):
    """ Runs against a throwaway quickstart environment with its own embedded ODB,
    created in setUpClass and deleted in tearDownClass - no pre-existing environment is ever used.
    """

    environment: 'TestEnvironment'

    @classmethod
    def setUpClass(class_) -> 'None':
        class_.environment = create_environment('zato-enmasse-bearer-')

# ################################################################################################################################

    @classmethod
    def tearDownClass(class_) -> 'None':
        delete_environment(class_.environment)

# ################################################################################################################################

    def invoke_enmasse(self, config_path:'str', is_import:'bool'=True, include_type:'str'='') -> 'None':
        """ Runs the enmasse CLI against the throwaway environment's server directory.
        """
        args = [_zato_bin, 'enmasse', self.environment.server_dir, '--verbose', '--missing-wait-time', '1']

        if is_import:
            args.extend(['--import', '--input', config_path])
        else:
            args.extend(['--export', '--output', config_path])
            if include_type:
                args.extend(['--include-type', include_type])

        # No server is running in the throwaway environment, so no config reload is possible
        enmasse_env = os.environ.copy()
        enmasse_env['Zato_Needs_Config_Reload'] = 'False'

        result = subprocess.run(args, capture_output=True, text=True, timeout=_enmasse_timeout, env=enmasse_env)

        if result.returncode != 0:
            self.fail(f'enmasse failed (exit {result.returncode}):\nstdout: {result.stdout}\nstderr: {result.stderr}')

        if 'error' in result.stdout:
            self.fail(f'Found an error in enmasse stdout:\n{result.stdout}')

        if 'error' in result.stderr:
            self.fail(f'Found an error in enmasse stderr:\n{result.stderr}')

# ################################################################################################################################

    def test_bearer_inbound_round_trip(self) -> 'None':
        """ Inbound bearer token definitions survive an import, an export and a re-import.
        """
        tmp_dir = tempfile.gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        import_path = os.path.join(tmp_dir, f'zato-enmasse-bearer-import-{test_suffix}.yaml')
        export_path = os.path.join(tmp_dir, f'zato-enmasse-bearer-export-{test_suffix}.yaml')

        data = template_bearer_inbound.format(test_suffix=test_suffix)

        with open_w(import_path) as import_file:
            _ = import_file.write(data)

        static_name = f'enmasse.bearer.static.{test_suffix}'
        jwt_name = f'enmasse.bearer.jwt.{test_suffix}'
        group_name = f'enmasse.bearer.group.{test_suffix}'
        mcp_name = f'enmasse.bearer.mcp.{test_suffix}'
        channel_name = f'enmasse.bearer.channel.{test_suffix}'

        try:
            # Import the definitions ..
            self.invoke_enmasse(import_path)

            # .. a second import of the same file must be a no-op, not an error ..
            self.invoke_enmasse(import_path)

            # .. now export everything the test created ..
            include_types = 'security,groups,mcp_gateway,channel_rest'
            self.invoke_enmasse(export_path, is_import=False, include_type=include_types)

            with open(export_path, 'r') as export_file:
                export_data = export_file.read()

            exported = yaml.safe_load(export_data)

            # .. index the exported security definitions by name ..
            security_by_name = {}

            for item in exported['security']:
                security_by_name[item['name']] = item

            # .. the static definition keeps its token ..
            static_def = security_by_name[static_name]
            self.assertEqual(static_def['type'], 'bearer_token')
            self.assertEqual(static_def['static_token'], f'enmasse-static-token-{test_suffix}')

            # .. the JWT definition keeps all its inbound fields ..
            jwt_def = security_by_name[jwt_name]
            self.assertEqual(jwt_def['type'], 'bearer_token')
            self.assertEqual(jwt_def['auth_endpoint'], 'http://localhost:8480/realms/zato-test/protocol/openid-connect/token')
            self.assertEqual(jwt_def['issuer'], 'http://localhost:8480/realms/zato-test')
            self.assertEqual(jwt_def['jwks_url'], 'http://localhost:8480/realms/zato-test/protocol/openid-connect/certs')
            self.assertEqual(jwt_def['audience'], 'zato-test-audience')
            self.assertEqual(jwt_def['claims'], ['department=Accounting'])

            # .. the group keeps both definitions as members ..
            groups_by_name = {}

            for item in exported['groups']:
                groups_by_name[item['name']] = item

            group = groups_by_name[group_name]
            self.assertIn(static_name, group['members'])
            self.assertIn(jwt_name, group['members'])

            # .. the MCP gateway keeps its group ..
            mcp_by_name = {}

            for item in exported['mcp_gateway']:
                mcp_by_name[item['name']] = item

            mcp_gateway = mcp_by_name[mcp_name]
            self.assertIn(group_name, mcp_gateway['security_groups'])

            # .. and the REST channel keeps its directly assigned definition ..
            channels_by_name = {}

            for item in exported['channel_rest']:
                channels_by_name[item['name']] = item

            channel = channels_by_name[channel_name]
            self.assertEqual(channel['security'], jwt_name)

            # .. finally, re-importing the export must succeed, proving the round trip is stable.
            self.invoke_enmasse(export_path)

        finally:
            if os.path.exists(import_path):
                os.remove(import_path)
            if os.path.exists(export_path):
                os.remove(export_path)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
