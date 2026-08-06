# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

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
from zato.cli.enmasse.importers.channel_mllp import ChannelMLLPImporter
from zato.cli.enmasse.importers.security import SecurityImporter
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.typing_ import cast_
from zato.common.defaults import default_server_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseChannelMLLPImporter(TestCase):
    """ Tests importing HL7 MLLP channels.
    """

    def setUp(self) -> 'None':

        # Server path for database connection
        self.server_path = default_server_base_dir

        # Create a temporary file for YAML content
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        _ = self.temp_file.write(template_complex_01.encode('utf-8'))
        self.temp_file.close()

        # Initialize the importer
        self.importer = EnmasseYAMLImporter()

        # Initialize the HL7 MLLP channel importer
        self.channel_mllp_importer = ChannelMLLPImporter(self.importer)

        # A channel may name a security definition, so the definitions have to exist first
        self.security_importer = SecurityImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse(self.server_path)

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

        # A channel that names a security definition can only resolve it once the definitions exist,
        # which is the order the importer itself runs the two sections in
        security_list = self.yaml_config['security']
        _ = self.security_importer.sync_security_definitions(security_list, self.session)

# ################################################################################################################################

    def test_channel_mllp_creation(self) -> 'None':
        """ Test the creation of HL7 MLLP channels.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_mllp']

        channel_def_count = len(channel_defs)
        self.assertTrue(channel_def_count > 0, 'No HL7 MLLP channel definitions found in YAML')

        channels_created, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        # Every channel the template declares should be created
        created_count = len(channels_created)
        self.assertEqual(created_count, channel_def_count, 'Not all HL7 MLLP channels were created')

        for channel in channels_created:
            self.assertTrue(channel.name.startswith('enmasse.hl7.mllp.'))
            self.assertEqual(channel.type_, 'channel-hl7-mllp')
            self.assertTrue(channel.is_channel)
            self.assertFalse(channel.is_outconn)

# ################################################################################################################################

    def test_channel_mllp_opaque_fields(self) -> 'None':
        """ Verify opaque fields roundtrip - routing, tolerance, and dedup fields.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_mllp']
        channels_created, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        # Build a lookup by name
        channels_by_name = {}
        for channel in channels_created:
            channels_by_name[channel.name] = channel

        # Channel 1 - should_validate and msh9_message_type
        channel_1 = channels_by_name['enmasse.hl7.mllp.1']
        opaque_1 = json.loads(channel_1.opaque1)
        self.assertEqual(opaque_1['msh9_message_type'], 'ORU')
        self.assertTrue(opaque_1['should_validate'])

        # Channel 2 - fix_off_by_one_field_index and dedup
        channel_2 = channels_by_name['enmasse.hl7.mllp.2']
        opaque_2 = json.loads(channel_2.opaque1)
        self.assertEqual(opaque_2['msh9_message_type'], 'ADT')
        self.assertEqual(opaque_2['msh9_trigger_event'], 'A01')
        self.assertTrue(opaque_2['fix_off_by_one_field_index'])
        self.assertEqual(opaque_2['dedup_ttl_value'], 30)
        self.assertEqual(opaque_2['dedup_ttl_unit'], 'minutes')

        # Channel 3 - overridden tolerance defaults
        channel_3 = channels_by_name['enmasse.hl7.mllp.3']
        opaque_3 = json.loads(channel_3.opaque1)
        self.assertTrue(opaque_3['is_default'])
        self.assertFalse(opaque_3['normalize_obx2_value_type'])
        self.assertFalse(opaque_3['allow_short_encoding_characters'])

# ################################################################################################################################

    def test_channel_mllp_idempotent_update(self) -> 'None':
        """ Run sync twice, assert second run produces 0 creates and updates with no data drift.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_mllp']

        # First sync - all channels should be created
        channels_created, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        channel_def_count = len(channel_defs)

        created_count = len(channels_created)
        self.assertEqual(created_count, channel_def_count)

        # Second sync - no new creates, only updates
        channels_created_2, channels_updated_2 = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        created_count_2 = len(channels_created_2)
        updated_count_2 = len(channels_updated_2)
        self.assertEqual(created_count_2, 0)
        self.assertEqual(updated_count_2, channel_def_count)

# ################################################################################################################################

    def test_channel_mllp_defaults(self) -> 'None':
        """ Verify that channels created without explicit tolerance flags get the library defaults.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_mllp']
        channels_created, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        # Channel 1 does not override tolerance flags - check that defaults apply
        channels_by_name = {}
        for channel in channels_created:
            channels_by_name[channel.name] = channel

        channel_1 = channels_by_name['enmasse.hl7.mllp.1']
        opaque_1 = json.loads(channel_1.opaque1)

        # These should have their default True values
        self.assertTrue(opaque_1['normalize_line_endings'])
        self.assertTrue(opaque_1['force_standard_delimiters'])
        self.assertTrue(opaque_1['restore_truncated_msh'])
        self.assertTrue(opaque_1['split_concatenated_messages'])
        self.assertTrue(opaque_1['use_msh18_encoding'])
        self.assertTrue(opaque_1['normalize_obx2_value_type'])
        self.assertTrue(opaque_1['replace_invalid_obx2_value_type'])
        self.assertTrue(opaque_1['normalize_invalid_escape_sequences'])
        self.assertTrue(opaque_1['normalize_obx8_abnormal_flags'])
        self.assertTrue(opaque_1['normalize_quadruple_quoted_empty'])
        self.assertTrue(opaque_1['allow_short_encoding_characters'])

        # fix_off_by_one_field_index defaults to False
        self.assertFalse(opaque_1['fix_off_by_one_field_index'])

# ################################################################################################################################

    def test_channel_mllp_is_active_honoured_on_update(self) -> 'None':
        """ A channel the YAML marks as inactive stays inactive when the same YAML is synced again.
        """
        self._setup_test_environment()

        channel_defs = [{
            'name': 'enmasse.hl7.mllp.inactive',
            'service': 'enmasse.hl7.test.service',
            'is_active': False,
        }]

        channels_created, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)
        self.assertFalse(channels_created[0].is_active)

        # The second sync goes down the update path, which is where the flag used to be dropped
        _, channels_updated = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)
        self.assertFalse(channels_updated[0].is_active)

# ################################################################################################################################

    def test_channel_mllp_stores_the_destination_list_as_text(self) -> 'None':
        """ A file writes a channel's destinations as a list of its own, while what a channel
        stores is the JSON text the Dashboard writes - one stored form for both.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_mllp']
        channels_created, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        channels_by_name = {}
        for channel in channels_created:
            channels_by_name[channel.name] = channel

        opaque = json.loads(channels_by_name['enmasse.hl7.mllp.3'].opaque1)

        destinations = json.loads(opaque['destinations'])
        self.assertEqual(len(destinations), 2)

        self.assertEqual(destinations[0]['connection'], 'enmasse.outgoing.rest.1')
        self.assertEqual(destinations[0]['type'], 'rest')
        self.assertTrue(destinations[0]['is_active'])
        self.assertEqual(destinations[0]['options']['method'], 'POST')

        # A destination that receives nothing is stored all the same, its options with it
        self.assertFalse(destinations[1]['is_active'])
        self.assertEqual(destinations[1]['options']['to'], 'ops@example.com')

        self.assertEqual(opaque['respond_from'], 'enmasse.outgoing.rest.1')
        self.assertEqual(opaque['delivery_mode'], 'in-order')

# ################################################################################################################################

    def test_channel_mllp_delivers_without_a_service(self) -> 'None':
        """ A channel that hands each message to its destinations alone needs no service, and
        what it never said stays at its default.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_mllp']
        channels_created, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        channels_by_name = {}
        for channel in channels_created:
            channels_by_name[channel.name] = channel

        opaque = json.loads(channels_by_name['enmasse.hl7.mllp.4'].opaque1)

        self.assertEqual(opaque['service'], '')
        self.assertEqual(opaque['respond_from'], 'service')
        self.assertEqual(opaque['delivery_mode'], 'same-time')

        destinations = json.loads(opaque['destinations'])
        self.assertEqual(len(destinations), 1)

        # A destination the file says nothing else about receives messages and is addressed
        # by the connection it delivers through
        self.assertTrue(destinations[0]['is_active'])
        self.assertEqual(destinations[0]['name'], 'enmasse.outgoing.rest.2')

# ################################################################################################################################

    def test_channel_mllp_rejects_an_unusable_destination_list(self) -> 'None':
        """ A destination list that could not be delivered to is refused before it is stored.
        """
        self._setup_test_environment()

        # A reply from a destination the channel does not have
        channel_defs = [{
            'name': 'enmasse.hl7.mllp.bad.reply',
            'destinations': [{'type': 'rest', 'connection': 'enmasse.outgoing.rest.1'}],
            'respond_from': 'enmasse.no.such.destination',
        }]

        with self.assertRaises(Exception):
            _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        # A destination of a type nothing can deliver through
        channel_defs = [{
            'name': 'enmasse.hl7.mllp.bad.type',
            'destinations': [{'type': 'carrier-pigeon', 'connection': 'enmasse.outgoing.rest.1'}],
        }]

        with self.assertRaises(Exception):
            _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        # A delivery mode that does not exist, the reserved one included
        channel_defs = [{
            'name': 'enmasse.hl7.mllp.bad.mode',
            'destinations': [{'type': 'rest', 'connection': 'enmasse.outgoing.rest.1'}],
            'delivery_mode': 'service-decides',
        }]

        with self.assertRaises(Exception):
            _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

# ################################################################################################################################

    def test_channel_mllp_needs_somewhere_to_deliver(self) -> 'None':
        """ A channel that names neither a service nor a destination is rejected.
        """
        self._setup_test_environment()

        channel_defs = [{
            'name': 'enmasse.hl7.mllp.no.delivery',
        }]

        with self.assertRaises(Exception):
            _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

# ################################################################################################################################

    def test_channel_mllp_security_name_resolves_to_id(self) -> 'None':
        """ The security definition a channel names is stored as that definition's id, and the name
        it was given by never reaches the channel's own fields.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_mllp']
        channels_created, _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

        channels_by_name = {}
        for channel in channels_created:
            channels_by_name[channel.name] = channel

        expected_id = self.importer.sec_defs['enmasse.mtls.2']['id']

        # The first channel names the definition ..
        channel_1 = channels_by_name['enmasse.hl7.mllp.1']
        opaque_1 = json.loads(channel_1.opaque1)
        self.assertEqual(opaque_1['security_id'], expected_id)
        self.assertNotIn('security', opaque_1)

        # .. and the second names none, so it accepts a sender whatever certificate it presented.
        channel_2 = channels_by_name['enmasse.hl7.mllp.2']
        opaque_2 = json.loads(channel_2.opaque1)
        self.assertEqual(opaque_2['security_id'], 0)

# ################################################################################################################################

    def test_channel_mllp_unknown_security_is_rejected(self) -> 'None':
        """ A channel naming a security definition that does not exist is rejected rather than
        created without one, which would leave it accepting every sender.
        """
        self._setup_test_environment()

        channel_defs = [{
            'name': 'enmasse.hl7.mllp.unknown.security',
            'service': 'demo.ping',
            'security': 'enmasse.no.such.definition',
        }]

        with self.assertRaises(Exception):
            _ = self.channel_mllp_importer.sync_definitions(channel_defs, self.session)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
