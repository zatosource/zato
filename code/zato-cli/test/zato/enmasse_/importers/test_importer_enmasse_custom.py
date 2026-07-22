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
from zato.cli.enmasse.importers.custom import CustomConnectorImporter
from zato.common.odb.model import GenericConn
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# Definitions of two custom connector types, as their authors would keep them in an enmasse file.
template_custom_connectors = """
custom_crm:
  - name: enmasse.custom.crm.1
    host: 127.0.0.1
    port: 9950
    api_key: enmasse-api-key-1
  - name: enmasse.custom.crm.2
    host: 10.152.81.19
    api_key: enmasse-api-key-2

custom_billing:
  - name: enmasse.custom.billing.1
    address: https://billing.example.com
    is_sandbox: true
"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseCustomConnectorsFromYAML(TestCase):
    """ Tests importing custom connector definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file with the definitions of the custom connector types
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_custom_connectors.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

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

    def test_custom_definition_creation(self):
        """ Test creating custom connector definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        custom_defs = self.yaml_config['custom_crm']

        # Process all the definitions of the crm type
        custom_importer = CustomConnectorImporter(self.importer, 'custom_crm')
        created, updated = custom_importer.sync_definitions(custom_defs, self.session)

        # Should have created 2 definitions
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # Verify the connection was created with the type derived from the YAML key
        connection = self.session.query(GenericConn).filter_by(
            name='enmasse.custom.crm.1',
            type_='outconn-crm'
        ).one()

        # The column-backed attributes come from the importer's defaults
        self.assertTrue(connection.is_active)
        self.assertFalse(connection.is_internal)
        self.assertFalse(connection.is_channel)
        self.assertTrue(connection.is_outconn)

        # Declared fields whose names match database columns are stored in these columns ..
        self.assertEqual(connection.port, 9950)

        # .. and the remaining ones live in the opaque attributes.
        opaque = parse_instance_opaque_attr(connection)

        self.assertEqual(opaque['host'], '127.0.0.1')
        self.assertEqual(opaque['api_key'], 'enmasse-api-key-1')

# ################################################################################################################################

    def test_custom_update(self):
        """ Test updating existing custom connector definitions.
        """
        self._setup_test_environment()

        # First, get one definition from YAML and create it
        custom_defs = self.yaml_config['custom_crm']
        custom_def = custom_defs[0]

        custom_importer = CustomConnectorImporter(self.importer, 'custom_crm')
        instance = custom_importer.create_definition(custom_def, self.session)
        self.session.commit()

        # Prepare an update definition based on the existing one
        update_def = {
            'name': custom_def['name'],
            'id': instance.id,
            'host': '192.168.1.1',
            'port': 9951,
            'api_key': 'enmasse-api-key-updated',
        }

        # Update the definition
        updated_instance = custom_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied, both to the column-backed field ..
        self.assertEqual(updated_instance.port, 9951)

        # .. and to the fields kept in the opaque attributes.
        opaque = parse_instance_opaque_attr(updated_instance)

        self.assertEqual(opaque['host'], '192.168.1.1')
        self.assertEqual(opaque['api_key'], 'enmasse-api-key-updated')

        # Make sure the type was preserved
        self.assertEqual(updated_instance.type_, 'outconn-crm')

# ################################################################################################################################

    def test_complete_custom_import_flow(self):
        """ Test the complete flow of importing custom connector definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process the whole file - each custom_ key is dispatched to its own importer
        created_objects, updated_objects = self.importer.sync_from_yaml(self.yaml_config, self.session)

        # Both types should have been created, each under its own key
        self.assertEqual(len(created_objects['custom_crm']), 2)
        self.assertEqual(len(created_objects['custom_billing']), 1)
        self.assertNotIn('custom_crm', updated_objects)
        self.assertNotIn('custom_billing', updated_objects)

        # Verify the second type got its own connection type
        connection = self.session.query(GenericConn).filter_by(
            name='enmasse.custom.billing.1',
            type_='outconn-billing'
        ).one()

        # The address matches a database column while is_sandbox is an opaque attribute
        self.assertEqual(connection.address, 'https://billing.example.com')

        opaque = parse_instance_opaque_attr(connection)
        self.assertTrue(opaque['is_sandbox'])

        # Try importing the same definitions again - should result in updates, not creations
        created_objects2, updated_objects2 = self.importer.sync_from_yaml(self.yaml_config, self.session)

        self.assertNotIn('custom_crm', created_objects2)
        self.assertNotIn('custom_billing', created_objects2)
        self.assertEqual(len(updated_objects2['custom_crm']), 2)
        self.assertEqual(len(updated_objects2['custom_billing']), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
