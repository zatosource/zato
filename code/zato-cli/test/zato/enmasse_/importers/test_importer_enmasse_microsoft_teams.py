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
from zato.cli.enmasse.importers.microsoft_teams import MicrosoftTeamsImporter
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

class TestEnmasseMicrosoftTeamsFromYAML(TestCase):
    """ Tests importing Microsoft Teams definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains Microsoft Teams definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize Microsoft Teams importer
        self.microsoft_teams_importer = MicrosoftTeamsImporter(self.importer)

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

    def test_microsoft_teams_definition_creation(self):
        """ Test creating Microsoft Teams definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        microsoft_teams_defs = self.yaml_config['microsoft_teams']

        # Process all Microsoft Teams definitions
        created, updated = self.microsoft_teams_importer.sync_definitions(microsoft_teams_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify Microsoft Teams connection was created correctly
        microsoft_teams = self.session.query(GenericConn).filter_by(
            name='enmasse.chat.microsoft-teams.1',
            type_=GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS
        ).one()

        self.assertEqual(microsoft_teams.client_id, '45678901-4567-4567-4567-4567890abcde')
        self.assertEqual(microsoft_teams.tenant_id, '87654321-7654-7654-7654-fedcba987654')
        self.assertTrue(hasattr(microsoft_teams, 'secret'))

# ################################################################################################################################

    def test_microsoft_teams_update(self):
        """ Test updating existing Microsoft Teams definitions.
        """
        self._setup_test_environment()

        # First, get the Microsoft Teams definition from YAML and create it
        microsoft_teams_defs = self.yaml_config['microsoft_teams']
        microsoft_teams_def = microsoft_teams_defs[0]

        # Create the Microsoft Teams definition
        instance = self.microsoft_teams_importer.create_definition(microsoft_teams_def, self.session)
        self.session.commit()
        original_client_id = microsoft_teams_def['client_id']
        self.assertEqual(instance.client_id, original_client_id)

        # Prepare an update definition based on the existing one
        update_def = {
            'name': microsoft_teams_def['name'],
            'id': instance.id,
            'client_id': '56789012-6789-6789-6789-234567890abc',  # Changed client_id
            'tenant_id': '23456789-9876-9876-9876-abcdef234567'   # Changed tenant_id
        }

        # Update the Microsoft Teams definition
        updated_instance = self.microsoft_teams_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied
        self.assertEqual(updated_instance.client_id, '56789012-6789-6789-6789-234567890abc')
        self.assertEqual(updated_instance.tenant_id, '23456789-9876-9876-9876-abcdef234567')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.CHAT_MICROSOFT_TEAMS)

# ################################################################################################################################

    def test_complete_microsoft_teams_import_flow(self):
        """ Test the complete flow of importing Microsoft Teams definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all Microsoft Teams definitions from the YAML
        microsoft_teams_list = self.yaml_config['microsoft_teams']
        microsoft_teams_created, microsoft_teams_updated = self.microsoft_teams_importer.sync_definitions(
            microsoft_teams_list, self.session)

        # Update importer's Microsoft Teams definitions
        self.importer.microsoft_teams_defs = self.microsoft_teams_importer.connection_defs

        # Verify Microsoft Teams definitions were created
        self.assertEqual(len(microsoft_teams_created), 1)
        self.assertEqual(len(microsoft_teams_updated), 0)

        # Verify the Microsoft Teams definitions dictionary was populated
        self.assertEqual(len(self.microsoft_teams_importer.connection_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.microsoft_teams_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        microsoft_teams_created2, microsoft_teams_updated2 = self.microsoft_teams_importer.sync_definitions(
            microsoft_teams_list, self.session)
        self.assertEqual(len(microsoft_teams_created2), 0)
        self.assertEqual(len(microsoft_teams_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
