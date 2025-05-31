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
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSecurityExporter(TestCase):
    """ Tests exporting security definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.security_importer = SecurityImporter(self.importer)

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

# ################################################################################################################################

    def test_security_export(self):
        self._setup_test_environment()

        # 1. Get security definitions from the YAML template
        security_list_from_yaml = self.yaml_config.get('security', [])

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_security, _ = self.security_importer.sync_security_definitions(security_list_from_yaml, self.session)
        self.session.commit()

        self.assertTrue(len(created_security) > 0, 'No security definitions were created from YAML.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('security', exported_data, 'Exporter did not produce a "security" section.')
        exported_security_list = exported_data['security']

        # 4. Compare exported data with the original YAML data
        self.assertEqual(len(exported_security_list), len(security_list_from_yaml),  'Number of exported security definitions does not match original YAML.')

        # Create dictionaries keyed by name for easier comparison
        yaml_security_by_name = {item['name']: item for item in security_list_from_yaml}
        exported_security_by_name = {item['name']: item for item in exported_security_list}

        for name, yaml_def in yaml_security_by_name.items():
            self.assertIn(name, exported_security_by_name,  f'Security definition "{name}" from YAML not found in export.')
            exported_def = exported_security_by_name[name]

            # Check that the type is preserved
            self.assertEqual(exported_def.get('type'), yaml_def.get('type'),  f'Security type mismatch for "{name}"')

            # Check common fields that should be exported - excludes passwords
            self.assertEqual(exported_def.get('name'), yaml_def.get('name'),  f'Security name mismatch for "{name}"')

            # Check username for all security types
            if 'username' in yaml_def:
                self.assertEqual(exported_def.get('username'), yaml_def.get('username'),  f'Username mismatch for security definition "{name}"')

            # Check type-specific fields
            if yaml_def.get('type') == 'bearer_token':
                for field in ['auth_endpoint', 'client_id_field', 'client_secret_field', 'grant_type', 'data_format']:
                    if field in yaml_def:
                        self.assertEqual(exported_def.get(field), yaml_def.get(field), f'Field {field} mismatch for security definition "{name}"')

                # Check extra_fields if present
                if 'extra_fields' in yaml_def:
                    self.assertEqual(exported_def.get('extra_fields'), yaml_def.get('extra_fields'), f'Extra fields mismatch for security definition "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
