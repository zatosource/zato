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
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.odoo import OdooImporter
from zato.common.odb.model import OutgoingOdoo
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOdooFromYAML(TestCase):
    """ Tests importing Odoo definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains Odoo definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize odoo importer
        self.odoo_importer = OdooImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

    def test_odoo_definition_creation(self):
        """ Test creating Odoo definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        odoo_defs = self.yaml_config['odoo']

        # Process all Odoo definitions
        created, updated = self.odoo_importer.sync_odoo_definitions(odoo_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify Odoo connection was created correctly
        odoo = self.session.query(OutgoingOdoo).filter_by(name='enmasse.odoo.1').one()
        self.assertEqual(odoo.host, 'odoo.example.com')
        self.assertEqual(odoo.port, 8069)
        self.assertEqual(odoo.user, 'admin')
        self.assertEqual(odoo.database, 'enmasse_db')
        self.assertTrue(hasattr(odoo, 'password'))

    def test_odoo_update(self):
        """ Test updating existing Odoo definitions.
        """
        self._setup_test_environment()

        # First, get the Odoo definition from YAML and create it
        odoo_defs = self.yaml_config['odoo']
        odoo_def = odoo_defs[0]

        # Create the Odoo definition
        instance = self.odoo_importer.create_odoo_definition(odoo_def, self.session)
        self.session.commit()
        original_host = odoo_def['host']
        self.assertEqual(instance.host, original_host)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': odoo_def['name'],
            'id': instance.id,
            'host': 'odoo-updated.example.com',  # Changed host
            'port': 8070  # Changed port
        }

        # Update the Odoo definition
        updated_instance = self.odoo_importer.update_odoo_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.host, 'odoo-updated.example.com')
        self.assertEqual(updated_instance.port, 8070)

        # Make sure other fields were preserved from the original YAML definition
        self.assertEqual(updated_instance.user, odoo_def['user'])
        self.assertEqual(updated_instance.database, odoo_def['database'])

    def test_complete_odoo_import_flow(self):
        """ Test the complete flow of importing Odoo definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all Odoo definitions from the YAML
        odoo_list = self.yaml_config['odoo']
        odoo_created, odoo_updated = self.odoo_importer.sync_odoo_definitions(odoo_list, self.session)

        # Update importer's Odoo definitions
        self.importer.odoo_defs = self.odoo_importer.odoo_defs

        # Verify Odoo definitions were created
        self.assertEqual(len(odoo_created), 1)
        self.assertEqual(len(odoo_updated), 0)

        # Verify the Odoo definitions dictionary was populated
        self.assertEqual(len(self.odoo_importer.odoo_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.odoo_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        odoo_created2, odoo_updated2 = self.odoo_importer.sync_odoo_definitions(odoo_list, self.session)
        self.assertEqual(len(odoo_created2), 0)
        self.assertEqual(len(odoo_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
