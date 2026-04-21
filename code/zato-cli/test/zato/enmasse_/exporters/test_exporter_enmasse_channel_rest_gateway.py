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
from zato.cli.enmasse.exporters.channel_rest import ChannelExporter
from zato.cli.enmasse.importers.channel_rest import ChannelImporter
from zato.common.test.enmasse_._template_rest_gateway import template_rest_gateway
from zato.common.typing_ import cast_

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

class TestEnmasseChannelRESTGatewayExporter(TestCase):
    """ Tests exporting REST channels with gateway_service_list.
    """

    def setUp(self) -> 'None':
        self.server_path = os.path.expanduser('~/env/qs-1/server1')

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_rest_gateway.encode('utf-8'))
        self.temp_file.close()

        self.importer = EnmasseYAMLImporter()
        self.channel_importer = ChannelImporter(self.importer)

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

        _ = self.importer.get_cluster(self.session)

        self.session.commit()

# ################################################################################################################################

    def test_rest_channel_gateway_export(self) -> 'None':
        """ Tests the export of REST channels with gateway_service_list.
        """
        self._setup_test_environment()

        if rest_channels := self.yaml_config.get('channel_rest', []):
            logger.info('Importing %d REST channels for test', len(rest_channels))

            self.channel_importer.importer.cluster_id = self.importer.cluster_id
            created, updated = self.channel_importer.sync_channel_rest(rest_channels, self.session)
            logger.info('Imported %d REST channels', len(created) + len(updated))

            all_exported_channels = self.channel_exporter.export(self.session, self.importer.cluster_id)

            exported_channels = [
                channel for channel in all_exported_channels
                if channel['name'].startswith('enmasse.channel.rest.gateway')
            ]

            self.assertEqual(len(exported_channels), 2, 'Expected 2 exported gateway channels')

            channel_with_gateway:'anydict' = {}
            channel_without_gateway:'anydict' = {}

            for channel in exported_channels:
                if channel['name'] == 'enmasse.channel.rest.gateway.1':
                    channel_with_gateway = channel
                elif channel['name'] == 'enmasse.channel.rest.gateway.2':
                    channel_without_gateway = channel

            self.assertIsNotNone(channel_with_gateway, 'Channel with gateway not found in export')
            self.assertIsNotNone(channel_without_gateway, 'Channel without gateway not found in export')

            self.assertIn('gateway_service_list', channel_with_gateway,
                'gateway_service_list should be in exported channel')
            self.assertIsInstance(channel_with_gateway['gateway_service_list'], list,
                'gateway_service_list should be a list')

            expected_list = ['demo.ping', 'api.my-service']
            self.assertEqual(channel_with_gateway['gateway_service_list'], expected_list,
                'gateway_service_list values mismatch')

            self.assertNotIn('gateway_service_list', channel_without_gateway,
                'gateway_service_list should not be in channel without it')

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
