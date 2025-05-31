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
from zato.cli.enmasse.importers.email_imap import IMAPImporter
from zato.common.odb.model import IMAP
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseEmailIMAPFromYAML(TestCase):
    """ Tests importing IMAP connection definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains connection definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize IMAP importer
        self.imap_importer = IMAPImporter(self.importer)

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

    def test_imap_definition_creation(self):
        """ Test creating IMAP connection definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        imap_defs = self.yaml_config['email_imap']

        # Process all IMAP definitions
        created, updated = self.imap_importer.sync_imap_definitions(imap_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify IMAP connection was created correctly
        imap = self.session.query(IMAP).filter_by(name='enmasse.email.imap.1').one()  # type: ignore
        self.assertEqual(imap.host, 'imap.example.com')
        self.assertEqual(imap.port, 993)
        self.assertEqual(imap.username, 'enmasse@example.com')
        self.assertEqual(imap.mode, 'plain')
        self.assertTrue(hasattr(imap, 'password'))

# ################################################################################################################################

    def test_imap_update(self):
        """ Test updating existing IMAP connection definitions.
        """
        self._setup_test_environment()

        # First, get the IMAP definition from YAML and create it
        imap_defs = self.yaml_config['email_imap']
        imap_def = imap_defs[0]

        # Create the IMAP definition
        instance = self.imap_importer.create_imap_definition(imap_def, self.session)
        self.session.commit()
        original_host = imap_def['host']
        self.assertEqual(instance.host, original_host)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': imap_def['name'],
            'id': instance.id,
            'host': 'imap-updated.example.com',  # Changed host
            'port': 143,  # Changed port
            'mode': 'plain'  # Changed mode
        }

        # Update the IMAP definition
        updated_instance = self.imap_importer.update_imap_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.host, 'imap-updated.example.com')
        self.assertEqual(updated_instance.port, 143)
        self.assertEqual(updated_instance.mode, 'plain')

        # Make sure other fields were preserved from the original YAML definition
        self.assertEqual(updated_instance.username, imap_def['username'])

        # Only check get_criteria if it exists in the definition
        if 'get_criteria' in imap_def:
            self.assertEqual(updated_instance.get_criteria, imap_def['get_criteria'])

# ################################################################################################################################

    def test_complete_imap_import_flow(self):
        """ Test the complete flow of importing IMAP connection definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all IMAP definitions from the YAML
        imap_list = self.yaml_config['email_imap']
        imap_created, imap_updated = self.imap_importer.sync_imap_definitions(imap_list, self.session)

        # Update importer's IMAP definitions
        self.importer.imap_defs = self.imap_importer.imap_defs

        # Verify IMAP definitions were created
        self.assertEqual(len(imap_created), 1)
        self.assertEqual(len(imap_updated), 0)

        # Verify the IMAP definitions dictionary was populated
        self.assertEqual(len(self.imap_importer.imap_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.imap_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        imap_created2, imap_updated2 = self.imap_importer.sync_imap_definitions(imap_list, self.session)
        self.assertEqual(len(imap_created2), 0)
        self.assertEqual(len(imap_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
