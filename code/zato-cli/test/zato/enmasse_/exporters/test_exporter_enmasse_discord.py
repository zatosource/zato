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
from zato.cli.enmasse.importers.discord import DiscordImporter
from zato.common.api import Discord
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseDiscordExport(TestCase):
    """ Tests exporting Discord definitions to YAML format using enmasse.
    """

# ################################################################################################################################

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains Discord definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer and exporter
        self.importer = EnmasseYAMLImporter()
        self.exporter = EnmasseYAMLExporter()

        # Initialize Discord importer
        self.discord_importer = DiscordImporter(self.importer)

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

    def test_discord_export(self):
        """ Test exporting Discord definitions to YAML format.
        """
        self._setup_test_environment()

        # Get Discord definitions from YAML
        discord_defs = self.yaml_config['discord']

        # Import the Discord definition first
        created, _ = self.discord_importer.sync_definitions(discord_defs, self.session)
        self.assertEqual(len(created), 1)

        # Export Discord definitions
        exported_discord = self.exporter.export_discord(self.session)
        self.assertIsNotNone(exported_discord)
        self.assertEqual(len(exported_discord), 1)

        # Verify exported data
        exported_item = exported_discord[0]
        self.assertEqual(exported_item['name'], 'enmasse.chat.discord.1')
        self.assertTrue(exported_item['is_active'])
        self.assertEqual(exported_item['address'], Discord.Default.Address)
        self.assertEqual(exported_item['timeout'], Discord.Default.Timeout)
        self.assertEqual(exported_item['default_channel_id'], '123456789012345678')

        # The token is a secret so it must never be exported
        self.assertNotIn('token', exported_item)
        self.assertNotIn('secret', exported_item)

# ################################################################################################################################

    def test_discord_full_export(self):
        """ Test that Discord definitions are included in the full export.
        """
        self._setup_test_environment()

        # Get Discord definitions from YAML
        discord_defs = self.yaml_config['discord']

        # Import the Discord definition first
        _ = self.discord_importer.sync_definitions(discord_defs, self.session)

        # Export all definitions to dict
        exported_dict = self.exporter.export_to_dict(self.session)

        # Verify Discord definitions are included
        self.assertIn('discord', exported_dict)
        self.assertEqual(len(exported_dict['discord']), 1)

        # Verify the data structure matches what was imported
        imported_def = discord_defs[0]
        exported_def = exported_dict['discord'][0]

        self.assertEqual(exported_def['name'], imported_def['name'])
        self.assertEqual(exported_def['default_channel_id'], imported_def['default_channel_id'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
