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
from zato.cli.enmasse.importers.ldap import LDAPImporter
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

class TestEnmasseLDAPFromYAML(TestCase):
    """ Tests importing LDAP connection definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains LDAP definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize LDAP importer
        self.ldap_importer = LDAPImporter(self.importer)

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

    def test_ldap_definition_creation(self):
        """ Test creating LDAP connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        ldap_defs = self.yaml_config['ldap']

        # Process all LDAP definitions
        created, updated = self.ldap_importer.sync_definitions(ldap_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify LDAP connection was created correctly
        ldap = self.session.query(GenericConn).filter_by(
            name='enmasse.ldap.1',
            type_=GENERIC.CONNECTION.TYPE.OUTCONN_LDAP
        ).one()

        self.assertEqual(ldap.username, 'CN=enmasse,OU=testing,OU=Servers,DC=enmasse')
        self.assertEqual(ldap.server_list, '127.0.0.1:389')
        self.assertTrue(hasattr(ldap, 'secret'))

# ################################################################################################################################

    def test_ldap_update(self):
        """ Test updating existing LDAP connection definitions.
        """
        self._setup_test_environment()

        # First, get the LDAP definition from YAML and create it
        ldap_defs = self.yaml_config['ldap']
        ldap_def = ldap_defs[0]

        # Create the LDAP definition
        instance = self.ldap_importer.create_definition(ldap_def, self.session)
        self.session.commit()
        original_username = ldap_def['username']
        self.assertEqual(instance.username, original_username)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': ldap_def['name'],
            'id': instance.id,
            'username': 'CN=updated,OU=testing,OU=Servers,DC=enmasse',  # Changed username
            'server_list': '192.168.1.1:389'  # Changed server_list
        }

        # Update the LDAP definition
        updated_instance = self.ldap_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.username, 'CN=updated,OU=testing,OU=Servers,DC=enmasse')
        self.assertEqual(updated_instance.server_list, '192.168.1.1:389')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.OUTCONN_LDAP)

# ################################################################################################################################

    def test_complete_ldap_import_flow(self):
        """ Test the complete flow of importing LDAP connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all LDAP definitions from the YAML
        ldap_list = self.yaml_config['ldap']
        ldap_created, ldap_updated = self.ldap_importer.sync_definitions(ldap_list, self.session)

        # Update importer's LDAP definitions
        self.importer.ldap_defs = self.ldap_importer.connection_defs

        # Verify LDAP definitions were created
        self.assertEqual(len(ldap_created), 1)
        self.assertEqual(len(ldap_updated), 0)

        # Verify the LDAP definitions dictionary was populated
        self.assertEqual(len(self.ldap_importer.connection_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.ldap_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        ldap_created2, ldap_updated2 = self.ldap_importer.sync_definitions(ldap_list, self.session)
        self.assertEqual(len(ldap_created2), 0)
        self.assertEqual(len(ldap_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
