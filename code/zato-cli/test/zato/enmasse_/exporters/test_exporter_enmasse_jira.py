# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.jira import JiraImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseJiraExporter(TestCase):
    """ Tests exporting JIRA connection definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.jira_importer = JiraImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self):

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_jira_export(self):
        self._setup_test_environment()

        # 1. Get JIRA connection definitions from the YAML template
        jira_list_from_yaml = self.yaml_config.get('jira', [])

        # If there are no JIRA connections in the template, add test data
        if not jira_list_from_yaml:
            jira_list_from_yaml = [
                {
                    'name': 'Test JIRA Connection',
                    'is_active': True,
                    'address': 'https://jira.example.com',
                    'username': 'test_user',
                    'is_cloud': True,
                    'api_version': 'v2',
                    'timeout': 30
                }
            ]
            self.yaml_config['jira'] = jira_list_from_yaml

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_jira_connections, _ = self.jira_importer.sync_definitions(jira_list_from_yaml, self.session)

        self.assertTrue(len(created_jira_connections) > 0, 'No JIRA connections were created.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('jira', exported_data, 'Exporter did not produce a "jira" section.')
        exported_jira_list = exported_data['jira']

        # 4. Compare exported data with the original YAML data
        self.assertEqual(len(exported_jira_list), len(jira_list_from_yaml), 
                         'Number of exported JIRA connections does not match original YAML.')

        # Create dictionaries keyed by name for easier comparison
        yaml_jira_by_name = {item['name']: item for item in jira_list_from_yaml}
        exported_jira_by_name = {item['name']: item for item in exported_jira_list}

        for name, yaml_def in yaml_jira_by_name.items():

            self.assertIn(name, exported_jira_by_name, f'JIRA connection "{name}" from YAML not found in export.')
            exported_def = exported_jira_by_name[name]

            # Compare fields that are expected to be exported by JiraExporter
            # Note: password and api_token are not exported for security reasons
            for field in ['name', 'is_active', 'address', 'username', 'is_cloud', 'api_version', 'timeout']:
                if field in yaml_def and yaml_def[field] is not None:
                    self.assertEqual(exported_def.get(field), yaml_def.get(field), 
                                     f'Mismatch for "{field}" in JIRA connection "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
