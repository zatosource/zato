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
from zato.cli.enmasse.importers.odoo import OdooImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOdooExporter(TestCase):
    """ Tests exporting Odoo connections to YAML-compatible dicts using enmasse.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importer is needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.odoo_importer = OdooImporter(self.importer)

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

    def test_odoo_export(self):
        self._setup_test_environment()

        # 1. Get Odoo connection definitions from the YAML template
        odoo_list_from_yaml = self.yaml_config.get('odoo', [])

        # 2. Import these definitions into the database to have something to export
        _ = self.importer.get_cluster(self.session) # Ensure importer has cluster context
        created_odoo_connections, _ = self.odoo_importer.sync_odoo_definitions(odoo_list_from_yaml, self.session)
        self.session.commit()

        self.assertTrue(len(created_odoo_connections) > 0,  'No Odoo connections were created from YAML.')

        # 3. Initialize the exporter and export the data
        yaml_exporter = EnmasseYAMLExporter()
        exported_data = yaml_exporter.export_to_dict(self.session)

        self.assertIn('odoo', exported_data, 'Exporter did not produce an "odoo" section.')
        exported_odoo_list = exported_data['odoo']

        # 4. Compare exported data with the original YAML data
        self.assertEqual(len(exported_odoo_list), len(odoo_list_from_yaml), 'Number of exported Odoo connections does not match original YAML.')

        # Create dictionaries keyed by name for easier comparison
        yaml_odoo_by_name = {item['name']: item for item in odoo_list_from_yaml}
        exported_odoo_by_name = {item['name']: item for item in exported_odoo_list}

        for name, yaml_def in yaml_odoo_by_name.items():

            self.assertIn(name, exported_odoo_by_name, f'Odoo connection "{name}" from YAML not found in export.')
            exported_def = exported_odoo_by_name[name]

            # Compare fields that are expected to be exported by OdooExporter
            # Note: password is not exported for security reasons
            for field in ['name', 'is_active', 'host', 'port', 'user', 'database', 'protocol']:
                if field in yaml_def:
                    self.assertEqual(exported_def.get(field), yaml_def.get(field), f'Mismatch for "{field}" in Odoo connection "{name}"')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
