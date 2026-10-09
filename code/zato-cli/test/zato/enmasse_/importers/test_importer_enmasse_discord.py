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
from zato.cli.enmasse.importers.discord import DiscordImporter
from zato.cli.enmasse.util.secrets import decrypt_secret, is_encrypted
from zato.common.api import Discord, GENERIC
from zato.common.odb.model import GenericConn
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseDiscordFromYAML(TestCase):
    """ Tests importing Discord definitions from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        environment = get_shared_environment()
        self.server_path = environment.server_dir

        # Create a temporary file using the existing template which already contains Discord definitions
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

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

    def test_discord_definition_creation(self):
        """ Test creating Discord definitions from YAML.
        """
        self._setup_test_environment()

        # Get definitions from YAML
        discord_defs = self.yaml_config['discord']

        # Process all Discord definitions
        created, updated = self.discord_importer.sync_definitions(discord_defs, self.session)

        # Should have created 1 definition
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        # Verify the Discord connection was created correctly
        discord = self.session.query(GenericConn).filter_by(
            name='enmasse.chat.discord.1',
            type_=GENERIC.CONNECTION.TYPE.CHAT_DISCORD
        ).one()

        self.assertTrue(discord.is_active)
        self.assertEqual(discord.address, Discord.Default.Address)
        self.assertTrue(is_encrypted(discord.secret))

        # The default channel and the timeout are opaque attributes
        opaque = parse_instance_opaque_attr(discord)
        self.assertEqual(opaque['default_channel_id'], '123456789012345678')
        self.assertEqual(opaque['timeout'], Discord.Default.Timeout)

        # The token is in the secret column only
        self.assertNotIn('token', opaque)

# ################################################################################################################################

    def test_discord_update(self):
        """ Test updating existing Discord definitions.
        """
        self._setup_test_environment()

        # First, get the Discord definition from YAML and create it
        discord_defs = self.yaml_config['discord']
        discord_def = discord_defs[0]

        # Create the Discord definition
        instance = self.discord_importer.create_definition(discord_def, self.session)
        self.session.commit()
        self.assertEqual(instance.name, discord_def['name'])

        # Prepare an update definition based on the existing one, with a new token and a new default channel
        update_def = {
            'name': discord_def['name'],
            'id': instance.id,
            'token': 'updated-test-token',
            'default_channel_id': '987654321098765432',
        }

        # Update the Discord definition
        updated_instance = self.discord_importer.update_definition(update_def, self.session)
        self.session.commit()

        # Verify the update was applied and the token is stored encrypted
        self.assertTrue(is_encrypted(updated_instance.secret))
        self.assertEqual(decrypt_secret(self.session, updated_instance.secret), 'updated-test-token')

        opaque = parse_instance_opaque_attr(updated_instance)
        self.assertEqual(opaque['default_channel_id'], '987654321098765432')

        # Make sure other fields were preserved
        self.assertEqual(updated_instance.type_, GENERIC.CONNECTION.TYPE.CHAT_DISCORD)

# ################################################################################################################################

    def test_complete_discord_import_flow(self):
        """ Test the complete flow of importing Discord definitions from a YAML file.
        """
        self._setup_test_environment()

        # Process all Discord definitions from the YAML
        discord_list = self.yaml_config['discord']
        discord_created, discord_updated = self.discord_importer.sync_definitions(discord_list, self.session)

        # Update importer's Discord definitions
        self.importer.discord_defs = self.discord_importer.connection_defs

        # Verify Discord definitions were created
        self.assertEqual(len(discord_created), 1)
        self.assertEqual(len(discord_updated), 0)

        # Verify the Discord definitions dictionary was populated
        self.assertEqual(len(self.discord_importer.connection_defs), 1)

        # Verify that these definitions are accessible from the main importer
        self.assertEqual(len(self.importer.discord_defs), 1)

        # Try importing the same definitions again - should result in updates, not creations
        discord_created2, discord_updated2 = self.discord_importer.sync_definitions(discord_list, self.session)
        self.assertEqual(len(discord_created2), 0)
        self.assertEqual(len(discord_updated2), 1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
