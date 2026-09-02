# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
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
from zato.cli.enmasse.importers.salesforce import SalesforceImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSalesforceExporter(TestCase):
    """ Tests exporting Salesforce connection definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.salesforce_importer = SalesforceImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self):

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_salesforce_export(self):
        self._setup_test_environment()

        # 1. Get Salesforce connection definitions from the YAML template
        salesforce_list_from_yaml = self.yaml_config['salesforce']

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_salesforce_connections, _ = self.salesforce_importer.sync_definitions(salesforce_list_from_yaml, self.session)

        created_count = len(created_salesforce_connections)
        self.assertGreater(created_count, 0, 'No Salesforce connections were created.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('salesforce', exported_data, 'Exporter did not produce a "salesforce" section.')
        exported_salesforce_list = exported_data['salesforce']

        # 4. Compare exported data with the original YAML data
        exported_count = len(exported_salesforce_list)
        yaml_count = len(salesforce_list_from_yaml)

        self.assertEqual(exported_count, yaml_count,
            'Number of exported Salesforce connections does not match original YAML.')

        # Create dictionaries keyed by name for easier comparison
        yaml_salesforce_by_name = {}
        for item in salesforce_list_from_yaml:
            yaml_salesforce_by_name[item['name']] = item

        exported_salesforce_by_name = {}
        for item in exported_salesforce_list:
            exported_salesforce_by_name[item['name']] = item

        for name, yaml_def in yaml_salesforce_by_name.items():

            self.assertIn(name, exported_salesforce_by_name, f'Salesforce connection "{name}" from YAML not found in export.')
            exported_def = exported_salesforce_by_name[name]

            # Compare fields that are expected to be exported by SalesforceExporter
            for field in ['name', 'address', 'username', 'api_version']:
                if field in yaml_def:
                    if yaml_def[field] is not None:
                        self.assertEqual(exported_def[field], yaml_def[field],
                            f'Mismatch for "{field}" in Salesforce connection "{name}"')

        # Secrets never leave the server, no matter the shape they were imported in
        for item in exported_salesforce_list:
            self.assertNotIn('password', item)
            self.assertNotIn('consumer_key', item)
            self.assertNotIn('consumer_secret', item)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
