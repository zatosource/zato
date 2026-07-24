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
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.microsoft_teams import MicrosoftTeamsImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseMicrosoftTeamsExport(TestCase):
    """ Tests exporting Microsoft Teams definitions to YAML format using enmasse.
    """

# ################################################################################################################################

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains Microsoft Teams definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer and exporter
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

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

    def test_microsoft_teams_export(self):
        """ Test exporting Microsoft Teams definitions to YAML format.
        """
        self._setup_test_environment()

        # Get Microsoft Teams definitions from YAML
        microsoft_teams_defs = self.yaml_config['microsoft_teams']

        # Import the Microsoft Teams definition first
        created, _ = self.microsoft_teams_importer.sync_definitions(microsoft_teams_defs, self.session)
        self.assertEqual(len(created), 1)

        # Export Microsoft Teams definitions
        exported_microsoft_teams = self.exporter.export_microsoft_teams(self.session)
        self.assertIsNotNone(exported_microsoft_teams)
        self.assertEqual(len(exported_microsoft_teams), 1)

        # Verify exported data
        exported_item = exported_microsoft_teams[0]
        self.assertEqual(exported_item['name'], 'enmasse.chat.microsoft-teams.1')
        self.assertEqual(exported_item['client_id'], '45678901-4567-4567-4567-4567890abcde')
        self.assertEqual(exported_item['tenant_id'], '87654321-7654-7654-7654-fedcba987654')
        self.assertTrue(exported_item.get('is_active'))

        # Verify that scopes are exported correctly
        self.assertEqual(exported_item.get('scopes'), 'https://graph.microsoft.com/.default')

# ################################################################################################################################

    def test_microsoft_teams_full_export(self):
        """ Test that Microsoft Teams definitions are included in the full export.
        """
        self._setup_test_environment()

        # Get Microsoft Teams definitions from YAML
        microsoft_teams_defs = self.yaml_config['microsoft_teams']

        # Import the Microsoft Teams definition first
        _ = self.microsoft_teams_importer.sync_definitions(microsoft_teams_defs, self.session)

        # Export all definitions to dict
        exported_dict = self.exporter.export_to_dict(self.session)

        # Verify Microsoft Teams definitions are included
        self.assertIn('microsoft_teams', exported_dict)
        self.assertEqual(len(exported_dict['microsoft_teams']), 1)

        # Verify the data structure matches what was imported
        imported_def = microsoft_teams_defs[0]
        exported_def = exported_dict['microsoft_teams'][0]

        self.assertEqual(exported_def['name'], imported_def['name'])
        self.assertEqual(exported_def['client_id'], imported_def['client_id'])
        self.assertEqual(exported_def['tenant_id'], imported_def['tenant_id'])
        self.assertEqual(exported_def['scopes'], imported_def['scopes'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
