# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import basicConfig, getLogger, WARN
from tempfile import gettempdir
from unittest import main

# PyYAML
import yaml

# Zato
from zato.common.test import rand_string, rand_unicode
from zato.common.test.enmasse_.base import BaseEnmasseTestCase
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_Gateway_MCP_Template = """

security:

  - name: enmasse.mcp.basic.{test_suffix}
    type: basic_auth
    username: enmasse.mcp.user.{test_suffix}
    password: enmasse.mcp.password.{test_suffix}

groups:

  - name: enmasse.mcp.group.{test_suffix}
    members:
      - enmasse.mcp.basic.{test_suffix}

mcp_gateway:

  - name: enmasse.mcp.full.{test_suffix}
    is_audit_log_active: true
    url_path: /mcp/enmasse-full-{test_suffix}
    services:
      - demo.ping
    security_groups:
      - enmasse.mcp.group.{test_suffix}
    skills:
      - crm-house-style
    validate_input: true
    allow_client_filters: true
    max_response_size: 2000
    size_cap_mode: block
    min_size_threshold: 100
    characters_per_token: 3.5
    safeguards_strip_nulls: true
    safeguards_collapse_whitespace: true
    safeguards_strip_base64: true
    safeguards_pii_enabled: true
    safeguards_pii_lands:
      - intl
    safeguards_pii_detectors:
      - intl_ipv4
    safeguards_pii_exclude:
      - intl_email
    safeguards_pii_validate: false
    safeguards_pii_stable_replacements: true
    safeguards_normalize_unicode: true
    safeguards_unicode_mode: reject
    safeguards_sanitize_markup: true
    safeguards_markup_mode: reject
    safeguards_url_policy_enabled: true
    safeguards_url_allow_list:
      - example.com
    safeguards_url_mode: neutralize

  - name: enmasse.mcp.minimal.{test_suffix}
    url_path: /mcp/enmasse-minimal-{test_suffix}
    services: demo.ping

"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseGatewayMCPLive(BaseEnmasseTestCase):
    """ Live CLI tests for MCP gateway import, export, and reimport against a real server.
    """

    def _cleanup(self, test_suffix:'str') -> 'None':
        from zato.cli.enmasse.client import cleanup_enmasse
        from zato.common.defaults import default_server_base_dir
        cleanup_enmasse(default_server_base_dir)

# ################################################################################################################################

    def _read_test_gateways(self, export_path:'str', test_suffix:'str') -> 'dict':
        """ Reads one exported file and returns this run's gateways keyed by name.
        """

        with open(export_path, 'r') as f:
            export_data = f.read()

        exported_dict = yaml.safe_load(export_data)

        self.assertIn('mcp_gateway', exported_dict, 'mcp_gateway key missing from export')

        out = {}

        for gateway in exported_dict['mcp_gateway']:
            if test_suffix in gateway['name']:
                out[gateway['name']] = gateway

        return out

# ################################################################################################################################

    def test_mcp_gateway_import_export_reimport(self) -> 'None':
        """ Full cycle: import MCP gateways, export them, verify the export, then reimport to confirm idempotency.
        """

        # sh
        from sh import ErrorReturnCode

        os.environ['Zato_Needs_Config_Reload'] = 'False'

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        import_file_name = 'zato-enmasse-mcp-import-' + test_suffix + '.yaml'
        export_file_name = 'zato-enmasse-mcp-export-' + test_suffix + '.yaml'

        import_path = os.path.join(tmp_dir, import_file_name)
        export_path = os.path.join(tmp_dir, export_file_name)

        # Prepare the import file from the template ..
        data = _Gateway_MCP_Template.format(test_suffix=test_suffix)

        with open_w(import_path) as f:
            _ = f.write(data)

        try:

            # .. import the MCP gateways ..
            _ = self.invoke_enmasse(import_path)

            # .. export them back out ..
            _ = self.invoke_enmasse(
                export_path, is_import=False, is_export=True, include_type='mcp_gateway,security,groups')

            # .. read the exported file and filter to this run's gateways ..
            gateways_by_name = self._read_test_gateways(export_path, test_suffix)

            gateway_count = len(gateways_by_name)
            self.assertEqual(gateway_count, 2, f'Expected 2 MCP gateways, found {gateway_count}')

            full_name = f'enmasse.mcp.full.{test_suffix}'
            minimal_name = f'enmasse.mcp.minimal.{test_suffix}'

            full = gateways_by_name[full_name]
            minimal = gateways_by_name[minimal_name]

            # .. every non-default field of the full gateway survived the round trip ..
            self.assertEqual(full['url_path'], f'/mcp/enmasse-full-{test_suffix}')
            self.assertEqual(full['services'], ['demo.ping'])
            self.assertTrue(full['is_audit_log_active'])
            self.assertEqual(full['skills'], ['crm-house-style'])
            self.assertTrue(full['validate_input'])
            self.assertTrue(full['allow_client_filters'])

            self.assertEqual(full['max_response_size'], 2000)
            self.assertEqual(full['size_cap_mode'], 'block')
            self.assertEqual(full['min_size_threshold'], 100)
            self.assertEqual(full['characters_per_token'], 3.5)

            self.assertTrue(full['safeguards_strip_nulls'])
            self.assertTrue(full['safeguards_collapse_whitespace'])
            self.assertTrue(full['safeguards_strip_base64'])

            self.assertTrue(full['safeguards_pii_enabled'])
            self.assertEqual(full['safeguards_pii_lands'], ['intl'])
            self.assertEqual(full['safeguards_pii_detectors'], ['intl_ipv4'])
            self.assertEqual(full['safeguards_pii_exclude'], ['intl_email'])
            self.assertTrue(full['safeguards_pii_stable_replacements'])

            # .. the explicit False against a True default survived, so a reimport cannot flip it back ..
            self.assertFalse(full['safeguards_pii_validate'])

            self.assertTrue(full['safeguards_normalize_unicode'])
            self.assertEqual(full['safeguards_unicode_mode'], 'reject')
            self.assertTrue(full['safeguards_sanitize_markup'])
            self.assertEqual(full['safeguards_markup_mode'], 'reject')
            self.assertTrue(full['safeguards_url_policy_enabled'])
            self.assertEqual(full['safeguards_url_allow_list'], ['example.com'])
            self.assertEqual(full['safeguards_url_mode'], 'neutralize')

            # .. the security group travels by name in both directions,
            # the id it resolved to never appearing in the export ..
            self.assertEqual(full['security_groups'], [f'enmasse.mcp.group.{test_suffix}'])

            # .. the minimal gateway keeps its defaults out of the export ..
            self.assertEqual(minimal['url_path'], f'/mcp/enmasse-minimal-{test_suffix}')
            self.assertEqual(minimal['services'], ['demo.ping'])

            self.assertNotIn('is_audit_log_active', minimal)
            self.assertNotIn('security_groups', minimal)
            self.assertNotIn('skills', minimal)
            self.assertNotIn('validate_input', minimal)
            self.assertNotIn('allow_client_filters', minimal)
            self.assertNotIn('max_response_size', minimal)
            self.assertNotIn('safeguards_pii_enabled', minimal)
            self.assertNotIn('safeguards_url_policy_enabled', minimal)

            # .. now reimport the exported file to confirm it is a clean input ..
            _ = self.invoke_enmasse(export_path)

            # .. and export again to make sure nothing drifted.
            reimport_export_file_name = 'zato-enmasse-mcp-reimport-export-' + test_suffix + '.yaml'
            reimport_export_path = os.path.join(tmp_dir, reimport_export_file_name)

            _ = self.invoke_enmasse(
                reimport_export_path, is_import=False, is_export=True, include_type='mcp_gateway,security,groups')

            reimport_gateways_by_name = self._read_test_gateways(reimport_export_path, test_suffix)

            self.assertEqual(reimport_gateways_by_name, gateways_by_name, 'The second export drifted from the first')

            if os.path.exists(reimport_export_path):
                os.remove(reimport_export_path)

        except ErrorReturnCode as error:
            stdout = error.stdout.decode('utf8')
            stderr = error.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception during MCP gateway import-export-reimport; stdout -> {stdout}')

        finally:
            if os.path.exists(import_path):
                os.remove(import_path)
            if os.path.exists(export_path):
                os.remove(export_path)

            self._cleanup(test_suffix)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
