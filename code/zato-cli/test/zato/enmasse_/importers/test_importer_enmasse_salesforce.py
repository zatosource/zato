# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
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
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.salesforce import SalesforceImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseSalesforceFromYAML(TestCase):
    """ Tests importing Salesforce connection definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains Salesforce definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importers
        self.importer = EnmasseYAMLImporter()
        self.salesforce_importer = SalesforceImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self):
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_salesforce_definition_creation(self):
        """ Test creating Salesforce connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        salesforce_defs = self.yaml_config['salesforce']

        # Process all Salesforce definitions
        created, updated = self.salesforce_importer.sync_definitions(salesforce_defs, self.session)

        # Should have created 2 definitions
        created_count = len(created)
        updated_count = len(updated)

        self.assertEqual(created_count, 2)
        self.assertEqual(updated_count, 0)

        # Verify the first connection was created correctly
        salesforce_first = self.session.query(GenericConn).filter_by(
            name='enmasse.salesforce.1',
            type_=GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE
        ).one()

        self.assertEqual(salesforce_first.address, 'https://example.my.salesforce.com')
        self.assertEqual(salesforce_first.username, 'enmasse.salesforce@example.com')
        self.assertTrue(hasattr(salesforce_first, 'secret'))

        # Verify the second connection was created correctly
        salesforce_second = self.session.query(GenericConn).filter_by(
            name='enmasse.salesforce.2',
            type_=GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE
        ).one()

        self.assertEqual(salesforce_second.address, 'https://example2.my.salesforce.com')

# ################################################################################################################################

    def test_salesforce_update(self):
        """ Test updating existing Salesforce connection definitions.
        """
        self._setup_test_environment()

        # First, get the Salesforce definition from YAML and create it
        salesforce_defs = self.yaml_config['salesforce']
        salesforce_def = salesforce_defs[0]

        # Create the Salesforce definition
        instance = self.salesforce_importer.create_definition(salesforce_def, self.session)
        self.session.commit()
        original_address = salesforce_def['address']
        self.assertEqual(instance.address, original_address)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': salesforce_def['name'],
            'id': instance.id,
            'address': 'https://updated.my.salesforce.com',
            'username': 'enmasse.salesforce.updated@example.com',
        }

        # Update the Salesforce definition
        updated_instance = self.salesforce_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.address, 'https://updated.my.salesforce.com')
        self.assertEqual(updated_instance.username, 'enmasse.salesforce.updated@example.com')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.CLOUD_SALESFORCE)

# ################################################################################################################################

    def test_complete_salesforce_import_flow(self):
        """ Test the complete flow of importing Salesforce connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all Salesforce definitions from the YAML
        salesforce_list = self.yaml_config['salesforce']
        salesforce_created, salesforce_updated = self.salesforce_importer.sync_definitions(salesforce_list, self.session)

        # Update importer's Salesforce definitions
        self.importer.salesforce_defs = self.salesforce_importer.connection_defs

        # Verify Salesforce definitions were created
        created_count = len(salesforce_created)
        updated_count = len(salesforce_updated)

        self.assertEqual(created_count, 2)
        self.assertEqual(updated_count, 0)

        # Verify the Salesforce definitions dictionary was populated
        connection_defs_count = len(self.salesforce_importer.connection_defs)
        self.assertEqual(connection_defs_count, 2)

        # Verify that these definitions are accessible from the main importer
        importer_defs_count = len(self.importer.salesforce_defs)
        self.assertEqual(importer_defs_count, 2)

        # Try importing the same definitions again - should result in updates, not creations
        salesforce_created2, salesforce_updated2 = self.salesforce_importer.sync_definitions(salesforce_list, self.session)

        created_count2 = len(salesforce_created2)
        updated_count2 = len(salesforce_updated2)

        self.assertEqual(created_count2, 0)
        self.assertEqual(updated_count2, 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
