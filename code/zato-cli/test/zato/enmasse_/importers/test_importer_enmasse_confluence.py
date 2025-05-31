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
from zato.cli.enmasse.importers.confluence import ConfluenceImporter
from zato.common.api import GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseConfluenceFromYAML(TestCase):
    """ Tests importing Confluence definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains Confluence definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize confluence importer
        self.confluence_importer = ConfluenceImporter(self.importer)

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

    def test_confluence_definition_creation(self):
        """ Test creating Confluence definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        confluence_defs = self.yaml_config['confluence']

        # Process all Confluence definitions
        created, updated = self.confluence_importer.sync_definitions(confluence_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify Confluence connection was created correctly
        confluence = self.session.query(GenericConn).filter_by(
            name='enmasse.confluence.1',
            type_=GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE
        ).one()

        self.assertEqual(confluence.address, 'https://example.atlassian.net')
        self.assertEqual(confluence.username, 'api_user@example.com')
        self.assertTrue(hasattr(confluence, 'secret'))

# ################################################################################################################################

    def test_confluence_update(self):
        """ Test updating existing Confluence definitions.
        """
        self._setup_test_environment()

        # First, get the Confluence definition from YAML and create it
        confluence_defs = self.yaml_config['confluence']
        confluence_def = confluence_defs[0]

        # Create the Confluence definition
        instance = self.confluence_importer.create_definition(confluence_def, self.session)
        self.session.commit()
        original_address = confluence_def['address']
        self.assertEqual(instance.address, original_address)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': confluence_def['name'],
            'id': instance.id,
            'address': 'https://updated.atlassian.net',  # Changed address
            'username': 'updated@example.com'  # Changed username
        }

        # Update the Confluence definition
        updated_instance = self.confluence_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.address, 'https://updated.atlassian.net')
        self.assertEqual(updated_instance.username, 'updated@example.com')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.CLOUD_CONFLUENCE)

# ################################################################################################################################

    def test_complete_confluence_import_flow(self):
        """ Test the complete flow of importing Confluence definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all Confluence definitions from the YAML
        confluence_list = self.yaml_config['confluence']
        confluence_created, confluence_updated = self.confluence_importer.sync_definitions(confluence_list, self.session)

        # Update importer's Confluence definitions
        self.importer.confluence_defs = self.confluence_importer.connection_defs

        # Verify Confluence definitions were created
        self.assertEqual(len(confluence_created), 1)
        self.assertEqual(len(confluence_updated), 0)

        # Verify the Confluence definitions dictionary was populated
        self.assertEqual(len(self.confluence_importer.connection_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.confluence_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        confluence_created2, confluence_updated2 = self.confluence_importer.sync_definitions(confluence_list, self.session)
        self.assertEqual(len(confluence_created2), 0)
        self.assertEqual(len(confluence_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
