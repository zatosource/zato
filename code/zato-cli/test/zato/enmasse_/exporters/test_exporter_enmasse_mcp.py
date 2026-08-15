# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from unittest import TestCase

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.mcp import GatewayMCPImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseGatewayMCPExport(TestCase):
    """ Tests exporting MCP gateway definitions to YAML format.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()
        self.security_importer = SecurityImporter(self.importer)
        self.mcp_importer = GatewayMCPImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self):
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)
        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # Process security definitions and groups first - MCP gateways reference security groups
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)
        _ = self.importer.sync_groups(self.yaml_config['groups'], self.session)

# ################################################################################################################################

    def test_mcp_gateway_export(self):
        self._setup_test_environment()

        mcp_list_from_yaml = self.yaml_config['mcp_gateway']

        created, _ = self.mcp_importer.sync_definitions(mcp_list_from_yaml, self.session)
        self.assertEqual(len(created), 2)

        exported_data = self.exporter.export_to_dict(self.session)

        self.assertIn('mcp_gateway', exported_data)
        exported_mcp_list = exported_data['mcp_gateway']

        # Filter to only the test-created gateways (DB may have pre-existing ones)
        exported_mcp_list = [item for item in exported_mcp_list if item['name'].startswith('enmasse.mcp.')]
        self.assertEqual(len(exported_mcp_list), 2)

        exported_by_name = {item['name']: item for item in exported_mcp_list}

        for yaml_def in mcp_list_from_yaml:
            name = yaml_def['name']
            self.assertIn(name, exported_by_name)
            exported_def = exported_by_name[name]
            self.assertEqual(exported_def['name'], yaml_def['name'])

        # The audit log toggle is on against its off default, so it survives the trip.
        exported_1 = exported_by_name['enmasse.mcp.gateway.1']
        exported_2 = exported_by_name['enmasse.mcp.gateway.2']

        self.assertTrue(exported_1['is_audit_log_active'])

        # The services list is exported as the list it was imported as,
        # whether it arrived as a YAML list or as a comma-separated string.
        self.assertEqual(exported_1['services'], ['crm.get-customer', 'crm.update-customer'])
        self.assertEqual(exported_2['services'], ['billing.get-invoice'])

        # Security group ids export as the names they resolve from,
        # so one environment's export is another's importable input.
        self.assertEqual(exported_1['security_groups'], ['enmasse.group.1'])

        # Every non-default runtime field of the fully configured gateway round-trips ..
        self.assertEqual(exported_1['skills'], ['crm-house-style'])
        self.assertTrue(exported_1['validate_input'])
        self.assertTrue(exported_1['allow_client_filters'])

        self.assertEqual(exported_1['max_response_size'], 2000)
        self.assertEqual(exported_1['size_cap_mode'], 'block')
        self.assertEqual(exported_1['min_size_threshold'], 100)
        self.assertEqual(exported_1['characters_per_token'], 3.5)

        self.assertTrue(exported_1['safeguards_strip_nulls'])
        self.assertTrue(exported_1['safeguards_collapse_whitespace'])
        self.assertTrue(exported_1['safeguards_strip_base64'])

        self.assertTrue(exported_1['safeguards_pii_enabled'])
        self.assertEqual(exported_1['safeguards_pii_lands'], ['intl'])
        self.assertEqual(exported_1['safeguards_pii_detectors'], ['intl_ipv4'])
        self.assertEqual(exported_1['safeguards_pii_exclude'], ['intl_email'])
        self.assertTrue(exported_1['safeguards_pii_stable_replacements'])

        # An explicit False against a True default survives the export,
        # so a re-import cannot flip it back on.
        self.assertFalse(exported_1['safeguards_pii_validate'])

        self.assertTrue(exported_1['safeguards_normalize_unicode'])
        self.assertEqual(exported_1['safeguards_unicode_mode'], 'reject')
        self.assertTrue(exported_1['safeguards_sanitize_markup'])
        self.assertEqual(exported_1['safeguards_markup_mode'], 'reject')
        self.assertTrue(exported_1['safeguards_url_policy_enabled'])
        self.assertEqual(exported_1['safeguards_url_allow_list'], ['example.com'])
        self.assertEqual(exported_1['safeguards_url_mode'], 'neutralize')

        # .. and a gateway that stated nothing keeps its defaults out of the export -
        # a re-import applies the same defaults, so nothing can silently flip.
        self.assertNotIn('is_audit_log_active', exported_2)
        self.assertNotIn('security_groups', exported_2)
        self.assertNotIn('skills', exported_2)
        self.assertNotIn('session_ttl', exported_2)
        self.assertNotIn('validate_input', exported_2)
        self.assertNotIn('allow_client_filters', exported_2)
        self.assertNotIn('max_response_size', exported_2)
        self.assertNotIn('size_cap_mode', exported_2)
        self.assertNotIn('characters_per_token', exported_2)
        self.assertNotIn('safeguards_strip_nulls', exported_2)
        self.assertNotIn('safeguards_pii_enabled', exported_2)
        self.assertNotIn('safeguards_pii_detectors', exported_2)
        self.assertNotIn('safeguards_pii_validate', exported_2)
        self.assertNotIn('safeguards_normalize_unicode', exported_2)
        self.assertNotIn('safeguards_url_policy_enabled', exported_2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging
    from unittest import main

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
