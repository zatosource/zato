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

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.exporters.channel_as4 import ChannelAS4Exporter
from zato.cli.enmasse.importers.channel_as4 import ChannelAS4Importer
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import stranydict
    SASession = SASession
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelAS4Exporter(TestCase):
    """ Tests exporting AS4 channels.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Importers are needed to set up the database state for export tests
        self.importer = EnmasseYAMLImporter()
        self.security_importer = SecurityImporter(self.importer)
        self.channel_as4_importer = ChannelAS4Importer(self.importer)

        # Exporter is needed to test the export functionality
        self.exporter = EnmasseYAMLExporter()
        self.channel_as4_exporter = ChannelAS4Exporter(self.exporter)

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

        # Clear existing data before importing
        cleanup_enmasse()
        _ = self.session.commit()

        # Import security definitions first, as AS4 channels may depend on them
        security_defs_from_yaml = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_defs_from_yaml, self.session)
        _ = self.session.commit()

# ################################################################################################################################

    def test_channel_as4_export(self) -> 'None':
        """ Tests the export of AS4 channel definitions.
        """
        self._setup_test_environment()

        # Import the template's AS4 channels first
        channel_as4_list = self.yaml_config['channel_as4']
        created, updated = self.channel_as4_importer.sync_channel_as4(channel_as4_list, self.session)
        _ = self.session.commit()

        logger.info('Imported %d AS4 channels (created=%d, updated=%d)',
            len(created) + len(updated), len(created), len(updated))

        # Export AS4 channels from the database
        cluster_id = self.importer.cluster_id
        exported_channels = self.channel_as4_exporter.export(self.session, cluster_id)
        logger.info('Successfully exported %d AS4 channels', len(exported_channels))

        # The number of exported channels matches the number imported
        self.assertEqual(len(created) + len(updated), len(exported_channels))

        exported_by_name = {}
        for channel in exported_channels:
            exported_by_name[channel['name']] = channel

        # The serviceless Peppol channel round-trips with all its fields
        channel = exported_by_name['enmasse.channel.as4.1']

        self.assertEqual(channel['url_path'], '/enmasse.as4.1')
        self.assertEqual(channel['as4_profile'], 'peppol')
        self.assertEqual(channel['as4_to_party'], 'enmasse-ap')
        self.assertEqual(channel['as4_serviced_participants'], '0192:991825827\n0088:7315458756324')
        self.assertEqual(channel['as4_inbound_topic'], 'enmasse.as4.inbound')

        # There is no routing service and no security, so neither is exported
        self.assertNotIn('service', channel)
        self.assertNotIn('security', channel)

# ################################################################################################################################

    def test_channel_as4_export_service_and_security(self) -> 'None':
        """ Tests that the routing service and security definition round-trip through the exporter.
        """
        self._setup_test_environment()

        channel_as4_list = self.yaml_config['channel_as4']
        _ = self.channel_as4_importer.sync_channel_as4(channel_as4_list, self.session)
        _ = self.session.commit()

        cluster_id = self.importer.cluster_id
        exported_channels = self.channel_as4_exporter.export(self.session, cluster_id)

        exported_by_name = {}
        for channel in exported_channels:
            exported_by_name[channel['name']] = channel

        channel = exported_by_name['enmasse.channel.as4.2']

        self.assertEqual(channel['url_path'], '/enmasse.as4.2')
        self.assertEqual(channel['service'], 'demo.ping')
        self.assertEqual(channel['security'], 'enmasse.basic_auth.1')
        self.assertEqual(channel['as4_profile'], 'edelivery1')
        self.assertEqual(channel['as4_from_party'], 'enmasse-peer')
        self.assertEqual(channel['as4_to_party'], 'enmasse-ap')
        self.assertEqual(channel['as4_service'], 'enmasse:service:1')
        self.assertEqual(channel['as4_action'], 'enmasse:action:1')
        self.assertEqual(channel['as4_extra_pmodes'], 'enmasse:service:2|enmasse:action:2')

        # Fields the channel never had are absent from its export
        self.assertNotIn('as4_serviced_participants', channel)
        self.assertNotIn('as4_signing_key', channel)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
