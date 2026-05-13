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
from zato.cli.enmasse.importers.channel_hl7_mllp import ChannelHL7MLLPImporter
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

class TestEnmasseChannelHL7MLLPImporter(TestCase):
    """ Tests importing HL7 MLLP channels.
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

        # Initialize the HL7 MLLP channel importer
        self.channel_hl7_mllp_importer = ChannelHL7MLLPImporter(self.importer)

        self.yaml_config = cast_('stranydict', None)
        self.session = cast_('any_', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            self.session.close()
        os.unlink(self.temp_file.name)
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        """ Set up the test environment by opening a database session and parsing the YAML file.
        """
        if not self.session:
            self.session = get_session_from_server_dir(self.server_path)

        if not self.yaml_config:
            self.yaml_config = self.importer.from_path(self.temp_file.name)

# ################################################################################################################################

    def test_channel_hl7_mllp_creation(self) -> 'None':
        """ Test the creation of HL7 MLLP channels.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_hl7_mllp']

        channel_def_count = len(channel_defs)
        self.assertTrue(channel_def_count > 0, 'No HL7 MLLP channel definitions found in YAML')

        channels_created, _ = self.channel_hl7_mllp_importer.sync_definitions(channel_defs, self.session)

        # All three channels from the template should be created
        created_count = len(channels_created)
        self.assertEqual(created_count, channel_def_count, 'Not all HL7 MLLP channels were created')

        for channel in channels_created:
            self.assertTrue(channel.name.startswith('enmasse.hl7.mllp.'))
            self.assertEqual(channel.type_, 'channel-hl7-mllp')
            self.assertTrue(channel.is_channel)
            self.assertFalse(channel.is_outconn)

# ################################################################################################################################

    def test_channel_hl7_mllp_opaque_fields(self) -> 'None':
        """ Verify opaque fields roundtrip - routing, tolerance, and dedup fields.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_hl7_mllp']
        channels_created, _ = self.channel_hl7_mllp_importer.sync_definitions(channel_defs, self.session)

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

    def test_channel_hl7_mllp_idempotent_update(self) -> 'None':
        """ Run sync twice, assert second run produces 0 creates and updates with no data drift.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_hl7_mllp']

        # First sync - all channels should be created
        channels_created, _ = self.channel_hl7_mllp_importer.sync_definitions(channel_defs, self.session)

        created_count = len(channels_created)
        self.assertEqual(created_count, 3)

        # Second sync - no new creates, only updates
        channels_created_2, channels_updated_2 = self.channel_hl7_mllp_importer.sync_definitions(channel_defs, self.session)

        created_count_2 = len(channels_created_2)
        updated_count_2 = len(channels_updated_2)
        self.assertEqual(created_count_2, 0)
        self.assertEqual(updated_count_2, 3)

# ################################################################################################################################

    def test_channel_hl7_mllp_defaults(self) -> 'None':
        """ Verify that channels created without explicit tolerance flags get the library defaults.
        """
        self._setup_test_environment()

        channel_defs = self.yaml_config['channel_hl7_mllp']
        channels_created, _ = self.channel_hl7_mllp_importer.sync_definitions(channel_defs, self.session)

        # Channel 1 does not override tolerance flags - check that defaults apply
        channels_by_name = {}
        for channel in channels_created:
            channels_by_name[channel.name] = channel

        channel_1 = channels_by_name['enmasse.hl7.mllp.1']
        opaque_1 = json.loads(channel_1.opaque1)

        # These should have their default True values
        self.assertTrue(opaque_1['normalize_line_endings'])
        self.assertTrue(opaque_1['force_standard_delimiters'])
        self.assertTrue(opaque_1['repair_truncated_msh'])
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
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
