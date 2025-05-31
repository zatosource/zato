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
            # SecurityImporter handles all types of security definitions
            _, _ = self.security_importer.sync_security_definitions(security_defs_from_yaml, self.session)

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

            # Add a simple assertion to verify the export worked
            self.assertEqual(len(exported_channels), len(created) + len(updated),  f'Expected {len(created) + len(updated)} exported channels, got {len(exported_channels)}')
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
