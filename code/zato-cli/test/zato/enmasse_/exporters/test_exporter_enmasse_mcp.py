# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.mcp import GatewayMCPImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

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
        self.server_path = default_server_base_dir

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
        cleanup_enmasse()

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
