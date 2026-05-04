# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import tempfile
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelRESTImporter(TestCase):
    """ Tests importing REST channels.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        # Create a temporary file for YAML content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize specialized importers
        self.security_importer = SecurityImporter(self.importer)
        self.channel_importer = ChannelImporter(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

        # Channel name with security groups
        self.channel_with_groups = 'enmasse.channel.rest.4'

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

    def test_channel_rest_creation(self):
        """ Test the creation of REST channels.
        """
        self._setup_test_environment()

        # First process security definitions which channels depend on
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)

        # Also process security groups which some channels use
        _ = self.importer.sync_groups(self.yaml_config['groups'], self.session)

        # Filter only REST channel definitions
        channel_defs = self.yaml_config['channel_rest']
        self.assertTrue(len(channel_defs) > 0, 'No REST channel definitions found in YAML')

        # Process channel definitions
        channels_created, _ = self.channel_importer.sync_channel_rest(channel_defs, self.session)

        # Assert the correct number of items were created
        self.assertEqual(len(channels_created), len(channel_defs), 'Not all REST channels were created')

        # Verify specific channels were created correctly
        for channel in channels_created:
            self.assertTrue(channel.name.startswith('enmasse.channel.rest.'))
            self.assertTrue(channel.url_path.startswith('/enmasse.rest.'))
            self.assertEqual(channel.connection, 'channel')
            self.assertEqual(channel.transport, 'plain_http')

            # Check for channel with security
            if channel.name == 'enmasse.channel.rest.3':
                # Verify that security was configured properly
                # Find the channel definition in YAML using a loop
                channel_def = None
                for channel_def in channel_defs:
                    if channel_def['name'] == channel.name:
                        channel_def = channel_def
                        break

                self.assertIsNotNone(channel_def, f'Channel definition not found for {channel.name}')
                self.assertIn('security', channel_def, 'Channel should have security defined in YAML') # type: ignore

                # Ensure the security name in YAML exists in the importer's security definitions
                security_name = channel_def['security'] # type: ignore
                self.assertIn(security_name, self.importer.sec_defs, f'Security definition {security_name} not found')

            # Check for channel with data_format
            if channel.name in ['enmasse.channel.rest.2', 'enmasse.channel.rest.3']:
                self.assertEqual(channel.data_format, 'json', f'Wrong data_format for {channel.name}')

# ################################################################################################################################
# ################################################################################################################################

    def test_channel_rest_security_groups(self):
        """ Test that security groups are correctly processed during REST channel import.
        """
        self._setup_test_environment()

        # First process security definitions which channels depend on
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)

        # Process security groups
        _ = self.importer.sync_groups(self.yaml_config['groups'], self.session)

        # Verify group definitions are stored correctly
        self.assertTrue(len(self.importer.group_defs) > 0, 'No group definitions found')
        self.assertIn('enmasse.group.1', self.importer.group_defs, 'Group 1 not found in group_defs')
        self.assertIn('enmasse.group.2', self.importer.group_defs, 'Group 2 not found in group_defs')

        # Process channel definitions
        channel_defs = self.yaml_config['channel_rest']
        channels_created, _ = self.channel_importer.sync_channel_rest(channel_defs, self.session)

        # Find the channel that should have groups
        channel_with_groups = cast_('any_', None)
        for channel in channels_created:
            if channel.name == self.channel_with_groups:
                channel_with_groups = channel
                break

        # Verify the channel with groups was created
        self.assertIsNotNone(channel_with_groups, f'Channel {self.channel_with_groups} not found')

        # Verify the channel has the opaque1 attribute with security groups
        self.assertIsNotNone(channel_with_groups.opaque1, 'Channel should have opaque1 attribute')

        opaque_attrs = json.loads(channel_with_groups.opaque1)

        # Verify security groups are in opaque1
        self.assertIn('security_groups', opaque_attrs, 'security_groups not found in opaque1')
        self.assertIsInstance(opaque_attrs['security_groups'], list, 'security_groups should be a list')
        self.assertTrue(len(opaque_attrs['security_groups']) > 0, 'No security groups found in opaque1')

        # Verify the correct number of groups were processed
        # We expect 2 groups from the YAML: enmasse.group.1 and enmasse.group.2
        expected_group_count = 2
        self.assertEqual(len(opaque_attrs['security_groups']), expected_group_count,
                         f'Expected {expected_group_count} security groups, found {len(opaque_attrs["security_groups"])}')

    def test_channel_rest_rate_limiting(self) -> 'None':
        """ Test that rate_limiting is correctly stored in opaque1 during REST channel import.
        """
        self._setup_test_environment()

        # First process security definitions which channels depend on
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)

        # Process security groups
        _ = self.importer.sync_groups(self.yaml_config['groups'], self.session)

        # Process channel definitions
        channel_defs = self.yaml_config['channel_rest']
        channels_created, _ = self.channel_importer.sync_channel_rest(channel_defs, self.session)

        # Find channels with rate_limiting
        channel_rest_2 = cast_('any_', None)
        channel_rest_3 = cast_('any_', None)

        for channel in channels_created:
            if channel.name == 'enmasse.channel.rest.2':
                channel_rest_2 = channel
            elif channel.name == 'enmasse.channel.rest.3':
                channel_rest_3 = channel

        # Verify channel_rest_2 has a simple rate limiting rule
        self.assertIsNotNone(channel_rest_2, 'Channel enmasse.channel.rest.2 not found')
        self.assertIsNotNone(channel_rest_2.opaque1, 'Channel rest.2 should have opaque1')

        opaque_2 = json.loads(channel_rest_2.opaque1)
        self.assertIn('rate_limiting', opaque_2)

        rules_2 = opaque_2['rate_limiting']
        self.assertEqual(len(rules_2), 1)
        self.assertEqual(rules_2[0]['limit'], 1000)
        self.assertEqual(rules_2[0]['limit_unit'], 'day')
        self.assertTrue(rules_2[0]['is_all_day'])

        # Verify channel_rest_3 has two rate limiting rules
        self.assertIsNotNone(channel_rest_3, 'Channel enmasse.channel.rest.3 not found')
        self.assertIsNotNone(channel_rest_3.opaque1, 'Channel rest.3 should have opaque1')

        opaque_3 = json.loads(channel_rest_3.opaque1)
        self.assertIn('rate_limiting', opaque_3)

        rules_3 = opaque_3['rate_limiting']
        self.assertEqual(len(rules_3), 2)

        # First rule - time range with two CIDR entries
        self.assertEqual(rules_3[0]['limit'], 100)
        self.assertEqual(rules_3[0]['limit_unit'], 'minute')
        self.assertFalse(rules_3[0]['is_all_day'])
        self.assertEqual(rules_3[0]['time_from'], '08:00')
        self.assertEqual(rules_3[0]['time_to'], '17:00')
        self.assertEqual(len(rules_3[0]['cidr_list']), 2)

        # Second rule - all-day, disabled, disallowed
        self.assertEqual(rules_3[1]['limit'], 50)
        self.assertEqual(rules_3[1]['limit_unit'], 'hour')
        self.assertTrue(rules_3[1]['disabled'])
        self.assertTrue(rules_3[1]['disallowed'])

# ################################################################################################################################

    def test_channel_rest_rate_limiting_update(self) -> 'None':
        """ Test that rate_limiting is correctly updated on an existing channel.
        """
        self._setup_test_environment()

        # First process security definitions which channels depend on
        _ = self.security_importer.sync_security_definitions(self.yaml_config['security'], self.session)

        # Process security groups
        _ = self.importer.sync_groups(self.yaml_config['groups'], self.session)

        # Create channels first
        channel_defs = self.yaml_config['channel_rest']
        channels_created, _ = self.channel_importer.sync_channel_rest(channel_defs, self.session)
        self.assertTrue(len(channels_created) > 0)

        # Run sync again - channels should be updated, not created
        _, channels_updated = self.channel_importer.sync_channel_rest(channel_defs, self.session)

        # No updates should be needed since nothing changed
        self.assertEqual(len(channels_updated), 0, 'No updates expected when reimporting same data')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
