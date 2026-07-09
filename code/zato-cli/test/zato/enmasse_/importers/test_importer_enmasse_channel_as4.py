# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import tempfile
from json import loads
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.channel_as4 import ChannelAS4Importer
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.odb.model import HTTPSOAP, Service
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_, stranydict = any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelAS4FromYAML(TestCase):
    """ Tests importing AS4 channels from YAML files using enmasse.
    """

    def setUp(self) -> 'None':
        # Server path for database connection
        self.server_path = default_server_base_dir

        # Create a temporary file using the existing template which already contains AS4 channels
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize security importer (needed for channels with security)
        self.security_importer = SecurityImporter(self.importer)
        self.importer.sec_defs = {} # Initialize sec_defs

        # Initialize AS4 channel importer
        self.channel_as4_importer = ChannelAS4Importer(self.importer)

        # Parse the YAML file
        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

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

        # Get the cluster instance from the database
        self.importer.cluster = self.importer.get_cluster(self.session)

        # Create security definitions first since AS4 channels may use them
        security_list = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_list, self.session)

# ################################################################################################################################

    def test_channel_as4_creation(self):
        """ Test creating AS4 channels from YAML.
        """
        self._setup_test_environment()

        # Get AS4 channel definitions from YAML
        channel_as4_defs = self.yaml_config['channel_as4']

        # Process all AS4 channel definitions
        created, updated = self.channel_as4_importer.sync_channel_as4(channel_as4_defs, self.session)

        # Should have created all channels from the template
        self.assertEqual(len(created), 2)  # There are 2 AS4 channels in template_complex_01
        self.assertEqual(len(updated), 0)

        # Verify the serviceless Peppol channel was created correctly - its messages
        # route to a pub/sub topic because there is no service configured.
        channel = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.channel.as4.1',
            connection=CONNECTION.CHANNEL,
            transport=URL_TYPE.AS4
        ).one()

        self.assertEqual(channel.url_path, '/enmasse.as4.1')
        self.assertIsNone(channel.service_id)
        self.assertIsNone(channel.security_id)

        # The AS4 fields travel in the opaque attributes
        opaque = loads(channel.opaque1)
        self.assertEqual(opaque['as4_profile'], 'peppol')
        self.assertEqual(opaque['as4_to_party'], 'enmasse-ap')
        self.assertEqual(opaque['as4_serviced_participants'], '0192:991825827\n0088:7315458756324')
        self.assertEqual(opaque['as4_inbound_topic'], 'enmasse.as4.inbound')

# ################################################################################################################################

    def test_channel_as4_creation_with_service_and_security(self):
        """ Test that a channel with a routing service and HTTP-level security keeps both.
        """
        self._setup_test_environment()

        channel_as4_defs = self.yaml_config['channel_as4']
        _ = self.channel_as4_importer.sync_channel_as4(channel_as4_defs, self.session)

        channel = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.channel.as4.2',
            connection=CONNECTION.CHANNEL,
            transport=URL_TYPE.AS4
        ).one()

        # The column-level fields first ..
        self.assertEqual(channel.url_path, '/enmasse.as4.2')
        self.assertIsNotNone(channel.security_id)

        # .. the routing service points to the configured one ..
        service = self.session.query(Service).filter_by(id=channel.service_id).one()
        self.assertEqual(service.name, 'demo.ping')

        # .. and the AS4 fields are carried in the opaque attributes.
        opaque = loads(channel.opaque1)

        self.assertEqual(opaque['as4_profile'], 'edelivery1')
        self.assertEqual(opaque['as4_from_party'], 'enmasse-peer')
        self.assertEqual(opaque['as4_to_party'], 'enmasse-ap')
        self.assertEqual(opaque['as4_service'], 'enmasse:service:1')
        self.assertEqual(opaque['as4_action'], 'enmasse:action:1')
        self.assertEqual(opaque['as4_extra_pmodes'], 'enmasse:service:2|enmasse:action:2')

# ################################################################################################################################

    def test_channel_as4_reimport_detects_no_changes(self):
        """ Test that importing the same YAML twice detects no changes the second time,
        including for the AS4 fields kept in the opaque attributes.
        """
        self._setup_test_environment()

        channel_as4_defs = self.yaml_config['channel_as4']

        created, updated = self.channel_as4_importer.sync_channel_as4(channel_as4_defs, self.session)
        self.assertEqual(len(created), 2)
        self.assertEqual(len(updated), 0)

        # The second, identical import must be a no-op.
        created, updated = self.channel_as4_importer.sync_channel_as4(channel_as4_defs, self.session)
        self.assertEqual(len(created), 0)
        self.assertEqual(len(updated), 0)

# ################################################################################################################################

    def test_channel_as4_update_opaque_fields(self):
        """ Test that updates to the AS4 fields persist and that untouched opaque fields survive an update.
        """
        self._setup_test_environment()

        channel_as4_defs = self.yaml_config['channel_as4']
        _ = self.channel_as4_importer.sync_channel_as4(channel_as4_defs, self.session)

        channel = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.channel.as4.1',
            connection=CONNECTION.CHANNEL,
            transport=URL_TYPE.AS4
        ).one()

        # Change some of the AS4 fields, leave others out of the update entirely.
        update_def = {
            'name': 'enmasse.channel.as4.1',
            'id': channel.id,
            'as4_serviced_participants': '0192:991825827',
            'as4_trust_anchors': '-----BEGIN CERTIFICATE-----\nnew-root\n-----END CERTIFICATE-----',
        }

        _ = self.channel_as4_importer.update_channel_as4(update_def, self.session)
        self.session.commit()

        self.session.expire_all()
        channel = self.session.query(HTTPSOAP).filter_by(id=channel.id).one()
        opaque = loads(channel.opaque1)

        # The updated fields carry their new values ..
        self.assertEqual(opaque['as4_serviced_participants'], '0192:991825827')
        self.assertEqual(opaque['as4_trust_anchors'], '-----BEGIN CERTIFICATE-----\nnew-root\n-----END CERTIFICATE-----')

        # .. while the fields the update did not mention are preserved.
        self.assertEqual(opaque['as4_profile'], 'peppol')
        self.assertEqual(opaque['as4_inbound_topic'], 'enmasse.as4.inbound')

# ################################################################################################################################

    def test_channel_as4_update_assigns_service(self):
        """ Test that an update can attach a routing service to a channel that had none.
        """
        self._setup_test_environment()

        channel_as4_defs = self.yaml_config['channel_as4']
        _ = self.channel_as4_importer.sync_channel_as4(channel_as4_defs, self.session)

        channel = self.session.query(HTTPSOAP).filter_by(
            name='enmasse.channel.as4.1',
            connection=CONNECTION.CHANNEL,
            transport=URL_TYPE.AS4
        ).one()
        self.assertIsNone(channel.service_id)

        update_def = {
            'name': 'enmasse.channel.as4.1',
            'id': channel.id,
            'service': 'demo.ping',
        }

        updated_instance = self.channel_as4_importer.update_channel_as4(update_def, self.session)
        self.session.commit()

        service = self.session.query(Service).filter_by(id=updated_instance.service_id).one()
        self.assertEqual(service.name, 'demo.ping')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
