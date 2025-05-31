# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

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
from zato.cli.enmasse.importers.confluence import ConfluenceImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseConfluenceExport(TestCase):
    """ Tests exporting Confluence definitions to YAML format using enmasse.
    """

# ################################################################################################################################

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains Confluence definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer and exporter
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

        # Initialize Confluence importer
        self.confluence_importer = ConfluenceImporter(self.importer)

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

    def _find_item_by_name(self, items, name):
        """ Helper method to find an item by name in a list of items.
        """
        for item in items:
            if item['name'] == name:
                return item
        return None

    def _verify_fields(self, exported_item, original_item, field_list):
        """ Helper method to verify fields match between exported and original items.
        """
        for field in field_list:
            if field in original_item:
                self.assertEqual(exported_item.get(field), original_item.get(field))

# ################################################################################################################################

    def test_confluence_export(self):
        """ Test exporting Confluence definitions to YAML format.
        """
        self._setup_test_environment()

        # Extract Confluence definitions from the YAML file
        confluence_list_from_yaml = self.yaml_config.get('confluence', [])

        # Skip the test if no Confluence definitions were found
        if not confluence_list_from_yaml:
            self.skipTest('No Confluence definitions found in YAML template')

        # Import Confluence definitions into the database
        created, _ = self.confluence_importer.sync_definitions(confluence_list_from_yaml, self.session)
        self.assertEqual(len(created), len(confluence_list_from_yaml))

        # Export Confluence definitions from the database
        exported_confluence_list = self.exporter.export_confluence(self.session)
        self.assertIsNotNone(exported_confluence_list)
        self.assertEqual(len(exported_confluence_list), len(confluence_list_from_yaml))

        # Get the first exported item (assuming there's at least one)
        exported_item = exported_confluence_list[0]
        exported_name = exported_item['name']

        # Get the corresponding original item from YAML
        yaml_item = self._find_item_by_name(confluence_list_from_yaml, exported_name)
        self.assertIsNotNone(yaml_item, f'Couldn\'t find matching Confluence definition for "{exported_name}"')

        # Verify basic fields are exported correctly
        self.assertEqual(exported_item['name'], yaml_item['name']) # type: ignore
        self.assertEqual(exported_item.get('is_active'), yaml_item.get('is_active', True)) # type: ignore

        # Verify connection-specific fields if they exist
        field_list = ['address', 'username', 'site_url']
        self._verify_fields(exported_item, yaml_item, field_list)

# ################################################################################################################################

    def test_confluence_full_export(self):
        """ Test that Confluence definitions are included in the full export.
        """
        self._setup_test_environment()

        # Get Confluence definitions from YAML
        confluence_defs = self.yaml_config.get('confluence', [])

        # Skip the test if no Confluence definitions were found
        if not confluence_defs:
            self.skipTest('No Confluence definitions found in YAML template')

        # Import the Confluence definition first
        _ = self.confluence_importer.sync_definitions(confluence_defs, self.session)

        # Export all definitions to dict
        exported_dict = self.exporter.export_to_dict(self.session)

        # Verify Confluence definitions are included in the export
        self.assertIn('confluence', exported_dict)
        self.assertTrue(len(exported_dict['confluence']) > 0)

        # Get the first Confluence definition from both imported and exported data
        imported_def = confluence_defs[0]
        imported_name = imported_def['name']

        # Find the corresponding exported definition
        exported_def = self._find_item_by_name(exported_dict['confluence'], imported_name)
        self.assertIsNotNone(exported_def, f'Couldn\'t find exported Confluence definition for "{imported_name}"')

        # Verify key fields match
        self.assertEqual(exported_def['name'], imported_def['name']) # type: ignore
        self.assertEqual(exported_def.get('is_active'), imported_def.get('is_active', True)) # type: ignore

        # Verify other fields if they exist
        field_list = ['address', 'username', 'site_url']
        self._verify_fields(exported_def, imported_def, field_list)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
