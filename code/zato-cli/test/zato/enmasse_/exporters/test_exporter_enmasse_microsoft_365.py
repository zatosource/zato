# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.microsoft_365 import Microsoft365Importer
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseMicrosoft365Export(TestCase):
    """ Tests exporting Microsoft 365 definitions to YAML format using enmasse.
    """

# ################################################################################################################################

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains Microsoft 365 definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer and exporter
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

        # Initialize Microsoft 365 importer
        self.microsoft_365_importer = Microsoft365Importer(self.importer)

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

    def test_microsoft_365_export(self):
        """ Test exporting Microsoft 365 definitions to YAML format.
        """
        self._setup_test_environment()

        # Get Microsoft 365 definitions from YAML
        microsoft_365_defs = self.yaml_config['microsoft_365']

        # Import the Microsoft 365 definition first
        created, _ = self.microsoft_365_importer.sync_definitions(microsoft_365_defs, self.session)
        self.assertEqual(len(created), 1)

        # Export Microsoft 365 definitions
        exported_microsoft_365 = self.exporter.export_microsoft_365(self.session)
        self.assertIsNotNone(exported_microsoft_365)
        self.assertEqual(len(exported_microsoft_365), 1)

        # Verify exported data
        exported_item = exported_microsoft_365[0]
        self.assertEqual(exported_item['name'], 'enmasse.cloud.microsoft365.1')
        self.assertEqual(exported_item['client_id'], '12345678-1234-1234-1234-123456789abc')
        self.assertEqual(exported_item['tenant_id'], '87654321-4321-4321-4321-cba987654321')
        self.assertTrue(exported_item.get('is_active'))

        # Verify that scopes are exported correctly
        self.assertEqual(exported_item.get('scopes'), 'Mail.Read Mail.Send')

# ################################################################################################################################

    def test_microsoft_365_full_export(self):
        """ Test that Microsoft 365 definitions are included in the full export.
        """
        self._setup_test_environment()

        # Get Microsoft 365 definitions from YAML
        microsoft_365_defs = self.yaml_config['microsoft_365']

        # Import the Microsoft 365 definition first
        _ = self.microsoft_365_importer.sync_definitions(microsoft_365_defs, self.session)

        # Export all definitions to dict
        exported_dict = self.exporter.export_to_dict(self.session)

        # Verify Microsoft 365 definitions are included
        self.assertIn('microsoft_365', exported_dict)
        self.assertEqual(len(exported_dict['microsoft_365']), 1)

        # Verify the data structure matches what was imported
        imported_def = microsoft_365_defs[0]
        exported_def = exported_dict['microsoft_365'][0]

        self.assertEqual(exported_def['name'], imported_def['name'])
        self.assertEqual(exported_def['client_id'], imported_def['client_id'])
        self.assertEqual(exported_def['tenant_id'], imported_def['tenant_id'])
        self.assertEqual(exported_def['scopes'], imported_def['scopes'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
