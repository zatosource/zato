# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

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
from zato.cli.enmasse.importers.odata import ODataImporter
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

class TestEnmasseODataExporter(TestCase):
    """ Tests exporting OData connection definitions to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.odata_importer = ODataImporter(self.importer)

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

    def test_odata_export(self):
        self._setup_test_environment()

        # 1. Get OData connection definitions from the YAML template
        odata_list_from_yaml = self.yaml_config['odata']

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_odata_connections, _ = self.odata_importer.sync_definitions(odata_list_from_yaml, self.session)

        self.assertTrue(len(created_odata_connections) > 0, 'No OData connections were created.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('odata', exported_data, 'Exporter did not produce an "odata" section.')
        exported_odata_list = exported_data['odata']

        # 4. Compare exported data with the original YAML data
        self.assertEqual(len(exported_odata_list), len(odata_list_from_yaml),
                         'Number of exported OData connections does not match original YAML.')

        # Create dictionaries keyed by name for easier comparison
        yaml_odata_by_name = {item['name']: item for item in odata_list_from_yaml}
        exported_odata_by_name = {item['name']: item for item in exported_odata_list}

        for name, yaml_def in yaml_odata_by_name.items():

            self.assertIn(name, exported_odata_by_name, f'OData connection "{name}" from YAML not found in export.')
            exported_def = exported_odata_by_name[name]

            # Compare fields that are expected to be exported by ODataExporter
            for field in ['name', 'address', 'odata_version', 'auth_type', 'username', 'token_url', 'tenant_id',
                'client_id', 'scopes']:
                if field in yaml_def and yaml_def[field] is not None:
                    self.assertEqual(exported_def.get(field), yaml_def.get(field),
                                     f'Mismatch for "{field}" in OData connection "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
