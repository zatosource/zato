# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.odata import ODataImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
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

class TestEnmasseODataFromYAML(TestCase):
    """ Tests importing OData connection definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = default_server_base_dir

        # Create a temporary file using the existing template which already contains OData definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize OData importer
        self.odata_importer = ODataImporter(self.importer)

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

    def test_odata_definition_creation(self):
        """ Test creating OData connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        odata_defs = self.yaml_config['odata']

        # Process all OData definitions
        created, updated = self.odata_importer.sync_definitions(odata_defs, self.session)

        # Should have created 2 definitions
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # Verify the basic-auth V2 connection was created correctly
        odata_v2 = self.session.query(GenericConn).filter_by(
            name='enmasse.odata.1',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_ODATA
        ).one()

        self.assertEqual(odata_v2.address, 'https://example.com/sap/opu/odata/sap/API_SALES_ORDER_SRV/')
        self.assertEqual(odata_v2.username, 'enmasse.odata.user.1')
        self.assertTrue(hasattr(odata_v2, 'secret'))

        # Verify the OAuth2 V4 connection was created correctly
        odata_v4 = self.session.query(GenericConn).filter_by(
            name='enmasse.odata.2',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_ODATA
        ).one()

        self.assertEqual(odata_v4.address, 'https://example.com/v2.0/test-tenant/sandbox/api/v2.0/')

# ################################################################################################################################

    def test_odata_update(self):
        """ Test updating existing OData connection definitions.
        """
        self._setup_test_environment()

        # First, get the OData definition from YAML and create it
        odata_defs = self.yaml_config['odata']
        odata_def = odata_defs[0]

        # Create the OData definition
        instance = self.odata_importer.create_definition(odata_def, self.session)
        self.session.commit()
        original_address = odata_def['address']
        self.assertEqual(instance.address, original_address)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': odata_def['name'],
            'id': instance.id,
            'address': 'https://updated.example.com/odata/',
            'username': 'enmasse.odata.user.updated',
        }

        # Update the OData definition
        updated_instance = self.odata_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.address, 'https://updated.example.com/odata/')
        self.assertEqual(updated_instance.username, 'enmasse.odata.user.updated')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.OUTCONN_ODATA)

# ################################################################################################################################

    def test_complete_odata_import_flow(self):
        """ Test the complete flow of importing OData connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all OData definitions from the YAML
        odata_list = self.yaml_config['odata']
        odata_created, odata_updated = self.odata_importer.sync_definitions(odata_list, self.session)

        # Update importer's OData definitions
        self.importer.odata_defs = self.odata_importer.connection_defs

        # Verify OData definitions were created
        self.assertEqual(len(odata_created), 2)
        self.assertEqual(len(odata_updated), 0)

        # Verify the OData definitions dictionary was populated
        self.assertEqual(len(self.odata_importer.connection_defs), 2)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.odata_defs), 2)

        # Try importing the same definitions again - should result in updates, not creations
        odata_created2, odata_updated2 = self.odata_importer.sync_definitions(odata_list, self.session)
        self.assertEqual(len(odata_created2), 0)
        self.assertEqual(len(odata_updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
