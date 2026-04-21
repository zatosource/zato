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
from zato.cli.enmasse.importers.jira import JiraImporter
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

class TestEnmasseJiraFromYAML(TestCase):
    """ Tests importing JIRA definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file using the existing template which already contains JIRA definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize JIRA importer
        self.jira_importer = JiraImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
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

    def test_jira_definition_creation(self):
        """ Test creating JIRA definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        jira_defs = self.yaml_config['jira']

        # Process all JIRA definitions
        created, updated = self.jira_importer.sync_definitions(jira_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify JIRA connection was created correctly
        jira = self.session.query(GenericConn).filter_by(
            name='enmasse.jira.1',
            type_=GENERIC.CONNECTION.TYPE.CLOUD_JIRA
        ).one()

        self.assertEqual(jira.address, 'https://example.atlassian.net')
        self.assertEqual(jira.username, 'enmasse@example.com')
        self.assertTrue(hasattr(jira, 'secret'))

# ################################################################################################################################

    def test_jira_update(self):
        """ Test updating existing JIRA definitions.
        """
        self._setup_test_environment()

        # First, get the JIRA definition from YAML and create it
        jira_defs = self.yaml_config['jira']
        jira_def = jira_defs[0]

        # Create the JIRA definition
        instance = self.jira_importer.create_definition(jira_def, self.session)
        _ = self.session.commit()
        original_address = jira_def['address']
        self.assertEqual(instance.address, original_address)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': jira_def['name'],
            'id': instance.id,
            'address': 'https://updated.atlassian.net',  # Changed address
            'username': 'updated@example.com'  # Changed username
        }

        # Update the JIRA definition
        updated_instance = self.jira_importer.update_definition(update_def, self.session)
        _ = self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.address, 'https://updated.atlassian.net')
        self.assertEqual(updated_instance.username, 'updated@example.com')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.CLOUD_JIRA)

# ################################################################################################################################

    def test_complete_jira_import_flow(self):
        """ Test the complete flow of importing JIRA definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all JIRA definitions from the YAML
        jira_list = self.yaml_config['jira']
        jira_created, jira_updated = self.jira_importer.sync_definitions(jira_list, self.session)

        # Update importer's JIRA definitions
        self.importer.jira_defs = self.jira_importer.connection_defs

        # Verify JIRA definitions were created
        self.assertEqual(len(jira_created), 1)
        self.assertEqual(len(jira_updated), 0)

        # Verify the JIRA definitions dictionary was populated
        self.assertEqual(len(self.jira_importer.connection_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.jira_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        jira_created2, jira_updated2 = self.jira_importer.sync_definitions(jira_list, self.session)
        self.assertEqual(len(jira_created2), 0)
        self.assertEqual(len(jira_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
