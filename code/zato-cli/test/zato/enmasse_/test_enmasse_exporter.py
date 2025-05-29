# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
import yaml
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseExporter(TestCase):
    """ Tests exporting configuration from database to YAML format using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file for the import template
        self.import_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.import_file.write(template_complex_01.encode('utf-8'))
        self.import_file.close()

        # Create a temporary file for the export result
        self.export_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        self.export_file.close()

        # Initialize the importer and exporter
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

        # Clear session and configs
        self.session = cast_('any_', None)
        self.yaml_config = cast_('stranydict', None)
        self.parsed_template = cast_('stranydict', None)
        self.parsed_export = cast_('stranydict', None)

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.import_file.name)
        os.unlink(self.export_file.name)
        cleanup_enmasse()

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.import_file.name)

        if not self.parsed_template:
            with open(self.import_file.name, 'r') as f:
                raw_yaml = f.read()
                self.parsed_template = yaml.safe_load(raw_yaml)

    def _normalize_yaml(self, config:'stranydict') -> 'stranydict':
        """ Normalize YAML configuration for comparison by removing password fields from template.
        """
        normalized = {}

        # Process each section
        for section_name, section_items in config.items():
            normalized_items = []

            for item in section_items:
                # Create a copy of the item
                normalized_item = item.copy()

                # Remove password-related fields from template
                if 'password' in normalized_item:
                    del normalized_item['password']

                if 'secret_value' in normalized_item:
                    del normalized_item['secret_value']

                normalized_items.append(normalized_item)

            normalized[section_name] = normalized_items

        return normalized

    def test_import_and_export_cycle(self):
        """ Test the complete cycle of importing and then exporting configuration,
            verifying that the exported configuration matches the imported one.
        """
        self._setup_test_environment()

        # Import the YAML configuration into the database
        self.importer.sync_from_yaml(self.yaml_config, self.session)

        # Now export the configuration back to YAML
        exported_yaml = self.exporter.export_from_server(self.server_path, self.export_file.name)

        # Parse the exported YAML
        self.parsed_export = yaml.safe_load(exported_yaml)

        # Normalize both configurations for comparison
        normalized_template = self._normalize_yaml(self.parsed_template)
        normalized_export = self._normalize_yaml(self.parsed_export)

        # Check that the exported configuration matches the template
        for section_name, template_items in normalized_template.items():
            # Verify section exists in exported config
            self.assertIn(section_name, normalized_export,
                          f'Section {section_name!r} missing from exported config')

            # Get exported items for this section
            export_items = normalized_export[section_name]

            # Verify count matches
            self.assertEqual(
                len(template_items),
                len(export_items),
                f'Item count mismatch in section {section_name!r}: expected {len(template_items)}, got {len(export_items)}')

            # Create dictionaries of items by name for easier comparison
            template_items_by_name = {item['name']: item for item in template_items}
            export_items_by_name = {item['name']: item for item in export_items}

            # Verify all items exist and match
            for name, template_item in template_items_by_name.items():
                # Check item exists
                self.assertIn(name, export_items_by_name,
                              f'Item {name!r} missing from exported section {section_name!r}')

                # Get exported item
                export_item = export_items_by_name[name]

                # Check all fields in template item exist in export item with same values
                for key, value in template_item.items():
                    self.assertIn(key, export_item,
                                  f'Field {key!r} missing from exported item {name!r} in section {section_name!r}')
                    self.assertEqual(
                        value,
                        export_item[key],
                        f'Field {key!r} value mismatch in item {name!r} section {section_name!r}: expected {value}, got {export_item[key]}')

                # Check all fields in export item exist in template item
                for key in export_item.keys():
                    self.assertIn(key, template_item,
                                  f'Extra field {key!r} in exported item {name!r} in section {section_name!r}')

        # Check that the exported configuration has no extra sections
        for section_name in normalized_export.keys():
            self.assertIn(section_name, normalized_template,
                          f'Extra section {section_name!r} in exported config')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
