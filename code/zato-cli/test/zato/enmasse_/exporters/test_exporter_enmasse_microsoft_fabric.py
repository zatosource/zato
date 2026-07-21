# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile
from unittest import TestCase, main

# The directory with the throwaway test environment helpers
_enmasse_tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, _enmasse_tests_dir)

# Zato
from env_helper import get_shared_environment
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.microsoft_fabric import MicrosoftFabricImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseMicrosoftFabricExport(TestCase):
    """ Tests exporting Microsoft Fabric definitions to YAML format using enmasse.
    """

# ################################################################################################################################

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains Microsoft Fabric definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer and exporter
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

        # Initialize Microsoft Fabric importer
        self.microsoft_fabric_importer = MicrosoftFabricImporter(self.importer)

        # Parse the YAML file
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
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_microsoft_fabric_export(self):
        """ Test exporting Microsoft Fabric definitions to YAML format.
        """
        self._setup_test_environment()

        # Get Microsoft Fabric definitions from YAML
        microsoft_fabric_defs = self.yaml_config['microsoft_fabric']

        # Import the Microsoft Fabric definition first
        created, _ = self.microsoft_fabric_importer.sync_definitions(microsoft_fabric_defs, self.session)
        self.assertEqual(len(created), 1)

        # Export Microsoft Fabric definitions
        exported_connections = self.exporter.export_microsoft_fabric(self.session)
        self.assertIsNotNone(exported_connections)
        self.assertEqual(len(exported_connections), 1)

        # Verify exported data
        exported_item = exported_connections[0]
        self.assertEqual(exported_item['name'], 'enmasse.cloud.microsoft-fabric.1')
        self.assertEqual(exported_item['client_id'], '34567890-3456-3456-3456-34567890abcd')
        self.assertEqual(exported_item['tenant_id'], '87654321-6543-6543-6543-edcba9876543')
        self.assertEqual(exported_item['address'], 'https://api.fabric.microsoft.com/v1')
        self.assertTrue(exported_item.get('is_active'))

# ################################################################################################################################

    def test_microsoft_fabric_full_export(self):
        """ Test that Microsoft Fabric definitions are included in the full export.
        """
        self._setup_test_environment()

        # Get Microsoft Fabric definitions from YAML
        microsoft_fabric_defs = self.yaml_config['microsoft_fabric']

        # Import the Microsoft Fabric definition first
        _ = self.microsoft_fabric_importer.sync_definitions(microsoft_fabric_defs, self.session)

        # Export all definitions to dict
        exported_dict = self.exporter.export_to_dict(self.session)

        # Verify Microsoft Fabric definitions are included
        self.assertIn('microsoft_fabric', exported_dict)
        self.assertEqual(len(exported_dict['microsoft_fabric']), 1)

        # Verify the data structure matches what was imported
        imported_def = microsoft_fabric_defs[0]
        exported_def = exported_dict['microsoft_fabric'][0]

        self.assertEqual(exported_def['name'], imported_def['name'])
        self.assertEqual(exported_def['client_id'], imported_def['client_id'])
        self.assertEqual(exported_def['tenant_id'], imported_def['tenant_id'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
