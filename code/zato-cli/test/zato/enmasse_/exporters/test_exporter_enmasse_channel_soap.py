# -*- coding: utf-8 -*-
"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

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
from zato.cli.enmasse.exporters.channel_soap import ChannelSOAPExporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.cli.enmasse.importers.group import GroupImporter
from zato.cli.enmasse.importers.channel_soap import ChannelSOAPImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, SASession
    stranydict, SASession = stranydict, SASession

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelSOAPExporter(TestCase):
    """ Tests exporting SOAP channels.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.security_importer = SecurityImporter(self.importer) # Handles all security definition types
        self.group_importer = GroupImporter(self.importer)
        self.channel_soap_importer = ChannelSOAPImporter(self.importer)

        # Exporter is needed to test the export functionality
        self.exporter = EnmasseYAMLExporter()
        self.channel_soap_exporter = ChannelSOAPExporter(self.exporter)

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
        security_defs_from_yaml = self.yaml_config['security']
        created_sec, updated_sec = self.security_importer.sync_security_definitions(security_defs_from_yaml, self.session)
        logger.info('Imported %d security definitions (created=%d, updated=%d)',
            len(created_sec) + len(updated_sec), len(created_sec), len(updated_sec))

        # Import security groups which channels also depend on
        group_defs = self.yaml_config['groups']
        _, _ = self.group_importer.sync_groups(group_defs, self.session)
        self.importer.group_defs = self.group_importer.group_defs

        self.session.commit()

# ################################################################################################################################

    def test_soap_channel_export(self) -> 'None':
        """ Tests the export of SOAP channel definitions.
        """
        self._setup_test_environment()

        # Import channels from YAML
        soap_channels = self.yaml_config['channel_soap']
        logger.info('Importing %d SOAP channels for test', len(soap_channels))

        created, updated = self.channel_soap_importer.sync_channel_soap(soap_channels, self.session)
        logger.info('Imported %d SOAP channels (created=%d, updated=%d)', len(created) + len(updated), len(created), len(updated))

        # Test that the imported channels can be exported correctly
        all_exported_channels = self.channel_soap_exporter.export(self.session, self.importer.cluster_id)

        # Filter exported channels to only include those with names starting with "enmasse"
        exported_channels = [channel for channel in all_exported_channels if channel['name'].startswith('enmasse')]

        logger.info('Exported %d SOAP channels (filtered to %d enmasse channels)',
            len(all_exported_channels), len(exported_channels))

        # Verify the number of exported channels matches the number of imported channels
        self.assertEqual(len(exported_channels), len(created) + len(updated),
            f'Expected {len(created) + len(updated)} exported channels, got {len(exported_channels)}')

        # Extract expected channel data directly from the YAML template
        template_dict = yaml.safe_load(template_complex_01)

        # Build expected fields dictionary from the template
        required_channel_fields = {}
        for channel_def in template_dict['channel_soap']:

            channel_name = channel_def['name']

            # Every SOAP channel round-trips these fields
            channel_required = {
                'name': channel_name,
                'url_path': channel_def['url_path'],
                'service': channel_def['service'],
                'soap_action': channel_def['soap_action'],
                'soap_version': channel_def['soap_version'],
            }

            # Add security if present
            if 'security' in channel_def:
                channel_required['security'] = channel_def['security']

            # Add the MTOM toggle if it is on
            if channel_def.get('use_mtom'):
                channel_required['use_mtom'] = channel_def['use_mtom']

            # Add groups if present
            if 'groups' in channel_def:
                channel_required['groups'] = channel_def['groups']

            # Add rate_limiting if present
            if 'rate_limiting' in channel_def:
                channel_required['rate_limiting'] = channel_def['rate_limiting']

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

        # The channel without MTOM must not export the toggle at all
        channel_1 = [channel for channel in exported_channels if channel['name'] == 'enmasse.channel.soap.1'][0]
        self.assertNotIn('use_mtom', channel_1)

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
