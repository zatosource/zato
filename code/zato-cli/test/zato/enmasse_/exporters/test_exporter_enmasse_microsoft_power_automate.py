# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.microsoft_power_automate import MicrosoftPowerAutomateImporter
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

class TestEnmasseMicrosoftPowerAutomateExport(TestCase):
    """ Tests exporting Microsoft Power Automate definitions to YAML format using enmasse.
    """

# ################################################################################################################################

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = default_server_base_dir

        # Create a temporary file using the existing template which already contains Microsoft Power Automate definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer and exporter
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

        # Initialize Microsoft Power Automate importer
        self.microsoft_power_automate_importer = MicrosoftPowerAutomateImporter(self.importer)

        # Parse the YAML file
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
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_microsoft_power_automate_export(self):
        """ Test exporting Microsoft Power Automate definitions to YAML format.
        """
        self._setup_test_environment()

        # Get Microsoft Power Automate definitions from YAML
        microsoft_power_automate_defs = self.yaml_config['microsoft_power_automate']

        # Import the Microsoft Power Automate definition first
        created, _ = self.microsoft_power_automate_importer.sync_definitions(microsoft_power_automate_defs, self.session)
        self.assertEqual(len(created), 1)

        # Export Microsoft Power Automate definitions
        exported_connections = self.exporter.export_microsoft_power_automate(self.session)
        self.assertIsNotNone(exported_connections)
        self.assertEqual(len(exported_connections), 1)

        # Verify exported data
        exported_item = exported_connections[0]
        self.assertEqual(exported_item['name'], 'enmasse.cloud.microsoft-power-automate.1')
        self.assertEqual(exported_item['client_id'], '23456789-2345-2345-2345-23456789abcd')
        self.assertEqual(exported_item['tenant_id'], '98765432-5432-5432-5432-dcba98765432')
        self.assertEqual(exported_item['environment_id'], 'Default-98765432-5432-5432-5432-dcba98765432')
        self.assertEqual(exported_item['address'], 'https://api.flow.microsoft.com')
        self.assertTrue(exported_item.get('is_active'))

# ################################################################################################################################

    def test_microsoft_power_automate_full_export(self):
        """ Test that Microsoft Power Automate definitions are included in the full export.
        """
        self._setup_test_environment()

        # Get Microsoft Power Automate definitions from YAML
        microsoft_power_automate_defs = self.yaml_config['microsoft_power_automate']

        # Import the Microsoft Power Automate definition first
        _ = self.microsoft_power_automate_importer.sync_definitions(microsoft_power_automate_defs, self.session)

        # Export all definitions to dict
        exported_dict = self.exporter.export_to_dict(self.session)

        # Verify Microsoft Power Automate definitions are included
        self.assertIn('microsoft_power_automate', exported_dict)
        self.assertEqual(len(exported_dict['microsoft_power_automate']), 1)

        # Verify the data structure matches what was imported
        imported_def = microsoft_power_automate_defs[0]
        exported_def = exported_dict['microsoft_power_automate'][0]

        self.assertEqual(exported_def['name'], imported_def['name'])
        self.assertEqual(exported_def['client_id'], imported_def['client_id'])
        self.assertEqual(exported_def['tenant_id'], imported_def['tenant_id'])
        self.assertEqual(exported_def['environment_id'], imported_def['environment_id'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
