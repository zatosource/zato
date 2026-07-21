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
from zato.cli.enmasse.importers.microsoft_fabric import MicrosoftFabricImporter
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

class TestEnmasseMicrosoftFabricFromYAML(TestCase):
    """ Tests importing Microsoft Fabric definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains Microsoft Fabric definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize Microsoft Fabric importer
        self.microsoft_fabric_importer = MicrosoftFabricImporter(self.importer)

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

    def test_microsoft_fabric_definition_creation(self):
        """ Test creating Microsoft Fabric definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        microsoft_fabric_defs = self.yaml_config['microsoft_fabric']

        # Process all Microsoft Fabric definitions
        created, updated = self.microsoft_fabric_importer.sync_definitions(microsoft_fabric_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify Microsoft Fabric connection was created correctly
        microsoft_fabric = self.session.query(GenericConn).filter_by(
            name='enmasse.cloud.microsoft-fabric.1',
            type_=GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_FABRIC
        ).one()

        self.assertEqual(microsoft_fabric.client_id, '34567890-3456-3456-3456-34567890abcd')
        self.assertEqual(microsoft_fabric.tenant_id, '87654321-6543-6543-6543-edcba9876543')
        self.assertEqual(microsoft_fabric.address, 'https://api.fabric.microsoft.com/v1')
        self.assertTrue(hasattr(microsoft_fabric, 'secret'))

# ################################################################################################################################

    def test_microsoft_fabric_update(self):
        """ Test updating existing Microsoft Fabric definitions.
        """
        self._setup_test_environment()

        # First, get the Microsoft Fabric definition from YAML and create it
        microsoft_fabric_defs = self.yaml_config['microsoft_fabric']
        microsoft_fabric_def = microsoft_fabric_defs[0]

        # Create the Microsoft Fabric definition
        instance = self.microsoft_fabric_importer.create_definition(microsoft_fabric_def, self.session)
        self.session.commit()
        original_client_id = microsoft_fabric_def['client_id']
        self.assertEqual(instance.client_id, original_client_id)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': microsoft_fabric_def['name'],
            'id': instance.id,
            'client_id': '45678901-7890-7890-7890-345678901cde',  # Changed client_id
            'tenant_id': '34567890-0987-0987-0987-cdefab345678',  # Changed tenant_id
        }

        # Update the Microsoft Fabric definition
        updated_instance = self.microsoft_fabric_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.client_id, '45678901-7890-7890-7890-345678901cde')
        self.assertEqual(updated_instance.tenant_id, '34567890-0987-0987-0987-cdefab345678')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.CLOUD_MICROSOFT_FABRIC)

# ################################################################################################################################

    def test_complete_microsoft_fabric_import_flow(self):
        """ Test the complete flow of importing Microsoft Fabric definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all Microsoft Fabric definitions from the YAML
        microsoft_fabric_list = self.yaml_config['microsoft_fabric']
        created, updated = self.microsoft_fabric_importer.sync_definitions(microsoft_fabric_list, self.session)

        # Update importer's Microsoft Fabric definitions
        self.importer.microsoft_fabric_defs = self.microsoft_fabric_importer.connection_defs

        # Verify Microsoft Fabric definitions were created
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify the Microsoft Fabric definitions dictionary was populated
        self.assertEqual(len(self.microsoft_fabric_importer.connection_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.microsoft_fabric_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        created2, updated2 = self.microsoft_fabric_importer.sync_definitions(microsoft_fabric_list, self.session)
        self.assertEqual(len(created2), 0)
        self.assertEqual(len(updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
