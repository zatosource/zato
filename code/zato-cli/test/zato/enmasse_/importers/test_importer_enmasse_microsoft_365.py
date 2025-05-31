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
from zato.cli.enmasse.importers.microsoft_365 import Microsoft365Importer
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

class TestEnmasseMicrosoft365FromYAML(TestCase):
    """ Tests importing Microsoft 365 definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains Microsoft 365 definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

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

    def test_microsoft_365_definition_creation(self):
        """ Test creating Microsoft 365 definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        microsoft_365_defs = self.yaml_config['microsoft_365']

        # Process all Microsoft 365 definitions
        created, updated = self.microsoft_365_importer.sync_definitions(microsoft_365_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify Microsoft 365 connection was created correctly
        microsoft_365 = self.session.query(GenericConn).filter_by(
            name='enmasse.cloud.microsoft365.1',
            type_=GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365
        ).one()

        self.assertEqual(microsoft_365.client_id, '12345678-1234-1234-1234-123456789abc')
        self.assertEqual(microsoft_365.tenant_id, '87654321-4321-4321-4321-cba987654321')
        self.assertTrue(hasattr(microsoft_365, 'secret'))

# ################################################################################################################################

    def test_microsoft_365_update(self):
        """ Test updating existing Microsoft 365 definitions.
        """
        self._setup_test_environment()

        # First, get the Microsoft 365 definition from YAML and create it
        microsoft_365_defs = self.yaml_config['microsoft_365']
        microsoft_365_def = microsoft_365_defs[0]

        # Create the Microsoft 365 definition
        instance = self.microsoft_365_importer.create_definition(microsoft_365_def, self.session)
        self.session.commit()
        original_client_id = microsoft_365_def['client_id']
        self.assertEqual(instance.client_id, original_client_id)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': microsoft_365_def['name'],
            'id': instance.id,
            'client_id': '98765432-5678-5678-5678-123456789abc',  # Changed client_id
            'tenant_id': '12345678-8765-8765-8765-abcdef123456'   # Changed tenant_id
        }

        # Update the Microsoft 365 definition
        updated_instance = self.microsoft_365_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.client_id, '98765432-5678-5678-5678-123456789abc')
        self.assertEqual(updated_instance.tenant_id, '12345678-8765-8765-8765-abcdef123456')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_365)

# ################################################################################################################################

    def test_complete_microsoft_365_import_flow(self):
        """ Test the complete flow of importing Microsoft 365 definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all Microsoft 365 definitions from the YAML
        microsoft_365_list = self.yaml_config['microsoft_365']
        microsoft_365_created, microsoft_365_updated = self.microsoft_365_importer.sync_definitions(microsoft_365_list, self.session)

        # Update importer's Microsoft 365 definitions
        self.importer.microsoft_365_defs = self.microsoft_365_importer.connection_defs

        # Verify Microsoft 365 definitions were created
        self.assertEqual(len(microsoft_365_created), 1)
        self.assertEqual(len(microsoft_365_updated), 0)

        # Verify the Microsoft 365 definitions dictionary was populated
        self.assertEqual(len(self.microsoft_365_importer.connection_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.microsoft_365_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        microsoft_365_created2, microsoft_365_updated2 = self.microsoft_365_importer.sync_definitions(microsoft_365_list, self.session)
        self.assertEqual(len(microsoft_365_created2), 0)
        self.assertEqual(len(microsoft_365_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
