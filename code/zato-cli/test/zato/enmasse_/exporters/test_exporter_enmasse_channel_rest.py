# -*- coding: utf-8 -*-
"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import tempfile
from unittest import TestCase, main
import yaml

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.exporters.channel import ChannelExporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.channel import ChannelImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, SASession

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelRESTExporter(TestCase):
    """ Tests exporting REST channels.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.security_importer = SecurityImporter(self.importer) # Handles all security definition types
        self.group_importer = GroupImporter(self.importer)
        self.channel_importer = ChannelImporter(self.importer)

        # Exporter is needed to test the export functionality
        self.exporter = EnmasseYAMLExporter()
        self.channel_exporter = ChannelExporter(self.exporter)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('SASession', None)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':

        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # Ensure importer has cluster context
        _ = self.importer.get_cluster(self.session)

        # Import security definitions first, as channels may depend on them
        security_defs_from_yaml = self.yaml_config.get('security', [])
        if security_defs_from_yaml:

            # This method already populates self.importer.sec_defs after commit
            created_sec, updated_sec = self.security_importer.sync_security_definitions(security_defs_from_yaml, self.session)
            logger.info('Imported %d security definitions (created=%d, updated=%d)',
                len(created_sec) + len(updated_sec), len(created_sec), len(updated_sec))

            # Verify that security definitions were populated correctly
            logger.info('Security definitions in importer: %s', list(self.importer.sec_defs.keys()))

        self.session.commit()

# ################################################################################################################################

    def test_rest_channel_export(self) -> 'None':
        """ Tests the export of REST channel definitions.
        """
        self._setup_test_environment()

        # Import channels from YAML
        if rest_channels := self.yaml_config.get('channel_rest', []):
            logger.info('Importing %d REST channels for test', len(rest_channels))

            # Process security groups which channels depend on
            group_defs = self.yaml_config.get('groups', [])
            if group_defs:
                # Sync the groups first
                _, _ = self.group_importer.sync_groups(group_defs, self.session)

                # Copy group_defs from group_importer to the main importer
                # to ensure channel_importer can access them
                self.importer.group_defs = self.group_importer.group_defs

            # Import the channel definitions
            self.channel_importer.importer.cluster_id = self.importer.cluster_id
            created, updated = self.channel_importer.sync_channel_rest(rest_channels, self.session)
            logger.info('Imported %d REST channels (created=%d, updated=%d)', len(created) + len(updated), len(created), len(updated))

            # Test that the imported channels can be exported correctly
            exported_channels = self.channel_exporter.export(self.session, self.importer.cluster_id)

            # Log the exported channels
            logger.info('Successfully exported %d REST channels', len(exported_channels))

            # Verify the number of exported channels matches the number of imported channels
            self.assertEqual(len(exported_channels), len(created) + len(updated),
                f'Expected {len(created) + len(updated)} exported channels, got {len(exported_channels)}')

            # Extract expected channel data directly from the YAML template
            # Parse the template to get the expected values
            template_dict = yaml.safe_load(template_complex_01)

            # Build expected fields dictionary from the template
            required_channel_fields = {}
            for channel_def in template_dict.get('channel_rest', []):

                channel_name = channel_def['name']

                # Create a copy of the channel definition for expected fields
                channel_required = {
                    'name': channel_name,
                    'url_path': channel_def.get('url_path'),
                    'service': channel_def.get('service'),
                }

                # Add optional fields if present in the template
                if 'data_format' in channel_def:
                    channel_required['data_format'] = channel_def.get('data_format')

                # Add groups if present (special handling for security groups)
                if 'groups' in channel_def and channel_def['groups']:
                    channel_required['groups'] = channel_def['groups']

                # Add this channel's requirements to our dictionary
                required_channel_fields[channel_name] = channel_required

            # Verify each exported channel against required fields
            for channel in exported_channels:
                name = channel['name']
                self.assertIn(name, required_channel_fields, f'Unexpected channel {name} in export')
                expected = required_channel_fields[name]

                # Check all required fields in the channel definition
                for field, value in expected.items():
                    self.assertIn(field, channel, f'Field {field} missing in channel {name}')

                    # Special handling for list fields like groups
                    if isinstance(value, list):
                        self.assertIsInstance(channel[field], list, f'Field {field} should be a list in channel {name}')
                        for item in value:
                            self.assertIn(item, channel[field], f'Expected {item} in {field} list for channel {name}')
                    else:
                        self.assertEqual(channel[field], value,
                            f'Field {field} has incorrect value in channel {name}, expected {value}, got {channel[field]}')
        else:
            logger.warning('No REST channels found in test YAML template')

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()


# ################################################################################################################################
# ################################################################################################################################
