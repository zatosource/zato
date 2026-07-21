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
from zato.cli.enmasse.importers.odata import ODataImporter
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

class TestEnmasseSAPFromYAML(TestCase):
    """ Tests importing SAP connection definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains SAP definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # SAP is a subtype of the OData implementation so the same importer class handles it
        self.sap_importer = ODataImporter(self.importer, 'sap')

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

    def test_sap_definition_creation(self):
        """ Test creating SAP connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        sap_defs = self.yaml_config['sap']

        # Process all SAP definitions
        created, updated = self.sap_importer.sync_definitions(sap_defs, self.session)

        # Should have created 2 definitions
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # Verify the basic-auth connection was created correctly, under the SAP type, not the OData one
        sap_basic = self.session.query(GenericConn).filter_by(
            name='enmasse.sap.1',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_SAP
        ).one()

        self.assertEqual(sap_basic.address, 'https://example.com/sap/opu/odata/sap/API_BUSINESS_PARTNER/')
        self.assertEqual(sap_basic.username, 'enmasse.sap.user.1')
        self.assertTrue(hasattr(sap_basic, 'secret'))

        # Verify the OAuth2 connection was created correctly
        sap_oauth2 = self.session.query(GenericConn).filter_by(
            name='enmasse.sap.2',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_SAP
        ).one()

        self.assertEqual(sap_oauth2.address, 'https://api4.successfactors.com/odata/v2/')

# ################################################################################################################################

    def test_sap_update(self):
        """ Test updating existing SAP connection definitions.
        """
        self._setup_test_environment()

        # First, get the SAP definition from YAML and create it
        sap_defs = self.yaml_config['sap']
        sap_def = sap_defs[0]

        # Create the SAP definition
        instance = self.sap_importer.create_definition(sap_def, self.session)
        self.session.commit()
        original_address = sap_def['address']
        self.assertEqual(instance.address, original_address)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': sap_def['name'],
            'id': instance.id,
            'address': 'https://updated.example.com/sap/opu/odata/',
            'username': 'enmasse.sap.user.updated',
        }

        # Update the SAP definition
        updated_instance = self.sap_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.address, 'https://updated.example.com/sap/opu/odata/')
        self.assertEqual(updated_instance.username, 'enmasse.sap.user.updated')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.OUTCONN_SAP)

# ################################################################################################################################

    def test_complete_sap_import_flow(self):
        """ Test the complete flow of importing SAP connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all SAP definitions from the YAML
        sap_list = self.yaml_config['sap']
        sap_created, sap_updated = self.sap_importer.sync_definitions(sap_list, self.session)

        # Update importer's SAP definitions
        self.importer.sap_defs = self.sap_importer.connection_defs

        # Verify SAP definitions were created
        self.assertEqual(len(sap_created), 2)
        self.assertEqual(len(sap_updated), 0)

        # Verify the SAP definitions dictionary was populated
        self.assertEqual(len(self.sap_importer.connection_defs), 2)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.sap_defs), 2)

        # Try importing the same definitions again - should result in updates, not creations
        sap_created2, sap_updated2 = self.sap_importer.sync_definitions(sap_list, self.session)
        self.assertEqual(len(sap_created2), 0)
        self.assertEqual(len(sap_updated2), 2)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
